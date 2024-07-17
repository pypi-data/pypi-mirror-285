from celery import Celery
from celery import Task
from celery.bin.celery import celery
from flask import Flask


def init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    app.cli.add_command(celery)
    app.shell_context_processor(
        lambda: {
            "celery": celery_app,
            **{task.__name__: task for task in celery_app.tasks.values() if not task.name.startswith("celery.")},
        }
    )

    return celery_app
