from api.middleware import JWTAuthMiddleware
from api.user.views import userAPI


def register_routers(app):
    app.add_middleware(JWTAuthMiddleware)
    app.include_router(userAPI, prefix="/api/user", tags=["user"])