from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database.database import get_db
from app.database.models.comment import Comment
from app.database.models.news import News
from app.database.models.user import User
from app.models.comment import CommentResponse, CommentCreate
from app.auth.utils import get_current_user
from app.auth.dependencies import comment_owner_or_admin


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    news = db.execute(select(News).filter(News.id == comment.news_id)).scalar_one_or_none()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    new_comment = Comment(
        news_id=comment.news_id,
        text=comment.text,
        author_id=current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: int, 
    db: Session = Depends(get_db),
):
    comment = db.execute(select(Comment).filter(Comment.id == comment_id)).scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int, 
    comment: CommentCreate,
    db_comment: Comment = Depends(comment_owner_or_admin),
    db: Session = Depends(get_db),
):
    db_comment.text = comment.text

    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db_comment: Comment = Depends(comment_owner_or_admin),
    db: Session = Depends(get_db),
):
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

@router.get("/", response_model=List[CommentResponse])
def get_comments(
    news_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    if news_id:
        comments = db.query(Comment).filter(Comment.news_id == news_id).all()
    else:
        comments = db.query(Comment).all()
    return comments
