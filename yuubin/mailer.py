from importlib import import_module
from typing import Awaitable, Coroutine

from yuubin.models import Mail
from yuubin.settings import MAIL_CONNECTOR
from yuubin.templates import Templates


def get_connector(connector_module) -> Coroutine[Awaitable[Mail], str, str]:

    try:
        connector_module, function = connector_module.split(":")
    except ValueError:
        function = "send"

    return getattr(import_module(connector_module), function)


async def send_mail(mail: Mail, templates: Templates):
    """Send one email.

    Args:
        mail (Mail): mail object
    """

    send = get_connector(MAIL_CONNECTOR)
    await send(mail, templates)
