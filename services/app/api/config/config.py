from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class BaseConfig(BaseSettings):
    celery_broker_url: str
    celery_result_backend: str
    client_secret_file: str
    credentials_dir: str
    redis_host: str
    
config = BaseConfig()