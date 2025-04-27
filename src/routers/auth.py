from authx import RequestToken
from fastapi import HTTPException, Request, APIRouter

from authorization.authx import AuthxDep
from schemes.auth import RefreshForm, UserAuth
from services.auth import AuthServiceDep


router = APIRouter(prefix='/auth')


@router.post('/registration')
async def registration(creds: UserAuth, auth_service: AuthServiceDep):
    '''Регистрирует нового пользователя'''
    return await auth_service.registration_new_user(creds)


@router.post('/login')
async def login(creds: UserAuth, auth_service: AuthServiceDep):
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
