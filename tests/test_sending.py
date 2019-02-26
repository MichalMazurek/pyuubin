from yuubin.mailer import get_connector, send_mail
from yuubin.connectors.smtp import send
from yuubin.models import Mail
from yuubin.templates import Templates
import yuubin.mailer
from asynctest import CoroutineMock


async def test_getting_connector():

    assert send == get_connector("yuubin.connectors.smtp:send")
    assert send == get_connector("yuubin.connectors.smtp")


async def test_sending_through_connector(monkeypatch):

    mock_send = CoroutineMock()

    def mock_get_connector(module):
        return mock_send

    monkeypatch.setattr(yuubin.mailer, "get_connector", mock_get_connector)

    mail = Mail({"to": ["test@example.com"], "subject": "test subject"})
    templates = Templates({})
    await send_mail(mail, templates)

    mock_send.assert_awaited_once_with(mail, templates)
