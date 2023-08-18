import os
from redis import Redis
from celery import Celery, group, chain
from json import dumps
from youtube import YouTube
from youtube.models import (
    Video, Channel, Playlist, PlaylistItem, VideoCommentThread, Comment, CommentAuthor
)
from json import loads, dumps
from typing import Iterator
import requests
from ..config import config


celery = Celery(__name__)
celery.conf.broker_url = config.celery_broker_url
celery.conf.result_backend = config.celery_result_backend

redis = Redis(host=config.redis_host)
client_secret_file = config.client_secret_file
credentials_dir = config.credentials_dir
youtube = YouTube()
youtube.authenticate(clients_secret_file=client_secret_file, credentials_directory=credentials_dir)


def get_video_by_id(video_id: str) -> Video:
    """Get a YouTube Video by its id."""
    video = youtube.find_video_by_id(video_id)
    if video:
        return video[0]
    return None

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

def get_channel_playlists(channel_id: str) -> list[Playlist]:
    playlists = youtube.find_channel_playlists(channel_id)
    return playlists

def get_playlist_videos(playlist_id: str) -> list[Video]:
    playlist_items: list[PlaylistItem] = list(next(youtube.find_playlist_items(playlist_id)))
    video_ids: list[str] = [item.video_id for item in playlist_items]
    videos = []
    for video_id in video_ids:
        video = get_video_by_id(video_id)
        if video:
            videos.append(video)
    return videos


def post_data(data: dict, url: str):
    admin_token = ''
    headers = {'Authorization': f'Bearer {admin_token}'}
    resp = requests.post(url, json=data, headers=headers)
    return resp


def get_video_comments(video_id: str):
    search_iterator: Iterator = youtube.find_video_comments(video_id)
    video_comment_threads: list[VideoCommentThread] = list(next(search_iterator))
    authors: list[dict[str, str]] = []
    comments: list[dict[str, str]] = []
    for video_comment_thread in video_comment_threads:
        comment: Comment = video_comment_thread.top_level_comment.comment
        author: CommentAuthor = video_comment_thread.top_level_comment.comment.comment_author
        authors.append(author.to_dict())
        comment.comment_author = author.to_dict()
        video_comment: dict[str, str] = comment.to_dict()
        comments.append(video_comment)
    return comments

@celery.task(name="load_channel")
def load_channel(channel_id: str):
    channel = get_channel_from_video(channel_id)
    redis.publish('channels', dumps(channel.to_dict()))
    return channel.to_dict()

@celery.task(name="load_video")
def load_video(video_id: str):
    video = get_video_by_id(video_id)
    redis.publish('videos', dumps(video.to_dict()))
    return video.to_dict()

@celery.task(name="load_channel_playlists")
def load_channel_playlists(channel_id: str):
    playlists = get_channel_playlists(channel_id)
    for playlist in playlists:
        redis.publish('playlists', dumps(playlist.to_dict()))
        
    return {'Playlists': [playlist.to_dict() for playlist in playlists]}


@celery.task(name="load_playlist_videos")
def load_playlist_videos(playlist_id: str):
    videos = get_playlist_videos(playlist_id)
    for video in videos:
        redis.publish('videos', dumps(video.to_dict()))
        
    return {'Videos': [video.to_dict() for video in videos]}


@celery.task(name="load_video_comments")
def load_video_comments(video_id: str):
    comments = get_video_comments(video_id)
    for comment in comments:
        redis.publish('comments', dumps(comment))
        
    return {'Comments': comments}

