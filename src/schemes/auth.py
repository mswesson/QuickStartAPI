from pydantic import BaseModel, Field


class UserAuth(BaseModel):
    username: str = Field(
        ...,
        min_length=5,
        max_length=30,
        pattern=r'^[a-zA-Z0-9]+$',
        description="Имя пользователя должно быть латинскими буквами и цифрами.",
    )
    password: str = Field(
        ..., min_length=8, max_length=128, description="Пароль должен быть не менее 8 символов."
    )


class RefreshForm(BaseModel):
    refresh_token: str
