import redis.asyncio as aioredis
from src.config import settings

# Создаем асингулярный клиент для работы с Redis
redis_client = aioredis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    decode_responses=True # Автоматически декодирует байты в строки Python
)

