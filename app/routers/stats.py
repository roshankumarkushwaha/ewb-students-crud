
import csv
import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app import crud

router = APIRouter(tags=["Reports"])


@router.get("/students/export.csv")
def export_csv():
    columns = [
        "id",
        "name",
        "date_of_birth",
        "email",
        "phone",
        "course",
        "address",
        "enrollment_date",
        "created_at",
        "updated_at",
    ]

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=columns,
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(crud.export_students())
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="students.csv"'
        },
    )


@router.get("/stats")
def stats():
    return crud.student_stats()
