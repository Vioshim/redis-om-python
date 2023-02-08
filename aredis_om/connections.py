import os

from . import redis


URL = os.environ.get("REDIS_OM_URL", None)


def get_redis_connection(**kwargs) -> redis.Redis:
    # Decode from UTF-8 by default
    if "decode_responses" not in kwargs:
        kwargs["decode_responses"] = True

    if url := kwargs.pop("url", URL):
        return redis.Redis.from_url(url, **kwargs)

    return redis.Redis(**kwargs)
