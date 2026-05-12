import redis
import json
from typing import Optional
from app.core.config import settings

# Global Redis Client
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

SCHEMA_CACHE_KEY = "skyquery:metadata:schema"
# Long-lived TTL as requested: e.g., 24 hours
SCHEMA_CACHE_TTL = 86400

def set_metadata(metadata_json: str):
    """
    Saves metadata JSON to Redis with a TTL.
    """
    redis_client.setex(SCHEMA_CACHE_KEY, SCHEMA_CACHE_TTL, metadata_json)

def get_metadata() -> Optional[str]:
    """
    Retrieves metadata JSON from Redis.
    """
    return redis_client.get(SCHEMA_CACHE_KEY)

def clear_metadata():
    """
    Removes cached metadata from Redis.
    Called when connection is reset or fails to prevent stale data.
    """
    redis_client.delete(SCHEMA_CACHE_KEY)
