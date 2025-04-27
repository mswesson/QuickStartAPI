from fastapi import FastAPI, Request
from authx.exceptions import MissingTokenError, JWTDecodeError
import uvicorn
from exceptions.handlers.auth import token_not_found, invalid_token
from authorization.authx import TokenPayloadDep
from routers.auth import router as auth_router
from database.connections import DBSessionsDep

app = FastAPI()

# обработчики ошибок
app.add_exception_handler(JWTDecodeError, invalid_token)
app.add_exception_handler(MissingTokenError, token_not_found)

# роуты
app.include_router(prefix='/api', router=auth_router)

@app.get('/protected')
async def protected(request: Request, payload: TokenPayloadDep, session: DBSessionsDep):
    name: str = getattr(payload, 'name')
    print(session)
    return {'message': f'Hi, {name.capitalize()}'}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
