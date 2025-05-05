import ssl
from email.message import EmailMessage

import certifi
from smtplib import SMTP
from celery import Celery

from config import settings

celery_app = Celery('tasks', broker=settings.CELERY_BROKER_URL)


@celery_app.task
def send_email(subject: str, body: str, to_email: str):
    '''Отправляет Email сообщение через SMTP'''
    email_message = EmailMessage()
    email_message["From"] = settings.SMTP_USER
    email_message["To"] = to_email
    email_message["Subject"] = subject
    email_message.set_content(body)

    try:
        with SMTP(host=settings.SMTP_HOST, port=settings.SMTP_PORT) as server:
            context = ssl.create_default_context(cafile=certifi.where())
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(email_message)
    except Exception as e:
        print(f'Ошибка при отправке письма: {e}')
