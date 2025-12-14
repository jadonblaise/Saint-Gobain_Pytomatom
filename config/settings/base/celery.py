from celery.schedules import crontab  # type: ignore[import]

from .internationalization import USE_TZ, TIME_ZONE

# All celery settings from https://docs.celeryq.dev/en/latest/userguide/configuration.html
# can be written here as UPPERCASE with a prefix "CELERY_".

# TBD: want to talk about 'New lowercase settings' from documentation.
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#conf-old-settings-map

# Celery
# -----------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE

# max one sub-process for a task to avoid filling up the queue.
worker_max_tasks_per_child = 1

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-time-limit
task_time_limit = 300
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_soft_time_limit

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
CELERY_TASK_TIME_LIMIT = 60 * 60  # 60 minutes
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
CELERY_TASK_SOFT_TIME_LIMIT = 60 * 10  # 10 minutes
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Results, using [django-celery-results](https://github.com/celery/django-celery-results)
CELERY_RESULT_BACKEND = "django-db"  # or: "django-cache" or "default" what is using the CACHES default backend


CELERY_BEAT_SCHEDULE: dict = {
    # "debugging-task": {
    #     "task": "apps.datalake.tasks.write_test_file",
    #     "schedule": crontab(minute="*/1"),  # <- every minute
    #     # "args": ["argument_to_commit_to_task"],
    #     # "schedule": crontab(minute=0, hour="*/1"),  # <- every hour
    #     # "schedule": crontab(minute="*/10"),  # <- every ten minutes
    #     # "schedule": crontab(minute=30, hour="*/1"),  # <- every hour at h:30
    #     # "schedule": crontab(minute=15, hour="*/2"),  # <- every two hours at h:15
    #     # "schedule": crontab(hour=22),  # <- everyday at 10pm
    # },
    # ! timezone is UTC
    # "rewrite-orders-porz-morning": {
    #     "task": "apps.sharepoint.tasks.write_ordermanagement",
    #     # "schedule": crontab(minute="*/1"),  # <- every minute
    #     "args": ["G035"],
    #     # "schedule": crontab(minute=0, hour="*/1"),  # <- every hour
    #     # "schedule": crontab(minute="*/10"),  # <- every ten minutes
    #     # "schedule": crontab(minute=30, hour="*/1"),  # <- every hour at h:30
    #     # "schedule": crontab(minute=15, hour="*/2"),  # <- every two hours at h:15
    #     "schedule": crontab(hour=str(5), minute=str(30)),  # <- everyday at 10pm
    # },
    # "rewrite-orders-porz-noon": {
    #     "task": "apps.sharepoint.tasks.write_ordermanagement",
    #     "args": ["G035"],
    #     "schedule": crontab(hour=str(13), minute=str(15)),
    # },
    # "rewrite-orders-porz-repetition-TEST": {
    #     "task": "apps.sharepoint.tasks.write_ordermanagement",
    #     "args": ["G035"],
    #     "schedule": crontab(minute="*/10"),
    # },
    "get-plannings-porz": {
        "task": "apps.sharepoint.tasks.get_porz_plannings",
        # "schedule": crontab(minute="*/1"),  # <- every minute
        # "args": ["argument_to_commit_to_task"],
        # "schedule": crontab(minute=0, hour="*/1"),  # <- every hour
        # "schedule": crontab(minute="*/10"),  # <- every ten minutes
        # "schedule": crontab(minute=30, hour="*/1"),  # <- every hour at h:30
        # "schedule": crontab(minute=15, hour="*/2"),  # <- every two hours at h:15
        # runs daily at 06:10 and 14:10 (UTC)
        "schedule": crontab(minute="10", hour="6,14"),
    },
}
CELERY_TASK_DEFAULT_QUEUE = "celery"
# define task routes here (not as args in the single tasks)
CELERY_ROUTES: dict = {
    "pytomatom.*": {"queue": "pytomatom"},
    "datalake.*": {"queue": "pytomatom"},
    "sharepoint.*": {"queue": "pytomatom"},
}
