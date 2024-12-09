from typing import Union

from fastapi import HTTPException
from fastapi.responses import JSONResponse as Response
from starlette.responses import JSONResponse

from utils import status


def success(*, data: Union[list, dict, str]) -> Response:
    return JSONResponse(
        status_code=status.HTTP_SUCCESS,
        content={
            "code": 200,
            "message": "Success",
            "data": data,
        }
    )


def fail(*, status_code: int = status.HTTP_ERROR, detail: str = ''):
    return HTTPException(status_code=status_code, detail=detail)
