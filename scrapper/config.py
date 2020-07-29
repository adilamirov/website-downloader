import os
from pathlib import Path

ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = ENV == 'development'
SECRET_KEY = os.getenv('SECRET_KEY', '123')

MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
MONGODB_DATABASE = os.getenv('MONGODB_DB', 'scrapper')

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND_URL', 'redis://localhost:6379/0')

UPLOAD_DIR = Path(__file__).parent.parent / 'upload'
