from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, DateTime, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[JSON] = mapped_column(JSON)
    publication_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    cover: Mapped[Optional[str]] = mapped_column(String(200))

    author = relationship("User", back_populates="news")
    comments = relationship("Comment", back_populates="news", cascade="all, delete-orphan")