
"""SQLAlchemy database operations for student management."""

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.model import Student

EDITABLE_FIELDS = {
    "name",
    "date_of_birth",
    "email",
    "phone",
    "course",
    "address",
    "enrollment_date",
}

DATE_FIELDS = {"date_of_birth", "enrollment_date"}


class DuplicateEmailError(Exception):
    """Raised when a student email is already registered."""


def _normalize_input(data: dict[str, Any]) -> dict[str, Any]:
    """Convert JSON date strings into Python date objects."""
    fields = {
        key: value
        for key, value in data.items()
        if key in EDITABLE_FIELDS
    }

    for key in DATE_FIELDS:
        value = fields.get(key)
        if isinstance(value, str) and value:
            fields[key] = date.fromisoformat(value)

    return fields



def _serialize_value(value: Any) -> Any:
    """Convert database values into API-friendly JSON values."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value



def _to_dict(student: Student | None) -> dict[str, Any] | None:
    if student is None:
        return None

    return {
        column.name: _serialize_value(
            getattr(student, column.name)
        )
        for column in Student.__table__.columns
    }


def _is_duplicate_email(exc: IntegrityError) -> bool:
    message = str(exc.orig).lower()
    return "email" in message or "unique constraint failed" in message


def create_student(data: dict[str, Any]) -> dict[str, Any]:
    fields = _normalize_input(data)

    try:
        with SessionLocal() as db:
            student = Student(**fields)
            db.add(student)
            db.commit()
            db.refresh(student)
            return _to_dict(student)
    except IntegrityError as exc:
        if _is_duplicate_email(exc):
            raise DuplicateEmailError from exc
        raise


def list_students(
    *,
    name=None,
    course=None,
    email=None,
    limit=20,
    offset=0,
):
    with SessionLocal() as db:
        statement = select(Student)

        if name:
            statement = statement.where(
                Student.name.ilike(f"%{name.strip()}%")
            )

        if course:
            statement = statement.where(
                func.lower(Student.course).like(f"%{course.strip().lower()}%")
            )

        if email:
            statement = statement.where(
                func.lower(Student.email) == email.strip().lower()
            )

        total = db.scalar(
            select(func.count()).select_from(
                statement.order_by(None).subquery()
            )
        ) or 0

        students = db.scalars(
            statement.order_by(Student.id)
            .limit(limit)
            .offset(offset)
        ).all()

        return {
            "items": [_to_dict(student) for student in students],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


def get_student(student_id: int):
    with SessionLocal() as db:
        student = db.get(Student, student_id)
        return _to_dict(student)


def update_student(
    student_id: int,
    data: dict[str, Any],
):
    fields = _normalize_input(data)

    with SessionLocal() as db:
        student = db.get(Student, student_id)
        if student is None:
            return None

        try:
            for key, value in fields.items():
                setattr(student, key, value)

                student.updated_at = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            db.commit()
            db.refresh(student)
            return _to_dict(student)

        except IntegrityError as exc:
            db.rollback()
            if _is_duplicate_email(exc):
                raise DuplicateEmailError from exc
            raise


def delete_student(student_id: int) -> bool:
    with SessionLocal() as db:
        student = db.get(Student, student_id)

        if student is None:
            return False

        db.delete(student)
        db.commit()
        return True


def student_stats():
    with SessionLocal() as db:
        total = db.scalar(
            select(func.count()).select_from(Student)
        ) or 0

        course_rows = db.execute(
            select(
                func.coalesce(
                    Student.course, "Not specified"
                ).label("course"),
                func.count().label("count"),
            )
            .group_by(Student.course)
            .order_by(func.count().desc(), Student.course.asc())
        ).all()

        latest_students = db.scalars(
            select(Student)
            .order_by(Student.id.desc())
            .limit(5)
        ).all()

        return {
            "total_students": total,
            "students_by_course": [
                {"course": row.course, "count": row.count}
                for row in course_rows
            ],
            "latest_students": [
                {
                    "id": student.id,
                    "name": student.name,
                    "course": student.course,
                    "created_at": _serialize_value(student.created_at),
                }
                for student in latest_students
            ],
        }


def export_students():
    with SessionLocal() as db:
        students = db.scalars(
            select(Student).order_by(Student.id)
        ).all()

        return [_to_dict(student) for student in students]
