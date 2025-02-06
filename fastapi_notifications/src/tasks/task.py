from time import sleep

from celery import Celery

from core.logger import log

celery = Celery(
    "tasks",
    backend="rpc://",
    broker="pyamqp://user:password@localhost//",
)

# console:
# celery -A tasks.task worker --loglevel=INFO

COUNTER = 0


@celery.task
def task_add(message: str, delay: int) -> None:
    log.info(f"Sleeping for {delay} sec...")

    global COUNTER
    count = COUNTER

    sleep(delay)

    with open("main.log", mode="a", encoding="utf-8") as fw:
        fw.write(message)
    log.info(f"Message from celery: '{message} {count}'")

    COUNTER += 1
    print(message)
    return None
