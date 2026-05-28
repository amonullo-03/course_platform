import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.courses.models import Course
from src.courses.schemas import CourseCreate, CourseResponse
from src.redis_client import redis_client # Импортируем наш клиент Redis

class CourseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_course(self, course_data: CourseCreate) -> Course:
        new_course = Course(**course_data.model_dump())
        self.session.add(new_course)
        await self.session.commit()
        await self.session.refresh(new_course)
        
        # ОЧИСТКА КЭША: Раз создался новый курс, старый кэш списка курсов стал неактуальным.
        # Удаляем его, чтобы при следующем запросе данные обновились.
        await redis_client.delete("all_courses")
        
        return new_course

    async def get_all_courses(self) -> list[dict]:
        # 1. Пробуем взять данные из кэша Redis
        cached_courses = await redis_client.get("all_courses")
        if cached_courses:
            # Если нашли, превращаем JSON-строку обратно в Python-список и возвращаем
            return json.loads(cached_courses)

        # 2. Если кэша не было, делаем тяжелый запрос в PostgreSQL
        query = select(Course)
        result = await self.session.execute(query)
        courses = result.scalars().all()

        # Превращаем ORM-объекты в валидные словари через Pydantic схему
        courses_jsonable = [CourseResponse.model_validate(c).model_dump(mode="json") for c in courses]

        # 3. Сохраняем результат в Redis на 60 секунд (ex=60)
        await redis_client.set(
            "all_courses", 
            json.dumps(courses_jsonable), 
            ex=60
        )

        return courses_jsonable

