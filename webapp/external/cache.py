import os

import dash

from flask_caching import Cache


REDIS_URL = os.environ.get("REDIS_URL")
CACHE_CONFIG = {
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_URL": os.environ.get("REDIS_URL", REDIS_URL),
}

app = dash.get_app()
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)
