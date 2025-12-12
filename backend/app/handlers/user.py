from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models.user import User
from app.models.user import UserResponse, UserCreate
from app.auth.utils import get_current_user, get_password_hash
from app.auth.dependencies import admin_required

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    result = db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user.password = get_password_hash(user.password)
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.execute(select(User).filter(User.id == user_id)).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, 
    user_update: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_user = db.execute(select(User).filter(User.id == user_id)).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Проверяем, не занят ли email другим пользователем
    if user_update.email != db_user.email:
        existing_user = db.execute(select(User).filter(User.email == user_update.email)).scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400,detail="Email already registered by another user")

    # Обновляем данные
    db_user.name = user_update.name
    db_user.email = user_update.email
    db_user.is_verified = user_update.is_verified
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)
    
    
    if user_update.avatar:
        db_user.avatar = user_update.avatar 

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_user = db.execute(select(User).filter(User.id == user_id)).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}
