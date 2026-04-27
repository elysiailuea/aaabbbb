from celery import Celery
from backend.app.core.config import settings

celery_app = Celery(
    "honeypot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.beat_schedule = {
    "aggregate-and-alert-every-30s": {
        "task": "app.tasks.jobs.run_aggregation_and_alerts",
        "schedule": 30.0,
    },
    "cleanup-events-daily": {
        "task": "app.tasks.cleanup.cleanup_old_events",
        "schedule": 24 * 60 * 60.0,
        "args": (7,),
    },
}