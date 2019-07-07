import logging
from asyncio import Event
from typing import Optional
from uuid import uuid4
import sys
import tblib

from pyuubin.db import RedisDb
from pyuubin.exceptions import CannotSendMessages, FailedToSendMessage
from pyuubin.mailer import send_mail
from pyuubin.templates import Templates


async def worker(
    consumer_name: str, redis_url: str, worker_id: Optional[str] = None, stopped_event: Optional[Event] = None
):

    worker_id = worker_id or uuid4()
    log = logging.getLogger(f"{__name__}.{worker_id}")
    db = RedisDb(consumer_name, redis_url)
    await db.connect()
    stopped_event = stopped_event or Event()

    log.info(f"Starting worker: {worker_id} for `{consumer_name}`.")

    async for email in db.mail_queue(stopped_event):

        templates = Templates(await db.load_templates())
        log.info("Received an email and sending it.")
        try:
            await send_mail(email, templates)
            log.info("Email sent.")
        except CannotSendMessages as e:
            await db.add_mail(email)
            log.error("Cannot send messages.")
            if log.getEffectiveLevel() == logging.DEBUG:
                log.exception(e)
            stopped_event.set()
        except (FailedToSendMessage, Exception) as e:
            et, ev, tb = sys.exc_info()
            await db.report_failed_mail(email, traceback=tblib.Traceback(tb).to_dict())
            log.error(f"Failed to send message: {e}")
            log.exception(e)
        finally:
            await db.ack_mail(email)

    log.info("Shutting down the worker.")
    await db.close()
