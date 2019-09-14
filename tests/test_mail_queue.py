import asyncio

from pytest import fixture, mark

import pyuubin.db
from pyuubin.db import RedisDb
from pyuubin.models import Mail


@fixture
def redis(monkeypatch, mock_aioredis):

    mock_aioredis.monkeypatch_module(pyuubin.db)
    return mock_aioredis


@mark.asyncio
async def test_mail_pop(redis):

    db = RedisDb()
    await db.connect("redis://localhost:6379/0")
    email_dict = {
        "to": ["test@example.com"],
        "cc": [],
        "subject": "Test Subject",
        "text": "",
        "html": "",
        "template_id": "",
        "parameters": None,
        "meta": None,
    }

    await db.add_mail(Mail(**email_dict))

    async def async_add_mail(email_dict):
        await asyncio.sleep(1)
        await db.add_mail(email_dict)

    async with db.mail_consumer("worker1") as consumer:
        async for mail in consumer.mail_queue():
            assert mail.to[0] == "test@example.com"
            assert (await consumer.consumer_queue_size()) == 1
            await consumer.ack_mail(mail)
            assert (await consumer.consumer_queue_size()) == 0
            consumer.stopped_event.set()
