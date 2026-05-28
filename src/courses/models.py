from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric
from decimal import Decimal
from src.database import Base

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    # В БД сохраняем как NUMERIC для точных вычислений
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
