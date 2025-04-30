from pydantic import BaseModel, EmailStr, Field


class SendCodeRequest(BaseModel):
    '''Модель для отправки кода верификации'''
    username: str = Field(
        ...,
        min_length=5,
        max_length=30,
        pattern=r'^[a-zA-Z0-9]+$',
        description="Имя пользователя должно быть латинскими буквами и цифрами.",
    )
    email: EmailStr
    password: str = Field(
        ..., min_length=8, max_length=128, description="Пароль должен быть не менее 8 символов."
    )
    
    
class VerifyCodeRequest(BaseModel):
    '''Модель подтверждения кода верификации'''
    email: EmailStr
    code: int

class RefreshForm(BaseModel):
    refresh_token: str
