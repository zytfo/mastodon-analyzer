# thirdparty
from celery import Celery
from kombu import Exchange, Queue

# project
from settings import get_settings

settings = get_settings()

app = Celery(
    "analyzer_recurrent_tasks",
    broker=(
        f"amqp://"
        f"{settings.RABBITMQ_USER}:"
        f"{settings.RABBITMQ_PASSWORD}@"
        f"{settings.RABBITMQ_HOST}:"
        f"{settings.RABBITMQ_PORT}"
    ),
    backend="redis://:{password}@{host}:{port}/0".format(
        password=settings.REDIS_PASSWORD, host=settings.REDIS_HOST, port=settings.REDIS_PORT
    ),
    include=["analyzer_recurrent_tasks"],
)

app.conf.task_routes = (
    [
        ("analyzer_recurrent_tasks.*", {"queue": "tasks"}),
    ],
)

app.conf.worker_max_tasks_per_child = 1
app.conf.worker_concurrency = 1
app.conf.task_time_limit = 50000
app.conf.worker_max_memory_per_child = 1024 * 1024 * 512

app.conf.result_expires = 3600

app.conf.task_queues = (Queue("tasks", Exchange("tasks", type="topic"), routing_key="analyzer_recurrent_tasks.#"),)

app.conf.task_default_queue = "tasks"
