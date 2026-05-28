from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from src.users.models import User
from src.users.schemas import UserRegister
from src.users.auth import AuthHandler

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, user_data: UserRegister) -> User:
        # Проверяем, существует ли уже пользователь с таким email
        query = select(User).where(User.email == user_data.email)
        result = await self.session.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже зарегистрирован"
            )
        
        # Хэшируем пароль перед сохранением в БД!
        hashed_password = AuthHandler.get_password_hash(user_data.password)
        
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def authenticate_user(self, user_data: UserRegister) -> str:
        # Ищем пользователя в БД
        query = select(User).where(User.email == user_data.email)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        
        # Защита от раскрытия информации: говорим общую фразу "Неверный email или пароль"
        if not user or not AuthHandler.verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
            
        # Если все ок, генерируем JWT токен. Кладем туда id пользователя.
        token = AuthHandler.create_access_token({"sub": str(user.id)})
        return token

