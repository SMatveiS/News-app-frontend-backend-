from datetime import datetime
from pydantic import BaseModel
from .news import AuthorShort


class CommentBase(BaseModel):
    news_id: int
    text: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    author_id: int
    publication_date: datetime
    author: AuthorShort

    class Config:
        from_attributes = True