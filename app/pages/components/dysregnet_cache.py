from typing import List, Union, Dict
import redis
import pandas as pd
import json

# TODO:
# - implement functionality of maximum number of cached items or time limit
# - implement sanity checks when caching or retrieving cached data
#
# For inspiration take flask_caching as an template:
# https://github.com/pallets-eco/flask-caching/blob/master/src/flask_caching/__init__.py
# However, flask_caching uses a outdated md5 hashing and we want the hash 
# value inside redis to be basically the session ID.
# Thus, we have decided to go with basic redis here and implement 
# funcitonality like flask_caching afterwords.

CACHE_KEY_PREFIX = 'DysRegNet_'

cache = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

def cache_data(session_id: str, results, parameters):
    """
    Function to set DysRegNet parameters and result in redis cache by session_id.
    Args:
        session_id (str): unique session identifier
        results (Dict[Dict[str, str]]): string dictionary of DysRegNet results
        parameters (Dict[str, [Dict[str, Dict[str, str]], 
        str, List[str], bool, float, Union[float, None]]]): dict of DysRegNet 
        parameters
    """
    
    cache.set(
        CACHE_KEY_PREFIX + session_id,
        json.dumps({"results": results, "parameters": parameters})
    )

def get_data(session_id):
    """
    Function to get cached DysRegNet result data based on session_id.
    """

    if 'DysRegNet_' + str(session_id) in cache.keys():
        return json.loads(cache.get(CACHE_KEY_PREFIX + str(session_id)))
    else:
        raise RuntimeError("Missing session_id: " + str(session_id))

def get_results(session_id):
    results = pd.DataFrame(get_data(session_id)["results"])
    # TODO? [tuple(c.split(",")) for c in results_convert.columns]
    return results
