import asyncio
import random

import pytest

from aredis_om import get_redis_connection


TEST_PREFIX = "redis-om:testing"


py_test_mark_asyncio = pytest.mark.asyncio


# "pytest_mark_sync" causes problem in pytest
def py_test_mark_sync(f):
    return f  # no-op decorator


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def redis():
    yield get_redis_connection()


def _delete_test_keys(prefix: str, conn):
    if keys := list(conn.scan_iter(f"{prefix}:*")):
        conn.delete(*keys)


@pytest.fixture
def key_prefix(request, redis):
    yield f"{TEST_PREFIX}:{random.random()}"


@pytest.fixture(scope="session", autouse=True)
def cleanup_keys(request):
    # Always use the sync Redis connection with finalizer. Setting up an
    # async finalizer should work, but I'm not suer how yet!
    from redis_om.connections import get_redis_connection as get_sync_redis

    # Increment for every pytest-xdist worker
    conn = get_sync_redis()
    once_key = f"{TEST_PREFIX}:cleanup_keys"
    conn.incr(once_key)

    yield

    # Delete keys only once
    if conn.decr(once_key) == 0:
        _delete_test_keys(TEST_PREFIX, conn)
