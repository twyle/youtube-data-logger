from api import create_app
from api.extensions.extensions import celery

app = create_app()