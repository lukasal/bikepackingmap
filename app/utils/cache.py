from flask_caching import Cache
from app.utils.config import Config

# Initialize the cache
cache = Cache(
    config={
        "CACHE_TYPE": Config.CACHE_TYPE,
        "CACHE_DEFAULT_TIMEOUT": Config.CACHE_DEFAULT_TIMEOUT,
    }
)
