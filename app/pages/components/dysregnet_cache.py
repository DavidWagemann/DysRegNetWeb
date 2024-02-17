import dash
from flask_caching import Cache
import redis

app = dash.get_app()

cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://127.0.0.1',
    'CACHE_DEFAULT_TIMEOUT': 0,
    'CACHE_THRESHOLD': 3,
    'CACHE_KEY_PREFIX': 'DysRegNet_'
})

# r = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

def get_data(session_id):

    if 'DysRegNet_' + session_id in cache.cache._cache:
        return cache.get('DysRegNet_' + session_id)
