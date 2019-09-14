import logging
from email.message import EmailMessage

import html2text
from aiosmtplib import (
    SMTP,
    SMTPAuthenticationError,
    SMTPConnectError,
    SMTPRecipientsRefused,
    SMTPResponseException,
)

from pyuubin.exceptions import CannotSendMessages, FailedToSendMessage
from pyuubin.models import Mail
from pyuubin.settings import settings
from pyuubin.templates import Templates

log = logging.getLogger(__name__)


async def attach_content(
    mail: Mail, templates: Templates, message: EmailMessage
) -> EmailMessage:
    """Attach content to the mul

    Args:
        mail (Mail): mail object
        templates (Templates): available templates
        message (MIMEMultipart): email message

    Returns:
        MIMEMultipart: message with attachments
    """

    if mail.template_id:
        html = await templates.render(mail.template_id, mail.parameters)
        message.set_content(
            html2text.HTML2Text().handle(html),
            subtype="plain",
            charset="utf-8",
        )
        message.add_alternative(html, subtype="html", charset="utf-8")
    else:
        if mail.html:
            if mail.text:
                message.set_content(
                    mail.text, subtype="plain", charset="utf-8"
                )
            else:
                message.set_content(
                    html2text.HTML2Text().handle(mail.html),
                    subtype="plain",
                    charset="utf-8",
                )
            message.add_alternative(mail.html, subtype="html", charset="utf-8")
        elif mail.text:
            message.set_content(mail.text, subtype="plain", charset="utf-8")

    return message


async def send(mail: Mail, templates: Templates) -> str:
    """Send one email over smtp.

    Raises:
        CannotSendMessages: when cannot connect to smtp server
        FailedToSendMessage: - when cannot send the message

    Args:
        mail (Mail): mail to be sent
        templates (Dict[str, str]): dictionary of templates
    """
    smtp = SMTP(
        hostname=settings.smtp_host,
        port=int(settings.smtp_port),
        use_tls=settings.smtp_tls,
    )

    message = EmailMessage()

    message["From"] = settings.mail_from
    message["Return-Path"] = settings.mail_return
    message["Subject"] = mail.subject
    message["To"] = ", ".join(mail.to)

    if mail.cc:
        message["CC"] = ", ".join(mail.cc)

    if mail.bcc:
        message["BCC"] = ", ".join(mail.bcc)

    message = await attach_content(mail, templates, message)

    try:

        try:
            await smtp.connect()
            if settings.smtp_user:
                await smtp.ehlo()
                await smtp.auth_plain(
                    settings.smtp_user,
                    settings.smtp_password.get_secret_value(),
                )

        except (SMTPConnectError, SMTPAuthenticationError) as e:
            log.error(e)
            if log.getEffectiveLevel() == logging.DEBUG:
                log.exception(e)
            raise CannotSendMessages()

        await smtp.send_message(message)
        smtp.close()

        return str(message)

    except (SMTPRecipientsRefused, SMTPResponseException) as e:
        log.exception(e)
        raise FailedToSendMessage()
