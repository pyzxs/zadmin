import jwt
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import get_settings

settings = get_settings()


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 跳过认证的路由
        if request.url.path in ["/api/user/login", "/docs", "/openapi.json", "/media"]:
            return await call_next(request)

        # 获取token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "缺少认证token"}
            )

        token = auth_header[7:]

        try:
            payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
            request.state.user_id = payload.get("id")
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "token已过期"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "无效token"}
            )

        response = await call_next(request)
        return response
