from importlib import import_module
from typing import Awaitable, Coroutine

from pyuubin.models import Mail
from pyuubin.settings import settings
from pyuubin.templates import Templates


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

    send = get_connector(settings.mail_connector)
    await send(mail, templates)
