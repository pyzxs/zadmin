from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.requests import Request

from api import auth
from api.auth import get_current_user
from api.user.schemas import auth_schemas
from core.database import get_db
from models.user import User

userAPI = APIRouter()


@userAPI.post("/login", response_model=auth_schemas.Token, name="文档登录认证", include_in_schema=False)
async def api_login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = auth.check_user_login(db, data)
    return {"access_token": token, "token_type": "bearer"}


@userAPI.post("list", name="测试")
def api_list(request: Request):
    return {"username": request.state.user_id}
