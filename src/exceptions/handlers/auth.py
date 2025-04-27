from fastapi import Request
from fastapi.responses import JSONResponse


async def invalid_token(request: Request, exc: Exception):
    '''Перехватывает ошибку с невалидным токеном'''    
    return JSONResponse(
        status_code=401,
        content={"detail": 'Invalid token'},
    )


async def token_not_found(request: Request, exc: Exception):
    '''Перехватывает ошибку когда токен не найден'''
    return JSONResponse(
        status_code=401,
        content={"detail": 'Token not found'},
    )
