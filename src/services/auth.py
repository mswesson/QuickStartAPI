from functools import lru_cache
from mimetypes import init
from typing import Annotated

import bcrypt

from database.queries import QueriesService, QueriesServiceDep
bcrypt.__about__ = bcrypt  # type: ignore
from authx import AuthX
from fastapi import Depends, HTTPException
from sqlalchemy import Select
from authorization.authx import AuthxDep
from database.connections import DBSessionsDep
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from database.models.user import User
from schemes.auth import UserAuth

class AuthService:
    def __init__(self, db: QueriesService, auth: AuthX) -> None:
        self.db = db
        self.auth = auth
        
    async def registration_new_user(self, creds: UserAuth):
        '''Регистрирует нового пользователя в системе'''
        password_hashed = self._hash_password(creds.password)
        user = User(username=creds.username, password=password_hashed)
        try:
            await self.db.add_new_user(user)
            return {'status': 'ok'}
        except Exception as ex:
            if "UNIQUE" in str(ex):
                raise HTTPException(status_code=409, detail="A user with that name already exists")
            else:
                raise HTTPException(status_code=500, detail="Unknown server error")
    
    async def login_user(self, creds: UserAuth):
        '''Проверяет правильность данных, в случае успеха выдает токен доступа'''
        user = await self.db.get_user_by_username(creds.username)

        if not user:
            raise HTTPException(status_code=401, detail='Invalid username') 
        
        if not self._verify_password(creds.password, user.password):
            raise HTTPException(status_code=401, detail='Invalid password') 
        
        token = self.auth.create_access_token(uid='12345', data={'name': creds.username})
        refresh_token = self.auth.create_refresh_token(uid='12345', data={'name': creds.username})
        return {'token': token, 'refresh_token': refresh_token}

    def _hash_password(self, password: str) -> str:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
        

def get_auth_service(db: QueriesServiceDep, auth: AuthxDep) -> AuthService:
    return AuthService(db=db, auth=auth)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
