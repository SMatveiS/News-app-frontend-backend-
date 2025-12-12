from fastapi import Depends, HTTPException
from app.auth.utils import get_current_user
from app.database.models.news import News
from app.database.models.comment import Comment
from sqlalchemy.orm import Session
from app.database.database import get_db

def admin_required(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

def verified_author_required(current_user=Depends(get_current_user)):
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="You must be a verified author.")
    return current_user

def comment_owner_or_admin(
    comment_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user),
):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not (current_user.is_admin or db_comment.author_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough rights")
    return db_comment

def news_owner_or_admin(
    news_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user),
):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    if not (current_user.is_admin or db_news.author_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough rights")
    return db_news
