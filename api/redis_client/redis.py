from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from redis.asyncio import Redis


@lru_cache
def get_redis():
    return Redis(host="redis", port=6379, decode_responses=True)


RedisDep = Annotated[Redis, Depends(get_redis)]
