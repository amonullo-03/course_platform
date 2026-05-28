from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.courses.schemas import CourseCreate, CourseResponse
from src.courses.service import CourseService
# Импортируем модель пользователя и функцию проверки токена
from src.users.auth import get_current_user
from src.users.models import User
from src.tasks.worker import send_welcome_email_task # Импортируем нашу задачу

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

@router.post("/{course_id}/buy", status_code=status.HTTP_200_OK)
async def buy_course(
    course_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Эндпоинт имитации покупки курса.
    Защищен авторизацией. Мгновенно возвращает ответ,
    а отправку письма перекладывает на плечи Celery.
    """
    # Имитируем, что мы нашли курс в БД (для примера возьмем заглушку названия)
    course_title = f"Курс №{course_id}"
    
    # КРИТИЧЕСКИ ВАЖНО: Вызываем задачу через метод .delay()
    # Если вызвать просто send_welcome_email_task(), код выполнится синхронно и заморозит FastAPI.
    # Метод .delay() отправляет только инструкции в Redis и мгновенно идет дальше.
    send_welcome_email_task.delay(current_user.email, course_title)
    
    return {
        "status": "success",
        "message": "Покупка оформлена. Письмо с доступом генерируется воркером на заднем плане."
    }
