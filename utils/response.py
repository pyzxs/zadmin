from typing import Union

from fastapi import HTTPException
from fastapi.responses import JSONResponse as Response
from starlette.responses import JSONResponse

from utils import status


def success(*, message, data: Union[list, dict, str] = '') -> Response:
    return JSONResponse(
        status_code=status.HTTP_SUCCESS,
        content={
            "code": 200,
            "message": message,
            "data": data,
        }
    )


def fail(*, status_code: int = status.HTTP_INTERNAL_SERVER_ERROR, detail: str = ''):
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "message": detail
        }
    )
