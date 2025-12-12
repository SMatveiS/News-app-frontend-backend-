from celery import Task
from app.celery_app import celery_app
from app.database.database import SessionLocal
from app.database.models.user import User
from app.database.models.news import News
from app.database.models.comment import Comment
from datetime import datetime, timedelta
import logging
import os
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# Папка для логов уведомлений
BASE_DIR = Path(__file__).resolve().parent.parent 

NOTIFICATIONS_LOG_DIR = BASE_DIR / "logs" / "notifications"

# Проверка, что папка для логов существует
def check_log_directory():
    try:
        NOTIFICATIONS_LOG_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Log directory ensured: {NOTIFICATIONS_LOG_DIR}")
    except Exception as e:
        logger.error(f"Failed to create log directory: {e}")
        raise

check_log_directory()

# Класс идемпотентных задач, чтобы уведомления не приходили дважды при различных ошибках
class IdempotentTask(Task):
    
    def apply_async(
            self,
            args=None,
            kwargs=None,
            task_id=None,
            **options
        ):
        # Генерация уникального task_id
        if task_id is None and kwargs:
            # Используем параметры задачи для генерации уникального ID
            task_id = f"{self.name}:{hash(json.dumps(kwargs, sort_keys=True))}"
        return super().apply_async(args, kwargs, task_id=task_id, **options)

def log_notification(
        notification_type: str, 
        recipients: list,
        content: dict,
    ):

    check_log_directory()

    timestamp = datetime.utcnow().isoformat()
    log_file = NOTIFICATIONS_LOG_DIR / f"{notification_type}_{datetime.utcnow().strftime('%Y%m%d')}.log"
    
    log_entry = {
        "timestamp": timestamp,
        "type": notification_type,
        "recipients": recipients,
        "content": content,
        "status": "sent"
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    logger.info(f"{notification_type} sent to {len(recipients)} users")
    for email in recipients:
        logger.info(f"   to {email}")

@celery_app.task(
    bind=True,
    base=IdempotentTask,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3
)
def send_new_news_notification(
    self,
    news_id: int,
    news_title: str,
    author_name: str,
):
    try:
        logger.info(f"Processing new news notification: {news_id}")
        
        db = SessionLocal()
        try:
            users = db.query(User).all()
            
            if not users:
                logger.warning("No users found to notify")
                return
            
            recipients = [user.email for user in users]
            
            content = {
                "subject": f"Новая новость: {news_title}",
                "body": f"Пользователь {author_name} опубликовал новую новость: '{news_title}'.\n\n"
                        f"Перейти к новости: http://localhost:8000/news/{news_id}",
                "news_id": news_id
            }
            
            log_notification("new_news", recipients, content)
            
            logger.info(f"New news notification sent successfully for news_id={news_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error sending new news notification: {e}")
        raise self.retry(exc=e)

@celery_app.task(
    bind=True,
    base=IdempotentTask,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3
)
def send_weekly_digest(self):
    try:
        logger.info("Processing weekly digest")
        
        db = SessionLocal()
        try:
            # Получить новости за последние 7 дней
            week_ago = datetime.utcnow() - timedelta(days=7)
            news_list = db.query(News).filter(
                News.publication_date >= week_ago
            ).order_by(News.publication_date.desc()).all()
            
            if not news_list:
                logger.info("No news published this week")
                return
            
            users = db.query(User).all()
            
            if not users:
                logger.warning("No users found to send digest")
                return
            
            recipients = [user.email for user in users]
            
            news_summary = "\n".join([
                f"- {news.title} (автор: {news.author.name}, {news.publication_date.strftime('%d.%m.%Y')})"
                for news in news_list
            ])
            
            content = {
                "subject": f"Еженедельный дайджест новостей ({len(news_list)} новостей)",
                "body": f"За последнюю неделю было опубликовано {len(news_list)} новостей:\n\n{news_summary}\n\n"
                        f"Читать все новости: http://localhost:8000/news",
                "news_count": len(news_list)
            }
            
            log_notification("weekly_digest", recipients, content)
            
            logger.info(f"Weekly digest sent successfully ({len(news_list)} news, {len(recipients)} recipients)")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error sending weekly digest: {e}")
        raise self.retry(exc=e)



from celery.signals import worker_shutdown

@worker_shutdown.connect
def worker_shutdown_handler(sender, **kwargs):
    logger.info("Celery worker shutting down gracefully...")
