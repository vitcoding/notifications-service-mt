import os
from email.message import EmailMessage
from uuid import UUID

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from core.config import config
from core.logger import log

LOGIN = config.smtp.login
PASSWORD = config.smtp.password
DOMAIN = config.smtp.domain
EMAIL = config.smtp.email
SMTP_HOST = config.smtp.host
SMTP_PORT = config.smtp.port


async def send_email(
    email: str, subject: str, text: str, template_id: UUID = None
) -> None:
    """Sends an email."""

    async with aiosmtplib.SMTP(
        hostname=SMTP_HOST, port=SMTP_PORT, use_tls=True
    ) as server:
        await server.login(LOGIN, PASSWORD)

        message = EmailMessage()
        message["From"] = EMAIL
        message["To"] = ",".join([email])
        message["Subject"] = subject

        if template_id is None:
            current_path = os.path.dirname(__file__)
            loader = FileSystemLoader(current_path)
            env = Environment(loader=loader)
            template = env.get_template("mail.html")
        else:
            # API request to get the template
            pass

        data = {
            "title": subject,
            "text": text,
        }
        output = template.render(**data)
        message.add_alternative(output, subtype="html")

        try:
            await server.send_message(message)
        except aiosmtplib.errors.SMTPException as err:
            reason = f"{type(err).__name__}: {err}"
            log.error(f"An error while sending the letter: {reason}")
        else:
            log.debug("The letter has been sent!")
