from functools import lru_cache
from typing import Annotated
from authx import AuthX, AuthXConfig, TokenPayload
from fastapi import Depends, Request
from config import settings


config = AuthXConfig()
config.JWT_SECRET_KEY = settings.AUTH_SECRET_KEY
config.JWT_TOKEN_LOCATION = ['headers']


@lru_cache
def get_auth() -> AuthX:
    return AuthX(config=config)


AuthxDep = Annotated[AuthX, Depends(get_auth)]


async def get_payload(request: Request, auth: AuthxDep) -> TokenPayload:
    return await auth.access_token_required(request)


TokenPayloadDep = Annotated[TokenPayload, Depends(get_payload)]
