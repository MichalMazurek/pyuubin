import pyuubin.connectors.smtp
from pyuubin.connectors.smtp import send, CannotSendMessages, FailedToSendMessage
from pyuubin.templates import Templates
from pyuubin.models import Mail
from pyuubin.settings import MAIL_FROM
import pytest
from email.parser import Parser
from email.message import Message
from typing import List, Optional
from aiosmtplib import SMTPConnectError, SMTPAuthenticationError, SMTPResponseException, SMTPRecipientsRefused


class MockSMTP:

    messages: List[Message]
    _exception: Optional[Exception]

    def __call__(self, *args, **kwargs):
        """"""
        return self

    def __init__(self, *args, **kwargs):
        """"""
        self.messages = []
        self._connect_exception = None
        self._send_exception = None

    async def send_message(self, message: Message):
        """"""
        if self._send_exception:
            raise self._send_exception
        self.messages.append(message)

    async def ehlo(self):
        pass

    async def auth_plain(self, user, password):

        self.user = user
        self.password = password

    async def connect(self, *args, **kwargs):
        """"""
        if self._connect_exception:
            raise self._connect_exception

    def raise_on_connect(self, exception: Exception):
        self._connect_exception = exception

    def raise_on_send(self, exception: Exception):
        self._send_exception = exception

    def reset_exceptions(self):
        self._send_exception = None
        self._connect_exception = None


@pytest.fixture
def mock_smtp(monkeypatch):

    mocked_smtp = MockSMTP()

    monkeypatch.setattr(pyuubin.connectors.smtp, "SMTP", mocked_smtp)

    return mocked_smtp


mail = Mail()
mail.to = ["test@example.com"]
mail.subject = "test subject"
mail.template_id = "undefined"
mail.parameters = {"message": "test"}

templates = Templates({})


async def test_connect_error(mock_smtp):

    mock_smtp.raise_on_connect(SMTPAuthenticationError(404, "can't connect"))

    with pytest.raises(CannotSendMessages):
        await send(mail, templates)

    mock_smtp.raise_on_connect(SMTPConnectError("can't connect"))

    with pytest.raises(CannotSendMessages):
        await send(mail, templates)

    mock_smtp.reset_exceptions()


async def test_send_exception(mock_smtp):

    mock_smtp.raise_on_send(SMTPRecipientsRefused(mail.to))

    with pytest.raises(FailedToSendMessage):
        await send(mail, templates)

    mock_smtp.raise_on_send(SMTPResponseException(404, "Message"))

    with pytest.raises(FailedToSendMessage):
        await send(mail, templates)

    mock_smtp.reset_exceptions()


async def test_send(mock_smtp):

    message = await send(mail, templates)

    assert str(mock_smtp.messages.pop()) == message

    lines = message.splitlines()

    assert f"From: {MAIL_FROM}" in lines
    assert f"Subject: test subject" in lines
    assert f"To: test@example.com" in lines

    email_parser = Parser()
    message = email_parser.parsestr(message)

    assert message.get_content_type() == "multipart/alternative"

    plain, html = message.get_payload()

    html_body = html.get_payload(decode=True).decode("utf8")
    assert "<dt>message</dt><dd>test</dd>" in html_body
    assert "<dt>missing_template_id</dt><dd>undefined</dd>" in html_body

    plain_body = plain.get_payload(decode=True).decode("utf8")

    assert "message\n\n    test" in plain_body
