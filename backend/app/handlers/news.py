from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database.database import get_db
from app.database.redis_client import redis_client
from app.models.news import NewsResponse, NewsCreate
from app.database.models.news import News
from app.auth.utils import get_current_user
from app.auth.dependencies import news_owner_or_admin, verified_author_required
from app.config import settings
from app.tasks import send_new_news_notification


router = APIRouter(prefix="/news", tags=["news"])
logger = logging.getLogger(__name__)

def get_news_cache_key(news_id: int) -> str:
    return f"news:{news_id}"


@router.post("/", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news(
    news: NewsCreate, 
    db: Session = Depends(get_db),
    current_user=Depends(verified_author_required),
):
    new_news = News(
        title=news.title,
        content=news.content,
        cover=news.cover,
        author_id=current_user.id
    )
    # Добавляем в бд
    db.add(new_news)
    db.commit()
    db.refresh(new_news)

    # Добавляем в кэш
    cache_key = get_news_cache_key(new_news.id)
    news_dict = {
        "id": new_news.id,
        "title": new_news.title,
        "content": new_news.content,
        "cover": new_news.cover,
        "author_id": new_news.author_id,
        "publication_date": new_news.publication_date.isoformat(),
        "author": {
            "id": current_user.id,
            "name": current_user.name
        }
    }
    redis_client.set(cache_key, news_dict, settings.news_cache_ttl)

    # Отправить уведомление о новой новости
    send_new_news_notification.apply_async(
        kwargs={
            "news_id": new_news.id,
            "news_title": new_news.title,
            "author_name": current_user.name
        }
    )
    logger.info(f"Queued notification task for news {new_news.id}")
    

    return new_news


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int, 
    db: Session = Depends(get_db),
):
    cache_key = get_news_cache_key(news_id)
    
    # Попытка получить из кэша
    cached_news = redis_client.get(cache_key)
    if cached_news:
        logger.info(f"📰 Returning news {news_id} from CACHE")
        return NewsResponse(**cached_news)
    
    # Если нет в кэше — берём из БД
    logger.info(f"🗄️  Fetching news {news_id} from DATABASE")
    news = db.execute(select(News).filter(News.id == news_id)).scalar_one_or_none()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Добавляем в кэш
    news_dict = {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "cover": news.cover,
        "author_id": news.author_id,
        "publication_date": news.publication_date.isoformat(),
        "author": {
            "id": news.author.id,
            "name": news.author.name
        } if news.author else None 
    }
    redis_client.set(cache_key, news_dict, settings.news_cache_ttl)

    return news


@router.put("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: int, 
    news: NewsCreate, 
    db_news: News = Depends(news_owner_or_admin),
    db: Session = Depends(get_db),
):
    db_news.title = news.title
    db_news.content = news.content
    db_news.cover = news.cover

    # Обновляем бд
    db.commit()
    db.refresh(db_news)

    # Обновляем кэш
    cache_key = get_news_cache_key(news_id)
    redis_client.delete(cache_key)
    logger.info(f"🔄 News {news_id} updated, cache invalidated")

    return db_news


@router.delete("/{news_id}")
def delete_news(
    news_id: int, 
    db_news: News = Depends(news_owner_or_admin),
    db: Session = Depends(get_db),
):
    # Обновляем бд
    db.delete(db_news)
    db.commit()

    # Обновляем кэш
    cache_key = get_news_cache_key(news_id)
    redis_client.delete(cache_key)
    logger.info(f"🗑️  News {news_id} deleted, cache invalidated")

    return {"message": "News deleted successfully"}

@router.get("/", response_model=List[NewsResponse])
def get_all_news(db: Session = Depends(get_db)):
    news = db.query(News).order_by(News.publication_date.desc()).all()
    return news

