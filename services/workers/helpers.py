import os
from elasticsearch import Elasticsearch
from datetime import datetime
import requests
import time


def create_es_client(es_host: str, es_port: int):
    """Create the elasticsearch client."""
    es_client = Elasticsearch(hosts=[f'http://{es_host}:{es_port}'])
    return es_client


def index_resource(resource: dict[str, str|int|datetime], index: str, es_client: Elasticsearch, id: str):
    response = es_client.index(index=index, body=resource, id=id)
    print(response)
    
def get_channel_playlists(channel_id: str) -> None:
    resp = requests.post(url='http://web:8000/channel/playlists', params={'channel_id': channel_id})
    print(resp.status_code)
    print(resp.json())
    
def get_playlist_videos(playlist_id: str) -> None:
    resp = requests.post(url='http://web:8000/playlist/videos', params={'playlist_id': playlist_id})
    print(resp.status_code)
    print(resp.json())
    
def get_video_comments(video_id: str) -> None:
    resp = requests.post(url='http://web:8000/video/comments', params={'video_id': video_id})
    print(resp.status_code)
    print(resp.json())
    return resp.json()

def get_video_comments_task_result(task_id: str) -> dict:
    resp = requests.get(url='http://web:8000/video/task_status', params={'task_id': task_id})
    count: int = 0
    while resp.json()['task_status'] != 'SUCCESS' and count < 10:
        time.sleep(1)
        comments = resp.json()['task_result']['Comments']
        print(comments)
        return comments
    return []
    
    