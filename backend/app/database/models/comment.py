from datetime import datetime

from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    publication_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="comments")
    author = relationship("User", back_populates="comments")