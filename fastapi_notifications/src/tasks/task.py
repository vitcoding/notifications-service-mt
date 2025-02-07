from time import sleep

from celery import shared_task

from core.logger import log

COUNTER = 0


@shared_task()
def task_add(message: str, delay: int) -> None:
    log.info(f"Sleeping for {delay} sec...")

    global COUNTER
    count = COUNTER

    sleep(delay)

    celery_message = f"{message} - {count}\n"
    with open("main.log", mode="a", encoding="utf-8") as fw:
        fw.write(f"{celery_message}")
    log.info(f"Message from celery: '{celery_message}'")

    COUNTER += 1
    return None
