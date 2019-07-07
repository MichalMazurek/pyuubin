from typing import List
from asynctest import CoroutineMock
from asyncio import Event
import pytest
import pyuubin.connectors.smtp
import pyuubin.worker
from pyuubin.models import Mail
from pyuubin.db import RedisDb, unpack
from pyuubin.settings import REDIS_MAIL_QUEUE
from pyuubin.worker import worker, CannotSendMessages, FailedToSendMessage


class MockRedisDb(RedisDb):
    def __call__(self, consumer_name: str, redis_url: str):

        self.consumer_name = consumer_name
        self.redis_url = redis_url
        self.consumer_queue = f"{REDIS_MAIL_QUEUE}:{self.consumer_name}"

        return self

    async def mail_queue(self, stopped_event=None):

        for _ in range(await self.redis.llen(REDIS_MAIL_QUEUE)):
            mail = await self.redis.rpop(REDIS_MAIL_QUEUE)
            if mail is not None:
                await self.redis.lpush(self.consumer_queue, mail)
                yield Mail(**unpack(mail))
            else:
                break


@pytest.fixture
def mock_redis_db(mock_aioredis, monkeypatch):
    mock_aioredis.monkeypatch_module()
    redis_db = MockRedisDb("test", "redis://localhost")
    monkeypatch.setattr(pyuubin.worker, "RedisDb", redis_db)
    return redis_db


def mail_generator(count: int) -> List[Mail]:

    for x in range(count):
        yield Mail(
            to=[f"mail{x}@example.com"],
            subject=f"[{x}] test subject",
            parameters={"non_secret": "test", "secret_data": "secret"},
            template_id="none",
        )


async def test_worker(mock_aioredis, monkeypatch, mock_redis_db):

    send_mock = CoroutineMock()

    monkeypatch.setattr(pyuubin.connectors.smtp, "send", send_mock)

    await mock_redis_db.connect()
    [await mock_redis_db.add_mail(mail.to_native()) for mail in mail_generator(4)]

    await worker("test", "redis://localhost")

    assert await mock_aioredis.llen(mock_redis_db.consumer_queue) == 0
    assert await mock_redis_db.mail_queue_size() == 0

    send_mock.assert_awaited()

    assert send_mock.await_count == 4


async def test_worker_exception_cannot_send_messages(mock_aioredis, monkeypatch, mock_redis_db):

    send_mock = CoroutineMock()

    def raise_connect_error(*_, **__):
        raise CannotSendMessages("")

    send_mock.side_effect = raise_connect_error

    stopped_event = Event()
    monkeypatch.setattr(pyuubin.connectors.smtp, "send", send_mock)

    await mock_redis_db.connect()
    [await mock_redis_db.add_mail(mail.to_native()) for mail in mail_generator(4)]

    await worker("test", "redis://localhost", stopped_event=stopped_event)

    send_mock.assert_awaited()

    assert stopped_event.is_set()


async def test_worker_exception_failed_to_send_message(mock_aioredis, monkeypatch, mock_redis_db):

    send_mock = CoroutineMock()

    def raise_connect_error(*_, **__):
        raise FailedToSendMessage("")

    send_mock.side_effect = raise_connect_error

    stopped_event = Event()
    monkeypatch.setattr(pyuubin.connectors.smtp, "send", send_mock)

    await mock_redis_db.connect()
    [await mock_redis_db.add_mail(mail.to_native()) for mail in mail_generator(4)]

    await worker("test", "redis://localhost", stopped_event=stopped_event)

    send_mock.assert_awaited()

    assert not stopped_event.is_set()

    assert await mock_aioredis.llen(f"{REDIS_MAIL_QUEUE}::failed") == 4
    failed_msg = unpack(await mock_aioredis.rpop(f"{REDIS_MAIL_QUEUE}::failed"))["mail"]
    assert failed_msg["parameters"]["secret_data"] == "XXXXXX"
