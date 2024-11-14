import redis
import os 
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize and configure the Redis client connection
redis_client = redis.StrictRedis.from_url(redis_url)