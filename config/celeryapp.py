#!/usr/bin/env python
import os

import celery

from django.conf import settings


# for handling redis with certificates: import ssl


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = celery.Celery(
    # ! KWARGS added here will usally be injected using the config.settings.base.celery module -> 'config_from_object'
    main="tasks",
    broker=settings.REDIS_URL,  # type: ignore[misc]
    backend=settings.REDIS_URL,  # type: ignore[misc]
    broker_use_ssl={
        # 'ssl_keyfile': settings.REDIS_KEY_FILE, 'ssl_certfile': settings.REDIS_CERT_FILE,
        # 'ssl_ca_certs': settings.REDIS_CA_FILE,
        # 'ssl_cert_reqs': ssl.CERT_NONE
    },
    redis_backend_use_ssl={
        # 'ssl_keyfile': settings.REDIS_KEY_FILE, 'ssl_certfile': settings.REDIS_CERT_FILE,
        # 'ssl_ca_certs': settings.REDIS_CA_FILE,
        # 'ssl_cert_reqs': ssl.CERT_NONE
    },
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# https://docs.celeryq.dev/en/latest/userguide/configuration.html
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
