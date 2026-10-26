

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import ValidationError

from app import crud
from app.schemas import (
    StudentCreate,
    StudentPage,
    StudentReplace,
    StudentResponse,
    StudentUpdate,
)

router = APIRouter()


@router.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
)
def create_student(student: StudentCreate):
    try:
        return crud.create_student(student.model_dump(mode="json"))
    except crud.DuplicateEmailError:
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists.",
        )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Unable to create student")
        raise HTTPException(
            status_code=500,
            detail="Could not create student. Check server logs.",
        )


@router.get("/students", response_model=StudentPage, tags=["Students"])
def list_students(
    name: str | None = Query(None, max_length=100),
    course: str | None = Query(None, max_length=100),
    email: str | None = Query(None, max_length=254),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return crud.list_students(
        name=name,
        course=course,
        email=email,
        limit=limit,
        offset=offset,
    )


@router.get(
   "/students/{student_id:int}",
    response_model=StudentResponse,
    tags=["Students"],
)
def get_student(student_id: int):
    student = crud.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


@router.put(
   "/students/{student_id:int}",
    response_model=StudentResponse,
    tags=["Students"],
)
def replace_student(student_id: int, student: StudentReplace):
    if crud.get_student(student_id) is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    try:
        return crud.update_student(
            student_id,
            student.model_dump(mode="json"),
        )
    except crud.DuplicateEmailError:
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists.",
        )


@router.patch(
    "/students/{student_id:int}",
    response_model=StudentResponse,
    tags=["Students"],
)
def patch_student(student_id: int, student: StudentUpdate):
    changes = student.model_dump(exclude_unset=True, mode="json")

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update.",
        )

    existing = crud.get_student(student_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Student not found.")

    fields = (
        "name",
        "date_of_birth",
        "email",
        "phone",
        "course",
        "address",
        "enrollment_date",
    )
    merged = {key: existing[key] for key in fields}
    merged.update(changes)

    try:
        validated = StudentReplace.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_context=False),
        )

    try:
        return crud.update_student(
            student_id,
            validated.model_dump(mode="json"),
        )
    except crud.DuplicateEmailError:
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists.",
        )


@router.delete(
   "/students/{student_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Students"],
)
def delete_student(student_id: int):
    if not crud.delete_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
