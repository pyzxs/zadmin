import logging
import os

from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi import status
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI

from config import get_settings
from config.config import BASE_DIR

settings = get_settings()
LOG_ERROR_FILE = os.path.join(BASE_DIR, settings.logging.error_path)
LOG_FORMATTER = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s\nTraceback:\n%(exc_text)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

_logger = logging.getLogger("error_logger")
_logger.setLevel(logging.ERROR)

# 创建文件处理器，只记录 ERROR 及以上级别

handler = logging.FileHandler(LOG_ERROR_FILE, encoding="utf-8")
handler.setLevel(logging.ERROR)
handler.setFormatter(LOG_FORMATTER)

_logger.addHandler(handler)


class CustomException(Exception):

    def __init__(
            self,
            msg: str,
            code: int = status.HTTP_400_BAD_REQUEST,
            status_code: int = status.HTTP_200_OK,
            desc: str = None
    ):
        self.msg = msg
        self.code = code
        self.status_code = status_code
        self.desc = desc


def register_exception(app: FastAPI):
    """
    异常捕捉
    """

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """
        自定义异常
        """
        _logger.error(
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Client: {request.client.host if request.client else 'unknown'}\n"
            f"Exception: {type(exc).__name__}",
            exc_info=(type(exc), exc, exc.__traceback__)
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.msg, "code": exc.code},
        )

    @app.exception_handler(HTTPException)
    async def unicorn_exception_handler(request: Request, exc: HTTPException):
        """
        重写HTTPException异常处理器
        """
        _logger.error(
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Client: {request.client.host if request.client else 'unknown'}\n"
            f"Exception: {type(exc).__name__}",
            exc_info=(type(exc), exc, exc.__traceback__)
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        重写请求验证异常处理器
        """
        _logger.error(
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Client: {request.client.host if request.client else 'unknown'}\n"
            f"Exception: {type(exc).__name__}",
            exc_info=(type(exc), exc, exc.__traceback__)
        )
        msg = exc.errors()[0].get("msg")
        if msg == "field required":
            msg = "请求失败，缺少必填项！"
        elif msg == "value is not a valid list":
            msg = f"类型错误，提交参数应该为列表！"
        elif msg == "value is not a valid int":
            msg = f"类型错误，提交参数应该为整数！"
        elif msg == "value could not be parsed to a boolean":
            msg = f"类型错误，提交参数应该为布尔值！"
        elif msg == "Input should be a valid list":
            msg = f"类型错误，输入应该是一个有效的列表！"
        elif msg == "Input should be a valid integer, unable to parse string as an integer":
            msg = f"类型错误：路径参数必须是一个整数！"
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {
                    "message": msg,
                    "body": exc.body,
                    "code": status.HTTP_400_BAD_REQUEST
                }
            ),
        )

    @app.exception_handler(ValueError)
    async def value_exception_handler(request: Request, exc: ValueError):
        """
        捕获值异常
        """
        _logger.error(
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Client: {request.client.host if request.client else 'unknown'}\n"
            f"Exception: {type(exc).__name__}",
            exc_info=(type(exc), exc, exc.__traceback__)
        )
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(
                {
                    "message": exc.__str__(),
                    "code": status.HTTP_400_BAD_REQUEST
                }
            ),
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        捕获全部异常
        """
        _logger.error(
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Client: {request.client.host if request.client else 'unknown'}\n"
            f"Exception: {type(exc).__name__}",
            exc_info=(type(exc), exc, exc.__traceback__)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                {
                    "message": "接口异常！",
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            ),
        )
