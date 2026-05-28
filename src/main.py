from fastapi import FastAPI
from src.courses.router import router as courses_router
from src.users.router import router as auth_router

app = FastAPI(title="Digital Course Platform")

# Регистрируем роутер курсов в приложении
app.include_router(auth_router)
app.include_router(courses_router)
