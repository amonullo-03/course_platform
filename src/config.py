from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str = "SUPER_SECRET_KEY_CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Настройки Redis (по умолчанию в Termux он запускается на localhost:6379)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    @property
    def DATABASE_URL(self) -> str:
        # Автоматически собираем строку подключения
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Настройка для чтения .env файла
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Создаем синглтон (один объект настроек на все приложение)
settings = Settings()
