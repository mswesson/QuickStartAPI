from fastapi import Request
from fastapi.responses import JSONResponse

from schemes.responses import ApiResponse


async def server_error(request: Request, exc: Exception):
    '''Перехватывает все ошибки'''    
    return JSONResponse(
        status_code=500,
        content=ApiResponse(result='error', message='Server error').model_dump()
    )
