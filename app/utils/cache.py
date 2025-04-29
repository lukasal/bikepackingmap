from flask_caching import Cache
from app.utils.config import Config
import os


# Initialize the cache
cache = Cache(
    config={
        "CACHE_TYPE": Config.CACHE_TYPE,
        "CACHE_DEFAULT_TIMEOUT": Config.CACHE_DEFAULT_TIMEOUT,
        "CACHE_REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    }
)
