import logging
from typing import Any, Dict

from fastapi import FastAPI

from pyuubin.api.v1 import app as v1_app
from pyuubin.db import redisdb
from pyuubin.health import get_health
from pyuubin.settings import REDIS_URL


async def attach_db():
    """Attach the redis db to app."""
    try:
        await redisdb.connect(REDIS_URL)
    except ConnectionError as e:
        log = logging.getLogger()
        log.error(f"Cannot connect to redis: {e}")
        raise


async def close_db():

    try:
        await redisdb.close()
    except AttributeError:
        pass


async def health_endpoint() -> Dict[str, Any]:
    return get_health()


def get_app():

    app = FastAPI()
    app.mount("/api/v1", v1_app)
    app.add_event_handler("startup", attach_db)
    app.add_event_handler("shutdown", close_db)
    app.get("/health")(health_endpoint)
    return app
