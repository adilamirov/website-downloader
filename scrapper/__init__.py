from flask import Flask
from flask_mongoengine import MongoEngine

from .views import TasksAPI
from .extensions import celery

db = MongoEngine()


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('scrapper.config')
    db.init_app(app)
    init_celery(app)
    register_views(app)
    init_upload_dir(app)
    return app


def init_celery(app=None):
    app = app or create_app()
    celery.conf.broker_url = app.config["CELERY_BROKER_URL"]
    celery.conf.result_backend = app.config["CELERY_RESULT_BACKEND"]
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def register_views(app: Flask):
    task_view = TasksAPI.as_view('tasks_api')
    app.add_url_rule('/tasks', view_func=task_view,
                     methods=['POST', ])
    app.add_url_rule('/tasks/<string:task_id>', view_func=task_view,
                     methods=['GET', 'PUT', 'DELETE'])


def init_upload_dir(app: Flask):
    app.config['UPLOAD_DIR'].mkdir(parents=True, exist_ok=True)
