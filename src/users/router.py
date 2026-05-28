from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.users.schemas import UserRegister, UserResponse, TokenResponse
from src.users.service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session)
    return await user_service.register_user(user_data)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), # <- Swagger будет слать форму сюда
    session: AsyncSession = Depends(get_async_session)
):
    user_service = UserService(session)
    
    # Пересобираем схему, так как OAuth2PasswordRequestForm 
    # записывает email в поле username
    credentials = UserRegister(email=form_data.username, password=form_data.password)
    
    token = await user_service.authenticate_user(credentials)
    return {"access_token": token, "token_type": "bearer"}
