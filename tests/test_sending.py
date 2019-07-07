from pyuubin.mailer import get_connector, send_mail
from pyuubin.connectors.smtp import send
from pyuubin.models import Mail
from pyuubin.templates import Templates
import pyuubin.mailer
from asynctest import CoroutineMock


async def test_getting_connector():

    assert send == get_connector("pyuubin.connectors.smtp:send")
    assert send == get_connector("pyuubin.connectors.smtp")


async def test_sending_through_connector(monkeypatch):

    mock_send = CoroutineMock()

    def mock_get_connector(module):
        return mock_send

    monkeypatch.setattr(pyuubin.mailer, "get_connector", mock_get_connector)

    mail = Mail({"to": ["test@example.com"], "subject": "test subject"})
    templates = Templates({})
    await send_mail(mail, templates)

    mock_send.assert_awaited_once_with(mail, templates)
