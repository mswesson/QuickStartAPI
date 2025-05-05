import json
from random import randint
from typing import Annotated

import bcrypt
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

bcrypt.__about__ = bcrypt  # type: ignore

from schemes.responses import ApiResponse
from redis_client.redis import RedisDep
from database.queries import QueriesService, QueriesServiceDep
from authx import AuthX, RequestToken
from fastapi import Depends, Request
from authorization.authx import AuthxDep
from passlib.context import CryptContext

from database.models.user import User
from schemes.auth import RefreshForm, SendCodeRequest, VerifyCodeRequest
from .email import EmailService, EmailServiceDep


class AuthService:
    def __init__(self, db: QueriesService, auth: AuthX, email: EmailService, redis: Redis) -> None:
        self.db = db
        self.auth = auth
        self.email = email
        self.redis = redis

    async def is_exist_user(self, username: str, email: str) -> bool:
        '''Проверяет существует ли пользователь в системе'''
        return await self.db.is_exist_user(username, email)

    async def add_user(self, creds: SendCodeRequest) -> ApiResponse | JSONResponse:
        '''Добавляет пользователя в систему'''
        password_hashed = self._hash_password(creds.password)
        user = User(username=creds.username, email=creds.email, password=password_hashed)

        try:
            await self.db.add_new_user(user)
            return ApiResponse(result='ok', message='The user has been added')
        except Exception as ex:
            if "UNIQUE" in str(ex):
                return JSONResponse(
                    status_code=409,
                    content=ApiResponse(
                        result='error', message='User already exists'
                    ).model_dump(),
                )
            else:
                raise ex

    async def login_user(self, creds: SendCodeRequest) -> ApiResponse | JSONResponse:
        '''Проверяет правильность данных, в случае успеха выдает токен доступа'''
        # TODO: Переделать на почту
        user = await self.db.get_user_by_username(creds.username)

        if not user:
            return JSONResponse(
                status_code=401,
                content=ApiResponse(result='error', message='Invalid username').model_dump(),
            )

        if not self._verify_password(creds.password, user.password):
            return JSONResponse(
                status_code=401,
                content=ApiResponse(result='error', message='Invalid password').model_dump(),
            )

        access_token = self.auth.create_access_token(uid=creds.username)
        refresh_token = self.auth.create_refresh_token(uid=creds.username)
        return ApiResponse(
            result='ok',
            message=('The tokens are located in the data of this response'),
            data={'access_token': access_token, 'refresh_token': refresh_token},
        )

    async def refresh_token(
        self, request: Request, refresh_data: RefreshForm
    ) -> ApiResponse | JSONResponse:
        '''Выдает новый токен доступа по рефреш токену'''
        try:
            try:
                payload = await self.auth.refresh_token_required(request)
            except Exception as ex:
                if not refresh_data or not refresh_data.refresh_token:
                    raise ex

                token = refresh_data.refresh_token
                payload = self.auth.verify_token(
                    RequestToken(token=token, type='refresh', location='json'),
                    verify_type=True,
                )

            access_token = self.auth.create_access_token(uid=payload.sub)
            refresh_token = self.auth.create_refresh_token(uid=payload.sub)
            return ApiResponse(
                result='ok',
                message='The tokens are located in the data of this response',
                data={'access_token': access_token, 'refresh_token': refresh_token},
            )
        except Exception as ex:
            return JSONResponse(
                status_code=401, content=ApiResponse(result='error', message=str(ex)).model_dump()
            )

    async def send_verify_code(self, creds: SendCodeRequest) -> ApiResponse | JSONResponse:
        '''Отправляет сообщение на почту пользователя для регистрации'''
        if await self.is_exist_user(username=creds.username, email=creds.email):
            return JSONResponse(
                status_code=409,
                content=ApiResponse(result='error', message='User already exists').model_dump(),
            )

        secret_code = self._get_random_code()
        await self.email.send_message(
            subject='Подтверждение регистрации',
            body=f'Код подтверждения: {secret_code}',
            to_email=creds.email,
        )
        await self.redis.set(
            f'verify_code_{creds.email}',
            json.dumps({'code': secret_code, **creds.model_dump()}),
            ex=300,
        )
        return ApiResponse(
            result='ok', message='A message with a secret code was sent to your email'
        )

    async def verify_code(self, verify: VerifyCodeRequest) -> ApiResponse | JSONResponse:
        '''Проверяет код с почтой, если связка есть в кэше, то регистрирует пользователя'''
        if creds := await self.redis.get(f'verify_code_{verify.email}'):
            creds = json.loads(creds)
            if creds['code'] == verify.code:
                await self.add_user(SendCodeRequest(**creds))
                return ApiResponse(result='ok', message='User is registered')
        return JSONResponse(
            status_code=409,
            content=ApiResponse(result='error', message='Invalid code').model_dump(),
        )

    def _get_random_code(self) -> int:
        '''Выдает случайны код'''
        return randint(1000, 9999)

    def _hash_password(self, password: str) -> str:
        '''Хеширует пароль'''
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        '''Проверяет совпадет ли пароль с хэшем пароля'''
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)


def get_auth_service(
    db: QueriesServiceDep, auth: AuthxDep, email: EmailServiceDep, redis: RedisDep
) -> AuthService:
    return AuthService(db=db, auth=auth, email=email, redis=redis)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
