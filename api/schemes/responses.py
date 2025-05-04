from typing import Any, Literal
from pydantic import BaseModel


class ApiResponse(BaseModel):
    result: Literal['ok', 'error']  # статус выполнения
    message: str | None = None  # описание ошибки или сообщения
    data: Any | None = None  # дополнительные данные, если нужно
