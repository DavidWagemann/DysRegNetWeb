import dash
from flask_caching import Cache

app = dash.get_app()

cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://127.0.0.1',
    'CACHE_KEY_PREFIX': 'DysRegNet_run'
})



