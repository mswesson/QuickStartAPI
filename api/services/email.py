from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from celery_client.tasks import send_email


class EmailService:
    '''Сервис для работы с Email'''

    async def send_message(self, subject: str, body: str, to_email: str) -> None:
        '''Отправляет сообщение на почту'''
        send_email.delay(subject, body, to_email)


@lru_cache
def get_email_service() -> EmailService:
    return EmailService()


EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
