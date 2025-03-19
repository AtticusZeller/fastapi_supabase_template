from celery import Celery

from app.core.config import settings

# Configuration de l'application Celery
celery_app = Celery(
    "app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configuration depuis settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 heure max par tâche
    worker_hijack_root_logger=False,
)

# Configuration spécifique à l'environnement
if settings.ENVIRONMENT == "local":
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True

# Découverte automatique des tâches
celery_app.autodiscover_tasks(["app.tasks"], force=True)
