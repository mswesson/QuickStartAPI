from fastapi import Request
from fastapi.responses import JSONResponse

from schemes.responses import ApiResponse


async def invalid_token(request: Request, exc: Exception):
    '''Перехватывает ошибку с невалидным токеном'''
    return JSONResponse(
        status_code=401, content=ApiResponse(result='error', message='Invalid token').model_dump()
    )


async def token_not_found(request: Request, exc: Exception):
    '''Перехватывает ошибку когда токен не найден'''
    return JSONResponse(
        status_code=401,
        content=ApiResponse(result='error', message='Token not found').model_dump(),
    )
