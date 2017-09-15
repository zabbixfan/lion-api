from app import create_app,celery
app = create_app()
app.app_context().push()

#celery -B -A task_worker.celery worker -l info