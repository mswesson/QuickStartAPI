from fastapi import FastAPI, Request
from authx.exceptions import MissingTokenError, JWTDecodeError

from exceptions.handlers.auth import token_not_found, invalid_token
from exceptions.handlers.api import server_error
from authorization.authx import TokenPayloadDep
from routers.auth import router as auth_router

app = FastAPI()

# обработчики ошибок
app.add_exception_handler(JWTDecodeError, invalid_token)
app.add_exception_handler(MissingTokenError, token_not_found)
app.add_exception_handler(Exception, server_error)

# роуты
app.include_router(prefix='/api', router=auth_router)


@app.get('/protected')
async def protected(request: Request, payload: TokenPayloadDep):
    return {'message': f'Hi, {payload.sub}'}
