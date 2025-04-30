from email.message import EmailMessage
from typing import Annotated

import bcrypt
bcrypt.__about__ = bcrypt  # type: ignore

from database.queries import QueriesService, QueriesServiceDep
from authx import AuthX
from fastapi import Depends, HTTPException
from authorization.authx import AuthxDep
from passlib.context import CryptContext

from database.models.user import User
from schemes.auth import SendCodeRequest
from .email import EmailService, EmailServiceDep
from config import settings

class AuthService:
    def __init__(self, db: QueriesService, auth: AuthX, email: EmailService) -> None:
        self.db = db
        self.auth = auth
        self.email = email
        
    async def is_exist_user(self, username: str, email: str) -> bool:
        '''Проверяет существует ли пользователь в системе'''
        return await self.db.is_exist_user(username, email)
        
    async def send_verificatin_code(self, code: int, email_to: str) -> None:
        '''Отправляет код верификации, для регистрации пользователя'''
        email_message = EmailMessage()
        email_message["From"] = settings.SMTP_USER
        email_message["To"] = email_to
        email_message["Subject"] = "Подтверждение регистрации"
        email_message.set_content(f"Ваш код подтверждения: {code}")
        await self.email.send_message(email_message)

    async def add_user(self, creds: SendCodeRequest) -> dict[str, str]:
        '''Добавляет пользователя в систему'''
        password_hashed = self._hash_password(creds.password)
        user = User(username=creds.username, email=creds.email, password=password_hashed)        
        
        try:
            await self.db.add_new_user(user)
            return {'status': 'ok'}
        except Exception as ex:
            if "UNIQUE" in str(ex):
                raise HTTPException(status_code=409, detail="User already exists")
            else:
                raise HTTPException(status_code=500, detail="Unknown server error")
    
    async def login_user(self, creds: SendCodeRequest) -> dict[str, str]:
        '''Проверяет правильность данных, в случае успеха выдает токен доступа'''
        # TODO: Переделать на почту
        user = await self.db.get_user_by_username(creds.username)

        if not user:
            raise HTTPException(status_code=401, detail='Invalid username') 
        
        if not self._verify_password(creds.password, user.password):
            raise HTTPException(status_code=401, detail='Invalid password') 
        
        token = self.auth.create_access_token(uid=creds.username)
        refresh_token = self.auth.create_refresh_token(uid=creds.username)
        return {'token': token, 'refresh_token': refresh_token}

    def _hash_password(self, password: str) -> str:
        '''Хеширует пароль'''
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        '''Проверяет совпадет ли пароль с хэшем пароля'''
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
        

def get_auth_service(db: QueriesServiceDep, auth: AuthxDep, email: EmailServiceDep) -> AuthService:
    return AuthService(db=db, auth=auth, email=email)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
