import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.database import get_async_session
from src.users.models import User

# Указываем FastAPI, где находится эндпоинт авторизации для Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthHandler:
    @staticmethod
    def _prepare_password(password: str) -> bytes:
        """
        Сжимает пароль любой длины через SHA-256 в 32 байта.
        Снимает лимит bcrypt в 72 символа и защищает кириллицу.
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """Хэширует подготовленный пароль с солью через bcrypt."""
        prepared = cls._prepare_password(password)
        # Генерируем соль и хэшируем. На выходе получаем bytes.
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(prepared, salt)
        # Декодируем в строку для сохранения в текстовое поле БД
        return hashed.decode("utf-8")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Безопасно проверяет пароль за константное время.
        """
        prepared = cls._prepare_password(plain_password)
        # bcrypt.checkpw требует bytes на входе
        return bcrypt.checkpw(prepared, hashed_password.encode("utf-8"))

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Генерирует временный JWT токен."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """Зависимость для проверки JWT и извлечения текущего пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    query = select(User).where(User.id == int(user_id))
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь деактивирован"
        )
        
    return user

