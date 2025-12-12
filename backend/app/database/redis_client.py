import redis
import json
import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                logger.info(f"Cache HIT: {key}")
                return json.loads(value)
            logger.info(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            logger.info(f"Cache SET: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
    
    def delete(self, key: str):
        try:
            self.client.delete(key)
            logger.info(f"Cache DELETE: {key}")
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
    
    def exists(self, key: str) -> bool:
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False

redis_client = RedisClient()
