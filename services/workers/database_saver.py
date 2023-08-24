from database.crud import add_channel
from redis import Redis
from json import loads
from database.database import get_db, create_all
from database.models.channel import Channel
from datetime import datetime
import requests
import sys
import os
from dotenv import load_dotenv
from helpers import (
    create_es_client, index_resource, get_channel_playlists, get_playlist_videos,
    get_video_comments, get_video_comments_task_result
)
from elasticsearch import Elasticsearch

load_dotenv()

url_base = os.environ.get('URL_BASE', 'http://localhost:5000/api/v1/')
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis = Redis(host=redis_host)

es_host = os.environ['ES_HOST']
es_port = os.environ['ES_PORT']

es_client: Elasticsearch = create_es_client(es_host, es_port)
channels_index = os.environ['CHANNELS_INDEX']
playlists_index = os.environ['PLAYLISTS_INDEX']
videos_index = os.environ['VIDEOS_INDEX']

def add_channel_to_db():
    sub = redis.pubsub()
    sub.subscribe('channels')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            channel_data = loads(data['data'])
            channel_data['published_at'] = datetime.utcnow()
            channel = Channel(**channel_data)
            print(channel)
            channel = add_channel(session=get_db, channel=channel)
            
def post_data(data: dict, url: str):
    admin_token = ''
    headers = {'Authorization': f'Bearer {admin_token}'}
    resp = requests.post(url, json=data, headers=headers)
    return resp
            
def add_channel_to_api():
    url = f'{url_base}/channels/channel'
    sub = redis.pubsub()
    sub.subscribe('channels')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            channel_data = loads(data['data'])
            resp = index_resource(resource=channel_data, index=channels_index, es_client=es_client, id=channel_data['channel_id'])
            print(resp)
            channel_data['published_at'] = str(datetime.utcnow())
            resp = post_data(data=channel_data, url=url)
            if resp.ok:
                print(resp.json())
            else:
                print(resp.text)
            resp = get_channel_playlists(channel_id=channel_data['channel_id'])
        

                
def add_video_to_api():
    url = f'{url_base}/videos/video'
    sub = redis.pubsub()
    sub.subscribe('videos')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            video_data = loads(data['data'])
            resp = post_data(data=video_data, url=url)
            if resp.ok:
                print(resp.json())
            else:
                print(resp.text)
            resp = get_video_comments(video_id=video_data['video_id'])
            task_id: str = resp['task_id']
            comments = get_video_comments_task_result(task_id)
            video_data['comments'] = comments
            resp = index_resource(resource=video_data, index=videos_index, es_client=es_client, id=video_data['video_id'])
            print(resp)
                
def add_playlist_to_api():
    url = f'{url_base}/playlists/playlist'
    sub = redis.pubsub()
    sub.subscribe('playlists')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            playlist_data = loads(data['data'])
            resp = index_resource(resource=playlist_data, index=playlists_index, es_client=es_client, id=playlist_data['playlist_id'])
            print(resp)
            playlist_data['published_at'] = str(datetime.utcnow())
            resp = post_data(data=playlist_data, url=url)
            if resp.ok:
                print(resp.json())
            else:
                print(resp.text)
            #resp = get_playlist_videos(playlist_id=playlist_data['playlist_id'])
            
def add_comment_to_api():
    url = f'{url_base}/comments/comment'
    sub = redis.pubsub()
    sub.subscribe('comments')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            comment_data = loads(data['data'])
            comment_data['published_at'] = str(datetime.utcnow())
            if comment_data.get('updated_at'):
                comment_data['updated_at'] = str(datetime.utcnow())
            # resp = post_data(data=comment_data, url=url)
            # if resp.ok:
            #     print(resp.json())
            # else:
            #     print(resp.text)
            # print(comment_data)
            
endpoints = {
    'playlist': add_playlist_to_api,
    'video': add_video_to_api,
    'channel': add_channel_to_api,
    'comment': add_comment_to_api
}         

def process_data(endpoint):
    while True:
        endpoints[endpoint]()

if __name__ == '__main__':
    channel = sys.argv[1]
    process_data(channel)