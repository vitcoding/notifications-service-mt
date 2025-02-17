import os
from email.message import EmailMessage
from typing import Any
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


class EmailService:
    """A class for work with emails."""

    def __init__(self) -> None:
        self._server = None

    async def __aenter__(self) -> "EmailService":
        self._server = aiosmtplib.SMTP(
            hostname=SMTP_HOST, port=SMTP_PORT, use_tls=True
        )
        await self._server.connect()
        await self._server.login(LOGIN, PASSWORD)
        log.info("\nEmail login done.")
        return self

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        if self._server:
            await self._server.quit()

    async def send_email(
        self, email: str, subject: str, text: str, template_id: UUID = None
    ) -> None:
        """Sends a message."""

        message = EmailMessage()
        message["From"] = EMAIL
        message["To"] = email
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
            await self._server.send_message(message)
        except aiosmtplib.errors.SMTPException as err:
            reason = f"{type(err).__name__}: {err}"
            log.error(f"An error while sending the letter: {reason}")
        else:
            log.info(f"\nThe letter has been sent! \nEmail: {email}")
