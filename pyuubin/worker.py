import asyncio
import logging
import sys
from asyncio import Event
from signal import SIGINT, SIGTERM
from typing import Optional
from uuid import uuid4

import click
import coloredlogs
import tblib

from pyuubin.db import RedisDb
from pyuubin.exceptions import CannotSendMessages, FailedToSendMessage
from pyuubin.mailer import send_mail
from pyuubin.settings import print_env_variables, settings
from pyuubin.templates import Templates


async def worker(
    consumer_name: str,
    redis_url: str,
    worker_id: Optional[str] = None,
    stopped_event: Optional[Event] = None,
):

    worker_id = worker_id or uuid4()
    log = logging.getLogger(f"pyuubin.worker.{worker_id}")
    db = RedisDb()
    await db.connect(redis_url)
    stopped_event = stopped_event or Event()

    log.info(f"Starting worker: {worker_id} for `{consumer_name}`.")

    async with db.mail_consumer(consumer_name) as consumer:
        async for email in consumer.mail_queue(stopped_event):

            templates = Templates(await db.load_templates())
            log.info("Received an email and sending it.")
            try:
                await send_mail(email, templates)
                log.info("Email sent.")
            except CannotSendMessages as e:
                await db.add_mail(email)
                log.error("Cannot send messages.")
                if (
                    log.getEffectiveLevel() == logging.DEBUG
                ):  # pragma: no cover
                    log.exception(e)
                stopped_event.set()
            except (FailedToSendMessage, Exception) as e:
                et, ev, tb = sys.exc_info()
                await consumer.report_failed_mail(
                    email, traceback=tblib.Traceback(tb).to_dict()
                )
                log.error(f"Failed to send message: {e}")
                log.exception(e)
            finally:
                await consumer.ack_mail(email)

    log.info("Shutting down the worker.")
    await db.close()


@click.command()
@click.option(
    "-n", "--name", help="Name of the service", default="main", type=str
)
@click.option("-w", "--workers", help="Number of workers", default=3, type=int)
@click.option(
    "-d",
    "--debug",
    envvar="DEBUG",
    default=False,
    flag_value=True,
    help="Enable debug mode.",
)
@click.option(
    "-e",
    "--print-environment-variables",
    help="print environment variables to be put in .env file for configuration",
    type=bool,
    flag_value=True,
)
def main(
    name: str = "main",
    workers: int = 3,
    debug: bool = False,
    print_environment_variables: bool = True,
):
    """Run the worker."""
    if print_environment_variables:
        print_env_variables()
        return

    async def worker_spawner():

        loop = asyncio.get_event_loop()

        stopped_event = asyncio.Event()

        def stop_queue(*args, **kwargs):
            stopped_event.set()

        loop.add_signal_handler(SIGINT, stop_queue)
        loop.add_signal_handler(SIGTERM, stop_queue)

        await asyncio.gather(
            *[
                worker(name, settings.redis_url, stopped_event=stopped_event)
                for _ in range(workers)
            ]
        )

    coloredlogs.install(level=logging.INFO if not debug else logging.DEBUG)

    asyncio.run(worker_spawner())


if __name__ == "__main__":
    main()
