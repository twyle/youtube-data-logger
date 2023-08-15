from redis import Redis
from json import loads

def read_channels():
    redis = Redis()
    sub = redis.pubsub()
    sub.subscribe('channels')
    for data in sub.listen():
        if isinstance(data['data'], bytes):
            print(loads(data['data']))
            
if __name__ == '__main__':
    while True:
        read_channels()