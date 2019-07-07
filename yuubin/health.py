from collections import defaultdict
from copy import deepcopy
from typing import Any, Dict, List

from sanic import response

from pyuubin import __version__ as version


def health_dict():
    return defaultdict(health_dict)


_health = health_dict()


def update_health(key: str, value: Any):
    """Update health state.

    Args:
        key (str): key to update, it can be a dot delimited path like: status.threads.1
        value (Any): value, non json serialisable will be a problem later.
    """
    path = key.split(".")

    def _update_health(health: Dict[str, Any], path: List[str], value: Any):

        if len(path) == 1:
            health[path[0]] = value
        elif path:
            _update_health(health[path[0]], path[1:], value)

    _update_health(_health, path, value)


def get_health() -> Dict[str, Any]:

    return deepcopy(_health)


async def health_endpoint(request) -> response.BaseHTTPResponse:

    return response.json({"version": version, **get_health()})
