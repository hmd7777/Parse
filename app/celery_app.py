import os
from celery import Celery


def make_celery() -> Celery:
  broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
  backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)

  app = Celery(
    "parse_app",
    broker=broker_url,
    backend=backend_url,
    include=["app.tasks.files"],
  )

  app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
  )

  return app


celery_app = make_celery()

