from app import celery

@celery.task()
def add():
    return "haha"