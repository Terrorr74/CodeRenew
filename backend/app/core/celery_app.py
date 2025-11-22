"""
Celery configuration for background task processing
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "coderenew",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.scan_tasks", "app.tasks.epss_tasks", "app.tasks.webhook_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max
    task_soft_time_limit=1500,  # 25 minutes soft limit
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # Results expire after 24 hours
    broker_connection_retry_on_startup=True,
)

# Retry configuration
celery_app.conf.task_annotations = {
    "app.tasks.scan_tasks.run_wordpress_scan": {
        "max_retries": 3,
        "default_retry_delay": 60,
    }
}
