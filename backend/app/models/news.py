from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class AuthorShort(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
        

class NewsBase(BaseModel):
    title: str
    content: Any
    cover: Optional[str] = None


class NewsCreate(NewsBase):
    pass


class NewsResponse(NewsBase):
    id: int
    author_id: int
    publication_date: datetime
    author: AuthorShort

    class Config:
        from_attributes = True