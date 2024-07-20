from django.conf import settings
from celery import Celery


def create_app(project_name: str, settings_path: str = "django.config:settings") -> Celery:
    app: Celery = Celery(project_name, backend=settings.CELERY_BROKER_URL)
    app.config_from_object(settings_path, namespace='CELERY')
    app.autodiscover_tasks()
    return app
