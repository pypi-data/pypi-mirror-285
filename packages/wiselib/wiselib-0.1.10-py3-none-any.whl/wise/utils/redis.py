from unittest.mock import MagicMock

import redis
import redis.lock
from django.conf import settings

from wise.utils.exception import NotLockedError

_redis_client = None


def get_redis_client() -> redis.Redis:
    global _redis_client

    if _redis_client:
        return _redis_client

    redis_settings = settings.ENV.redis
    _redis_client = redis.Redis(
        host=redis_settings.host, port=redis_settings.port, db=redis_settings.db
    )
    return _redis_client


def ensure_locked(lock: redis.lock.Lock) -> None:
    if lock.acquire(blocking=False):
        lock.release()
        raise NotLockedError()


def get_mock_redis():
    r = MagicMock()
    r.get = lambda *args, **kwargs: None
    return r
