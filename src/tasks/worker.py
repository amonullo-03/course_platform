import asyncio
from celery import Celery
from src.config import settings

# Инициализируем Celery. 
# В качестве брокера (куда складывать задачи) и резалт-бэкенда (куда писать результаты) используем Redis.
celery_app = Celery(
    "course_tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

# Ограничиваем Celery, чтобы он не забивал память в Termux
celery_app.conf.update(
    worker_max_tasks_per_child=100,
    task_ignore_result=True # Нам не нужно сохранять статус выполнения в Redis ради экономии памяти
)

@celery_app.task(name="send_welcome_email")
def send_welcome_email_task(user_email: str, course_title: str):
    """
    Фоновая задача. Celery запускает её в отдельном процессе.
    Она имитирует долгую отправку письма или генерацию PDF.
    """
    import time
    print(f"[Celery] Начало отправки письма для {user_email}...")
    
    # Имитируем тяжелую работу (зависание на 5 секунд)
    time.sleep(5) 
    
    print(f"[Celery] Письмо об успешной покупке курса '{course_title}' успешно отправлено на {user_email}!")
    return True

