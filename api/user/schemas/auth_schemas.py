from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description='登录Token')
    token_type: str = Field(..., description="jwt类型")