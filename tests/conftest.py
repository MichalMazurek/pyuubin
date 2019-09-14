from asyncio import Event, TimeoutError, wait_for
from collections import defaultdict
from typing import Union

import pytest

import pyuubin.db as app_module
from pyuubin.api.app import get_app


class MockedAioRedis(object):
    def __init__(self, monkeypatch):

        self.me = {}
        self.monkeypatch = monkeypatch
        self.expires = {}
        self.my_events = defaultdict(Event)

    def monkeypatch_module(self, module=app_module, name="create_redis_pool"):
        async def instantiate_me(*a, **k):
            return self

        self.monkeypatch.setattr(module, name, instantiate_me)

    def __call__(self, *args, **kwargs):
        return self

    async def __aexit__(self, *args, **kwargs):
        """Exit context."""

    async def __aenter__(self, *args, **kwargs):
        """Set context."""
        return self

    async def set(self, key, value, expire=0):
        self.me[key] = value.encode("utf8")
        if expire:
            self.expires[key] = expire

    async def get(self, key):
        try:
            return self.me[key]
        except KeyError:
            return None

    async def keys(self, preffix: str):

        try:
            preffix, _ = preffix.split("*")
        except ValueError:
            preffix = ""

        return [
            key.encode("utf8")
            for key in self.me.keys()
            if key.startswith(preffix)
        ]

    async def ttl(self, key):
        return self.expires[key]

    async def llen(self, key):
        try:
            return len(self.me[key])
        except KeyError:
            return 0

    async def delete(self, key):
        try:
            del self.me[key]
        except KeyError:
            pass

    async def lpush(self, key: str, value: Union[str, bytes]):
        try:
            value = value.encode("utf8")
        except AttributeError:
            pass

        try:
            self.me[key].insert(0, value)
            self.my_events[key].set()
        except KeyError:
            self.me[key] = [value]

    async def rpop(self, key):
        return self.me[key].pop()

    async def rpoplpush(self, key_1, key_2):
        try:
            item = self.me[key_1].pop()
            await self.lpush(key_2, item)
            return item
        except IndexError:
            return None

    async def lrange(self, key, start, stop):

        return list(self.me[key][start:stop])

    async def brpoplpush(self, key_1, key_2, timeout=1):

        try:
            if self.me[key_1]:
                item = self.me[key_1].pop()
                await self.lpush(key_2, item)
                return item
            else:
                try:
                    await wait_for(
                        self.my_events[key_1].wait(), timeout=timeout
                    )
                    self.my_events[key_1].clear()
                    item = self.me[key_1].pop()
                    await self.lpush(key_2, item)
                    return item
                except (TimeoutError, IndexError):
                    return None
        except KeyError:
            return None

    async def lrem(self, key, count, value):
        try:
            value = value.encode("utf8")
        except AttributeError:
            pass
        try:
            self.me[key].remove(value)
        except KeyError:
            return None
        except ValueError:
            raise

    def close(self):
        """"""

    async def wait_closed(self):
        pass


@pytest.fixture()
def mock_aioredis(monkeypatch):

    with monkeypatch.context() as m:
        mocked_aioredis = MockedAioRedis(m)
        yield mocked_aioredis


@pytest.fixture
def app(mock_aioredis):
    mock_aioredis.monkeypatch_module()
    app = get_app()
    yield app


@pytest.fixture
def test_cli(app):

    from starlette.testclient import TestClient

    with TestClient(app) as client:
        yield client
