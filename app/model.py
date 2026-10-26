
from datetime import date

from sqlalchemy import Date, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)

    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    course: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enrollment_date: Mapped[date | None] = mapped_column(Date, nullable=True)




    created_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=func.strftime(
            "%Y-%m-%dT%H:%M:%SZ", "now"
        ),
    )
    updated_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default=func.strftime(
            "%Y-%m-%dT%H:%M:%SZ", "now"
        ),
    )
