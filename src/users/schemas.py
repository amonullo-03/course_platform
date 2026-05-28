from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr # Автоматически проверит валидность email-адреса
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

