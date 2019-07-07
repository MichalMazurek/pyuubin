import asyncio
import logging
import coloredlogs
from pathlib import Path
from signal import SIGINT, SIGTERM, signal

import click

import pyuubin.settings as settings
from pyuubin.api.app import get_app
from pyuubin.auth import add_authentication
from pyuubin.worker import worker as mailer_worker

coloredlogs.install()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("-s", "--host", envvar="HTTP_HOST", default="0.0.0.0", help="Host to run HTTP API on.")
@click.option("-p", "--port", envvar="HTTP_PORT", default=8080, type=int, help="Port to run HTTP API on.")
@click.option("-d", "--debug", envvar="DEBUG", default=False, flag_value=True, help="Enable debug mode.")
@click.option("-r", "--redis-url", envvar="REDIS_URL", default="redis://localhost:6379", help="Url to redis.")
@click.option("-e", "--prefix", envvar="REDIS_PREFIX", default="pyuubin:", help="Prefix for mail queue.")
@click.option("-q", "--queue-name", envvar="REDIS_MAIL_QUEUE", default=None, help="Mail queue name.")
@click.option(
    "-P", "--htpasswd-file", envvar="AUTH_HTPASSWD_FILE", default="", help="A htpasswd file with passwords for app"
)
def main(
    ctx: click.Context,
    host: str,
    port: int,
    debug: bool,
    redis_url: str,
    prefix: str,
    queue_name: str,
    htpasswd_file: str,
):

    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    log = logging.getLogger(__name__)

    settings.REDIS_URL = redis_url

    log.info(f"Will use redis: {settings.REDIS_URL}.")

    if ctx.invoked_subcommand is not None:
        return

    app = get_app()

    def get_ssl():
        if not settings.SSL_ENABLED:
            return None

        if not Path(settings.SSL_CERT).exists():
            import pyuubin.certs as certs

            certs.create_self_signed_certificate(settings.SSL_CERT, settings.SSL_KEY)

        return {"cert": settings.SSL_CERT, "key": settings.SSL_KEY}

    if settings.AUTH_HTPASSWD_FILE:
        add_authentication(app)
    else:
        log.warning("No httpasswd file given in AUTH_HTPASSWD_FILE. Running without authentication.")

    app.run(host, port, debug=debug, ssl=get_ssl())


@main.command()
@click.option("-n", "--name", help="Name of the service", default="main", type=str)
@click.option("-w", "--workers", help="Number of workers", default=3, type=int)
@click.pass_context
def worker(ctx: click.Context, name: str, workers: int):
    async def worker_spawner(stopped_event: asyncio.Event):
        await asyncio.gather(
            *[mailer_worker(name, settings.REDIS_URL, stopped_event=stopped_event) for _ in range(workers)]
        )

    stopped_event = asyncio.Event()

    def stop_queue(*args, **kwargs):
        stopped_event.set()

    signal(SIGINT, stop_queue)
    signal(SIGTERM, stop_queue)

    asyncio.run(worker_spawner(stopped_event))


if __name__ == "__main__":
    main()
