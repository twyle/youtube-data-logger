import os
from redis import Redis
from celery import Celery
from json import dumps
from youtube import YouTube
from youtube.models import (
    Video, Channel
)


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

redis = Redis()

youtube = YouTube(client_secret_file='/home/lyle/Downloads/client_secret.json')
youtube.authenticate()


def get_video_by_id(video_id: str) -> Video:
    """Get a YouTube Video by its id."""
    video = youtube.find_video_by_id(video_id)
    return video[0]

def get_channel_id_title(video: Video) -> dict[str, str]:
    """Get channel id and title from video."""
    return {video.video_title:video.channel_id}

def get_channel_id(video: Video) -> str:
    """Get channel id from video."""
    return video.channel_id

def get_channel_from_id(channel_id: str) -> Channel:
    channel = youtube.find_channel_by_id(channel_id)
    return channel

def get_channel_from_video(video_id: str) -> Channel:
    video = get_video_by_id(video_id)
    channel_id = get_channel_id(video)
    channel = get_channel_from_id(channel_id)
    return channel[0]

@celery.task(name="load_channel")
def load_channel(channel_id: str):
    if redis.get(channel_id):
        channel = redis.get(channel_id)
        redis.publish('channels', channel)
        return channel
    else:
        channel = get_channel_from_video(channel_id)
        redis.set(channel_id, channel.to_json())
        redis.publish('channels', dumps(channel.to_dict()))
        return channel.to_dict()

@celery.task(name="load_video")
def load_video(video_id: str):
    video = get_video_by_id(video_id)
    redis.publish('videos', dumps(video.to_dict()))
    return video.to_dict()