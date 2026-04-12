from ..conf.extensions import celery


@celery.task(name="tasks.ping")
def ping_task():
    return {"status": "ok"}
