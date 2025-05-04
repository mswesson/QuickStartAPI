from contextlib import asynccontextmanager
from email.message import EmailMessage
from functools import lru_cache
from typing import Annotated
from aiosmtplib import SMTP
from fastapi import Depends
import certifi
import ssl

from config import settings


class EmailService:
    '''Сервис для работы с Email'''

    def __init__(self) -> None:
        pass

    async def send_message(self, message: EmailMessage) -> None:
        '''Отправляет сообщение на почту'''
        async with self._get_smpt_connect() as smtp:
            await smtp.send_message(message)

    @asynccontextmanager
    async def _get_smpt_connect(self):
        '''Контекстный менеджер для получения сессии SMTP'''
        context = ssl.create_default_context(cafile=certifi.where())
        smtp = SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, start_tls=True, tls_context=context)

        await smtp.connect()
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        try:
            yield smtp
        finally:
            await smtp.quit()


@lru_cache
def get_email_service() -> EmailService:
    return EmailService()


EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
