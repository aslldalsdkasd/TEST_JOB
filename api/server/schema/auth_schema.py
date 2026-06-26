from pydantic import BaseModel

class UserSchema(BaseModel):
    """Схема пользователя"""
    login: str
    password: str

class TokenResponse(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str = "bearer"