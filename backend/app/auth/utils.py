import jwt
from datetime import datetime, timedelta
from passlib.hash import argon2
from fastapi import HTTPException, status, Depends, Request
from app.database.models.user import User
from app.database.database import get_db
from app.database.redis_client import redis_client
import logging
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "my_super_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 21

def get_password_hash(password: str) -> str:
    return argon2.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return argon2.verify(password, hashed)

def create_access_token(
    user_id: int, 
    is_admin: bool = False, 
    is_verified: bool = False,
):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "admin": is_admin,
        "verified": is_verified,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    import uuid
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "jti": str(uuid.uuid4())},
        SECRET_KEY, algorithm=ALGORITHM
    )

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    user_id = int(payload["sub"])
    
    # Попытка получить из кэша
    cached_user = get_cached_user(user_id)
    if cached_user:
        logger.info(f"👤 User {user_id} loaded from CACHE")
        user = User(
            id=cached_user["id"],
            name=cached_user["name"],
            email=cached_user["email"],
            is_admin=cached_user["is_admin"],
            is_verified=cached_user["is_verified"],
            avatar=cached_user.get("avatar")
        )
        return user
    
    # Если нет в кэше — берём из бд
    logger.info(f"🗄️  User {user_id} loaded from DATABASE")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Добавляем в кэш
    cache_user(user)
    
    return user

def get_user_cache_key(user_id: int) -> str:
    return f"user:{user_id}"

def cache_user(user: User):
    cache_key = get_user_cache_key(user.id)
    # без hashed_password!
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified,
        "avatar": user.avatar,
    }
    redis_client.set(cache_key, user_data, ttl=600)

def get_cached_user(user_id: int) -> dict:
    cache_key = get_user_cache_key(user_id)
    return redis_client.get(cache_key)
