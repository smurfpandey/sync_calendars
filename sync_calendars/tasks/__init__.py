"""Initialize tasks engine"""

def init_celery_app(celery, app):
    """Function to create new Celery object to use with Flask app"""
    # celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
    #                 broker=app.config['CELERY_BROKER_URL'],
    #                 include=['calendar_tasks'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        """Task subclass that wraps the task execution in an application context"""
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
