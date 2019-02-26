import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import html2text
from aiosmtplib import SMTP, SMTPAuthenticationError, SMTPConnectError, SMTPRecipientsRefused, SMTPResponseException

from yuubin import settings
from yuubin.exceptions import CannotSendMessages, FailedToSendMessage
from yuubin.models import Mail
from yuubin.templates import Templates

log = logging.getLogger(__name__)


async def attach_content(mail: Mail, templates: Templates, message: MIMEMultipart) -> MIMEMultipart:
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
        message.attach(MIMEText(html, "html", "utf-8"))
        message.attach(MIMEText(html2text.HTML2Text().handle(html), "plain", "utf-8"))
    else:
        if mail.html:
            message.attach(MIMEText(mail.html, "html", "utf-8"))
            if mail.text:
                message.attach(MIMEText(html2text.HTML2Text().handle(mail.html), "plain", "utf-8"))
            else:
                message.attach(MIMEText(html2text.HTML2Text().handle(html), "plain", "utf-8"))
        elif mail.text:
            message.attach(MIMEText(mail.text, "plain", "utf-8"))

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
    smtp = SMTP(hostname=settings.SMTP_HOST, port=int(settings.SMTP_PORT))

    try:
        await smtp.connect()
    except (SMTPConnectError, SMTPAuthenticationError) as e:
        log.error(e)
        if log.getEffectiveLevel() == logging.DEBUG:
            log.exception(e)
        raise CannotSendMessages()

    message = MIMEMultipart("alternative")

    message["From"] = settings.MAIL_FROM
    message["Return-Path"] = settings.MAIL_RETURN
    message["Subject"] = mail.subject
    message["To"] = ", ".join(mail.to)

    if mail.cc:
        message["CC"] = ", ".join(mail.cc)

    if mail.bcc:
        message["BCC"] = ", ".join(mail.bcc)

    message = await attach_content(mail, templates, message)

    try:
        await smtp.send_message(message)
        return str(message)

    except (SMTPRecipientsRefused, SMTPResponseException) as e:
        log.exception(e)
        raise FailedToSendMessage()
