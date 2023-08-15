from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class BaseConfig(BaseSettings):
    celery_broker_url: str
    celery_result_backend: str
    secret_file: str
    
config = BaseConfig()