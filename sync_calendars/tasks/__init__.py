"""Initialize tasks engine"""

def init_celery_app(celery, app):
    """Function to create new Celery object to use with Flask app"""

    # Disable all the invalid-name,too-few-public-methods violations in this function
    #

    celery.conf.update(app.config)
    TaskBase = celery.Task  # pylint: disable=invalid-name,

    class ContextTask(TaskBase):    #pylint: disable=too-few-public-methods
        """Task subclass that wraps the task execution in an application context"""
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
