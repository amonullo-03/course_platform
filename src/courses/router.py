from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.courses.schemas import CourseCreate, CourseResponse
from src.courses.service import CourseService

# Импортируем модель пользователя и функцию проверки токена
from src.users.auth import get_current_user
from src.users.models import User

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


# Защищенный эндпоинт: добавили зависимость current_user
@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user) # <- FastAPI не пустит сюда без валидного токена!
):
    # Теперь внутри функции у нас есть доступ к `current_user`, 
    # например, мы можем привязать курс к его создателю (автору).
    course_service = CourseService(session)
    return await course_service.create_new_course(course_data)


# Открытый эндпоинт: смотреть курсы могут все (даже неавторизованные)
@router.get("/", response_model=list[CourseResponse])
async def get_courses(session: AsyncSession = Depends(get_async_session)):
    course_service = CourseService(session)
    return await course_service.get_all_courses()
