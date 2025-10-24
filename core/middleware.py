import time

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config import get_settings
from core import get_logger

settings = get_settings()


def register_middleware(app: FastAPI):
    print("注册中间件")
    register_request_log_middleware(app)
    register_http_request_cors_middleware(app)


def register_http_request_cors_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers
    )


def register_request_log_middleware(app: FastAPI):
    """
    记录请求日志中间件
    :param app:
    :return:
    """

    @app.middleware("http")
    async def request_log_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        http_version = f"http/{request.scope['http_version']}"
        content_length = response.raw_headers[0][1].decode("UTF-8")
        process_time = response.headers["X-Process-Time"]
        content = f"http.log_message: '{request.method} {request.url} {http_version}' {response.status_code}" \
                  f" {response.charset} {content_length} {process_time}"
        get_logger().info(content)

        return response
