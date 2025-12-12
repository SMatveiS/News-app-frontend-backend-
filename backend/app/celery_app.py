from celery import Celery
from celery.schedules import crontab
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Инициализация Celery
celery_app = Celery(
    "news_api",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Ретраи и backoff
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    worker_pool_restarts=True,
)

# Периодические задачи
celery_app.conf.beat_schedule = {
    "weekly-digest": {
        "task": "app.tasks.send_weekly_digest",
        "schedule": crontab(day_of_week="sunday", hour=9, minute=0),  # Каждое воскресенье в 9:00
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")
