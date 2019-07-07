from asyncio import Event
from dataclasses import asdict
from typing import Any, Dict, Optional

import msgpack
from aioredis import Redis, create_redis_pool

from pyuubin.models import Mail, Template
from pyuubin.settings import REDIS_MAIL_QUEUE, REDIS_PREFIX
from tblib import pickling_support
from contextlib import asynccontextmanager
from logging import getLogger

pickling_support.install()


log = getLogger(__name__)


def pack(data: Any) -> bytes:
    return msgpack.packb(data, use_bin_type=True)


def unpack(packed_data: bytes) -> Any:
    return msgpack.unpackb(packed_data, raw=False)


def _t_id(template_id: str) -> str:
    """Generate template id key for redis

    Args:
        template_id (str): template id

    Returns:
        str: redis key for the template
    """
    return REDIS_PREFIX + f":templates:{template_id}"


class MailQueueConsumer:
    def __init__(self, consumer_name: str, db: "RedisDb"):
        self.consumer_name = consumer_name
        self.consumer_queue = f"{REDIS_MAIL_QUEUE}::consumer::{consumer_name}"
        self.stopped_event = None
        self.db = db

    async def report_failed_mail(self, mail: Mail, traceback: Dict[str, Any]):
        """Report failed mail to a failed mails queue which is: "{REDIS_MAIL_QUEUE}::failed"

        Args:
            mail (Mail): mail object
            traceback (Dict[str, Any]): serialized traceback with tblib
        """
        new_mail_parameters = dict(
            (key, "X" * len(value) if key.startswith("secret_") else value) for key, value in mail.parameters.items()
        )
        failed_mail = asdict(mail)
        failed_mail["parameters"] = new_mail_parameters

        payload = {"mail": failed_mail, "traceback": traceback}
        await self.db.redis.lpush(f"{REDIS_MAIL_QUEUE}::failed", pack(payload))

    async def consumer_queue_size(self):
        return await self.db.redis.llen(self.consumer_queue)

    async def mail_queue(self, stopped_event: Optional[Event] = None):
        """Pop one email"""
        self.stopped_event = stopped_event or Event()
        while not self.stopped_event.is_set():
            mail = await self.redis.brpoplpush(REDIS_MAIL_QUEUE, self.consumer_queue, timeout=1)
            if mail is not None:
                yield Mail(**unpack(mail))

    async def stop_mail_queue(self):
        try:
            self.stopped_event.set()
        except AttributeError:
            pass

    async def ack_mail(self, mail: Mail):
        """Confirm email sent."""
        await self.db.redis.lrem(self.consumer_queue, 1, pack(asdict(mail)))

    async def cleanup(self):
        """Push all leftover messages back to the queue."""
        log.debug(f"Cleaning up the consumer queue. {self.consumer_name}")
        while await self.db.redis.rpoplpush(self.consumer_queue, REDIS_MAIL_QUEUE):
            continue


class RedisDb:
    """Redis db helper."""

    redis: Redis
    consumer_name: str
    redis_url: str
    consumer_queue: str
    _templates: Dict[str, str]

    def __init__(self):
        self.redis = None
        self._templates = {}

    async def connect(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        if self.redis is None:
            self.redis = await create_redis_pool(redis_url)

        return self.redis

    @property
    def connected(self):
        return self.redis is not None

    async def add_mail(self, mail: Dict[str, Any], failure=False):
        try:
            await self.redis.lpush(REDIS_MAIL_QUEUE, pack(asdict(Mail(**mail))))
        except TypeError as e:
            raise TypeError(f"Wrong keywords for Mail: {e}")

    async def mail_queue_size(self):
        return await self.redis.llen(REDIS_MAIL_QUEUE)

    async def close(self):
        if self.redis is not None:
            self.redis.close()
            await self.redis.wait_closed()

    @asynccontextmanager
    async def mail_consumer(self, consumer_name: str):
        """Create a mail queue consumer."""
        consumer = MailQueueConsumer(consumer_name, self)
        yield consumer
        consumer.cleanup()

    async def add_template(self, template: Template):
        """Add/Replace template in REDIS."""
        await self.redis.set(_t_id(template.template_id), template.content)

    async def remove_template(self, template_id: str):
        """Remove template from REDIS."""
        await self.redis.delete(_t_id(template_id))

    async def get_template(self, template_id: str) -> str:
        """Return template content from REDIS."""
        await self.redis.get(_t_id(template_id))

    async def load_templates(self) -> Dict[str, str]:
        """Return available templates"""

        template_ids = await self.redis.keys(_t_id("*"))
        for redis_template_id in template_ids:
            redis_template_id = redis_template_id.decode("utf8")
            template_preffix_length = len(_t_id(""))
            self._templates[redis_template_id[template_preffix_length:]] = (
                await self.redis.get(redis_template_id)
            ).decode("utf8")
        return self._templates


redisdb = RedisDb()
