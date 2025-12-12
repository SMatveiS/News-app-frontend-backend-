from fastapi import Depends, HTTPException
from app.auth.utils import get_current_user

def admin_required(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user

def verified_author_required(current_user=Depends(get_current_user)):
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="Not verified author")
    return current_user
