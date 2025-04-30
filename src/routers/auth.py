from random import randint
from authx import RequestToken
from fastapi import HTTPException, Request, APIRouter

from authorization.authx import AuthxDep
from schemes.auth import RefreshForm, SendCodeRequest, VerifyCodeRequest
from services.auth import AuthServiceDep


router = APIRouter(prefix='/auth')


redis = {}


@router.post('/send-code')
async def send_code(creds: SendCodeRequest, auth_service: AuthServiceDep):
    '''Отправляет код верификации пользователю'''
    if await auth_service.is_exist_user(username=creds.username, email=creds.email):
        raise HTTPException(status_code=409, detail="User already exists")
    
    secret_code = randint(1000, 9999)
    await auth_service.send_verificatin_code(secret_code, creds.email)
    redis[creds.email] = {'code': secret_code, **creds.model_dump()}
    print(redis)
    return {'result': 'ok'}


@router.post('/verify-code')
async def verify_code(verify: VerifyCodeRequest, auth_service: AuthServiceDep):
    '''Проверяет код верификации пользователя'''
    if (creds := redis.get(verify.email)):
        if creds['code'] == verify.code:
            await auth_service.add_user(SendCodeRequest(**creds))
            return {'result': 'ok'}
    raise HTTPException(status_code=409, detail="Invalid code")


@router.post('/login')
async def login(creds: SendCodeRequest, auth_service: AuthServiceDep):
    '''Авторизация в сервисе с помощью username и password'''
    return await auth_service.login_user(creds)


@router.post('/refresh')
async def refresh(request: Request, auth: AuthxDep, refresh_data: RefreshForm):
    '''Принимает рефреш токен и на его основе выдает новый токен доступа'''
    try:
        try:
            payload = await auth.refresh_token_required(request)
        except Exception as ex:
            if not refresh_data or not refresh_data.refresh_token:
                raise ex

            token = refresh_data.refresh_token
            payload = auth.verify_token(
                RequestToken(token=token, type='refresh', location='json'),
                verify_type=True,
            )

        access_token = auth.create_access_token(uid=payload.sub)
        return {"access_token": access_token}
    except Exception as ex:
        raise HTTPException(status_code=401, detail=str(ex))
