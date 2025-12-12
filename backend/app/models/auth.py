from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    # Валидация логина
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not (3 <= len(v) <= 32):
            raise ValueError("Login must be between 3 and 32 characters")
        if not re.match(r"^[a-zA-Z0-9._-]+$", v):
            raise ValueError("Login must contain only latin letters, numbers, dots, underscores or dashes")
        return v

    # Валидация пароля
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str