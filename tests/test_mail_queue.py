from yuubin.db import RedisDb
import yuubin.db
from pytest import fixture
import asyncio


@fixture
def redis(monkeypatch, mock_aioredis):

    mock_aioredis.monkeypatch_module(yuubin.db)
    return mock_aioredis


async def test_mail_pop(redis, loop):

    db = RedisDb("test_consumer", "redis://localhost:6379/0")
    await db.connect()
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

    await db.add_mail(email_dict)

    async def async_add_mail(email_dict):
        await asyncio.sleep(1)
        await db.add_mail(email_dict)

    counter = 0
    async for mail in db.mail_queue():
        assert mail.to[0] == "test@example.com"
        assert (await db.consumer_queue_size()) == 1
        await db.ack_mail(mail)
        assert (await db.consumer_queue_size()) == 0
        counter += 1
        if counter > 1:
            break
        else:
            asyncio.ensure_future(async_add_mail(email_dict))
