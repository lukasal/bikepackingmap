import redis
import os 
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize and configure the Redis client connection
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
