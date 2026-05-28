from pydantic import BaseModel, Field
from decimal import Decimal

class CourseCreate(BaseModel):
    title: str = Field(max_length=100)
    description: str | None = None
    # Используем Decimal. gt=0 означает "greater than 0" (строго больше нуля)
    price: Decimal = Field(default=Decimal("0.00"), gt=Decimal("0.00"))

class CourseResponse(CourseCreate):
    id: int

    class Config:
        from_attributes = True
