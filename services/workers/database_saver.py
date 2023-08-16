from database.crud import add_channel
from redis import Redis
from json import loads
from database.database import get_db, create_all
from database.models.channel import Channel
from datetime import datetime
import requests

def add_channel_to_db():
    redis = Redis()
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
    url = 'http://localhost:5000/api/v1/channels/channel'
    redis = Redis()
    sub = redis.pubsub()
    sub.subscribe('channels')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            channel_data = loads(data['data'])
            channel_data['published_at'] = str(datetime.utcnow())
            resp = post_data(data=channel_data, url=url)
            if resp.ok:
                print(resp.json())
            else:
                print(resp.text)
                
def add_video_to_api():
    url = 'http://localhost:5000/api/v1/videos/video'
    redis = Redis()
    sub = redis.pubsub()
    sub.subscribe('videos')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            channel_data = loads(data['data'])
            channel_data['published_at'] = str(datetime.utcnow())
            resp = post_data(data=channel_data, url=url)
            if resp.ok:
                print(resp.json)
            else:
                print(resp.text)
                
def add_playlist_to_api():
    url = 'http://localhost:5000/api/v1/playlists/playlist'
    redis = Redis()
    sub = redis.pubsub()
    sub.subscribe('playlists')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            playlist_data = loads(data['data'])
            playlist_data['published_at'] = str(datetime.utcnow())
            resp = post_data(data=playlist_data, url=url)
            if resp.ok:
                print(resp.json())
            else:
                print(resp.text)
            print(playlist_data)
            
def add_comment_to_api():
    url = 'http://localhost:5000/api/v1/comments/comment'
    redis = Redis()
    sub = redis.pubsub()
    sub.subscribe('comments')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            comment_data = loads(data['data'])
            comment_data['published_at'] = str(datetime.utcnow())
            if comment_data.get('updated_at'):
                comment_data['updated_at'] = str(datetime.utcnow())
            resp = post_data(data=comment_data, url=url)
            if resp.ok:
                print(resp.json())
            else:
                print(resp.text)
            print(comment_data)
            
def process_data(endpoint):
    endpoints = {
        'playlist': add_playlist_to_api,
        'video': add_video_to_api,
        'channel': add_channel_to_api,
        'comment': add_comment_to_api
    }
    while True:
        endpoints[endpoint]()

if __name__ == '__main__':
    create_all()
    process_data('playlist')