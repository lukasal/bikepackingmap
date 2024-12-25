import redis
import os 
redis_url = os.getenv("REDIS_HOST", "localhost")

# Initialize and configure the Redis client connection
redis_client = redis.StrictRedis(
    host=redis_url, port=6379, db=0, password=os.getenv("REDIS_KEY")
)
