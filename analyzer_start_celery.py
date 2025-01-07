# stdlib
import logging

# thirdparty
from celery.schedules import crontab

# project
from analyzer_tasks_header import app
from settings import get_settings

settings = get_settings()

app.conf.beat_schedule = {
    "reward_clans": {
        "task": "analyzer_recurrent_tasks",  # noqa
        "schedule": crontab(),  # noqa
    },
}

app.conf.timezone = "UTC"
app.conf.task_acks_late = True
app.conf.beat_enabled = True


if __name__ == "__main__":
    app.control.purge()

    worker = app.Worker(
        include=[],
        queue="tasks",
        pool="prefork",
        beat=True,
        without_gossip=True,
    )

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    worker.start()
