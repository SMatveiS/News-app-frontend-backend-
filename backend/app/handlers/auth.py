from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database.database import get_db
from app.database.models.user import User
from app.database.models.refresh_token import RefreshToken
from app.database.redis_client import redis_client
from app.auth.utils import (
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    get_current_user, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
    cache_user
)
from app.models.auth import RefreshRequest, RegisterRequest, LogoutRequest
from app.models.user import UserResponse
from fastapi_sso.sso.github import GithubSSO
import os
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

def get_session_key(refresh_token: str) -> str:
    return f"session:{refresh_token}"

def save_session(
    user_id: int,
    refresh_token: str,
    user_agent: str,
):
    session_key = get_session_key(refresh_token)
    session_data = {
        "user_id": user_id,
        "user_agent": user_agent,
        "created_at": str(datetime.utcnow())
    }
    ttl = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # в секундах
    redis_client.set(session_key, session_data, ttl)
    logger.info(f"🔑 Session saved for user {user_id} (TTL: {ttl}s)")

def get_session(refresh_token: str) -> dict:
    session_key = get_session_key(refresh_token)
    return redis_client.get(session_key)

def delete_session(refresh_token: str):
    session_key = get_session_key(refresh_token)
    redis_client.delete(session_key)

def get_user_sessions_keys(user_id: int) -> list:
    pattern = f"session:*"
    keys = redis_client.client.keys(pattern)
    user_sessions = []
    for key in keys:
        session_data = redis_client.get(key.replace("session:", ""))
        if session_data and session_data.get("user_id") == user_id:
            user_sessions.append(key.replace("session:", ""))
    return user_sessions

@router.post("/register", response_model=UserResponse)
def register_user(
    data: RegisterRequest, 
    db: Session = Depends(get_db),
):
    logger.info(f"Registering new user: email={data.email}, login={data.name}")

    # Проверка email
    if db.query(User).filter(User.email == data.email).first():
        logger.warning(f"Registration failed: Email {data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Проверка логина
    if db.query(User).filter(User.name == data.name).first():
        logger.warning(f"Registration failed: Login {data.name} already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this login already exists"
        )

    try:
        new_user = User(
            name=data.name,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            is_verified=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        cache_user(new_user)
        logger.info(f"User registered successfully: ID {new_user.id}")
        return new_user

    except Exception as e:
        logger.error(f"Registration DB error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login")
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    logger.info(f"Attempting login for user: {form_data.username}")

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: Invalid credentials for {form_data.username}")
        raise HTTPException(401, "Wrong email or password")

    access_token = create_access_token(user.id, user.is_admin, user.is_verified)
    refresh_token = create_refresh_token(user.id)

    logger.info(f"Login successful: User {user.id} ({user.email})")

    save_session(user.id, refresh_token, request.headers.get("User-Agent", ""))
    
    cache_user(user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": refresh_token
    }

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "FAKE_CLI")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "FAKE_SECRET")
GITHUB_REDIRECT_URL = os.getenv("GITHUB_REDIRECT_URL", "http://localhost:8000/auth/github/callback")

github_sso = GithubSSO(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    redirect_uri=GITHUB_REDIRECT_URL,
)

@router.get("/github/login")
async def github_login():
    async with github_sso:
        return await github_sso.get_login_redirect()

@router.get("/github/callback")
async def github_callback(
    request: Request, 
    db: Session = Depends(get_db),
):
    async with github_sso:
        user_sso = await github_sso.verify_and_process(request)
    
    user = db.query(User).filter_by(email=user_sso.email).first()
    if not user:
        user = User(
            name=user_sso.display_name or user_sso.email,
            email=user_sso.email,
            avatar=user_sso.picture,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(user.id, user.is_admin, user.is_verified)
    refresh_token = create_refresh_token(user.id)
    
    save_session(user.id, refresh_token, request.headers.get("User-Agent", ""))
    
    cache_user(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_access_token(
    data: RefreshRequest, 
    db: Session = Depends(get_db),
):
    session = get_session(data.refresh_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    payload = decode_token(data.refresh_token)
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    cache_user(user)
    
    return {
        "access_token": create_access_token(user.id, user.is_admin, user.is_verified),
        "refresh_token": data.refresh_token
    }


@router.get("/sessions")
def get_my_sessions(current_user: User = Depends(get_current_user),):
    session_tokens = get_user_sessions_keys(current_user.id)
    sessions = []
    for token in session_tokens:
        session_data = get_session(token)
        if session_data:
            sessions.append({
                "refresh_token": token[:20] + "...",  # Скрыть полный токен
                "user_agent": session_data.get("user_agent"),
                "created_at": session_data.get("created_at")
            })
    logger.info(f"👤 User {current_user.id} has {len(sessions)} active sessions")
    return sessions

@router.post("/logout")
def logout(data: LogoutRequest,):
    session = get_session(data.refresh_token)
    if not session:
        raise HTTPException(404, "Session not found")
    delete_session(data.refresh_token)
    logger.info(f"Session logged out")
    return {"ok": True}
