import datetime
import logging

from fastapi import FastAPI

from pyuubin.api.v1 import app as v1_app
from pyuubin.auth import add_authentication
from pyuubin.db import redisdb
from pyuubin.health import update_health
from pyuubin.settings import settings


async def attach_db():
    """Attach the redis db to app."""
    try:
        update_health("start_time", datetime.datetime.utcnow().isoformat())
        await redisdb.connect(settings.redis_url)
    except ConnectionError as e:
        log = logging.getLogger()
        log.error(f"Cannot connect to redis: {e}")
        raise


async def close_db():

    try:
        await redisdb.close()
    except AttributeError:
        pass


def get_app():

    app = FastAPI()
    app.mount("/api/v1", v1_app)
    app.add_event_handler("startup", attach_db)
    app.add_event_handler("shutdown", close_db)

    if settings.auth_htpasswd_file:
        add_authentication(app, settings.auth_htpasswd_file)
    return app


app = get_app()
