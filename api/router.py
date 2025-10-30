from api.user.views import userAPI


def register_routers(app):
    app.include_router(userAPI, prefix="/api/user", tags=["user"])