from fastapi import Request, APIRouter

from schemes.responses import ApiResponse
from schemes.auth import RefreshForm, SendCodeRequest, VerifyCodeRequest
from services.auth import AuthServiceDep


router = APIRouter(prefix='/auth')


@router.post('/registration/send-code', response_model=ApiResponse)
async def send_code(creds: SendCodeRequest, auth_service: AuthServiceDep):
    '''Отправляет код верификации пользователю'''
    return await auth_service.send_verify_code(creds)


@router.post('/registration/verify-code', response_model=ApiResponse)
async def verify_code(verify: VerifyCodeRequest, auth_service: AuthServiceDep):
    '''Проверяет код верификации пользователя'''
    return await auth_service.verify_code(verify)


@router.post('/login', response_model=ApiResponse)
async def login(creds: SendCodeRequest, auth_service: AuthServiceDep):
    '''Авторизация в сервисе с помощью username и password'''
    return await auth_service.login_user(creds)


@router.post('/refresh', response_model=ApiResponse)
async def refresh(request: Request, refresh_data: RefreshForm, auth_service: AuthServiceDep):
    '''Принимает рефреш токен и на его основе выдает новый токен доступа'''
    return await auth_service.refresh_token(request, refresh_data)
