from sanic import Sanic
from sanic_transmute import add_swagger

from yuubin.api.v1 import blueprint as v1_blueprint
from yuubin.db import RedisDb
from yuubin.health import health_endpoint
from yuubin.settings import REDIS_URL
import logging


async def attach_db(app, loop):
    """Attach the redis db to app."""
    try:
        app.db = RedisDb("api", REDIS_URL)
        await app.db.connect()
    except ConnectionError as e:
        log = logging.getLogger()
        log.error(f"Cannot connect to redis: {e}")
        app.stop()


async def close_db(app, loop):

    try:
        await app.db.close()
    except AttributeError:
        pass


def get_app():
    """Return Application instance."""

    app = Sanic(configure_logging=True)

    app.register_listener(attach_db, "before_server_start")
    app.register_listener(close_db, "after_server_stop")
    app.blueprint(v1_blueprint)
    app.add_route(health_endpoint, "/health")
    add_swagger(app, "/api/v1/swagger.json", "/api/v1/")
    return app
