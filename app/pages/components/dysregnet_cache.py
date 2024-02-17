# import dash
# from flask_caching import Cache
import redis
import pandas as pd
import json

# app = dash.get_app()

# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'redis',
#     'CACHE_TYPE': 'RedisCache',
#     'CACHE_REDIS_URL': 'redis://127.0.0.1',
#     'CACHE_DEFAULT_TIMEOUT': 0,
#     'CACHE_THRESHOLD': 3,
#     'CACHE_KEY_PREFIX': 'DysRegNet_'
# })

cache = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

# def dummy_hash_method():
#     # this assersts session_id is available in scope
#     return session_id
#
#
def get_data(session_id):
    """
    Function to get cached DysRegNet result data based on session_id.
    """

    if 'DysRegNet_' + str(session_id) in cache.keys():
        return json.loads(cache.get('DysRegNet_' + str(session_id)))
    else:
        raise RuntimeError("Missing session_id: " + str(session_id))

def get_results(session_id):
    results = pd.DataFrame(get_data(session_id)["results"])
    # TODO? [tuple(c.split(",")) for c in results_convert.columns]
    return results
