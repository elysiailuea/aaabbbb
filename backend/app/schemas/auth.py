from pydantic import BaseModel


class LoginReq(BaseModel):
    username: str
    password: str


class TokenResp(BaseModel):
    access_token: str
    token_type: str = "bearer"