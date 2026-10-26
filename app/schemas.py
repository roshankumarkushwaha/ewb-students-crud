"""Pydantic request/response schemas and validation."""
from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class StudentFields(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Asha Sharma"])
    date_of_birth: date = Field(examples=["2005-04-12"])
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=250)
    enrollment_date: date | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank.")
        return value

    @field_validator("phone", "course", "address")
    @classmethod
    def clean_optional_text(cls, value):
        if value is None:
            return None
        return value.strip() or None

    @model_validator(mode="after")
    def validate_dates_and_contact(self):
        today = date.today()
        if self.date_of_birth > today:
            raise ValueError("Date of birth cannot be in the future.")
        if self.enrollment_date and self.enrollment_date > today:
            raise ValueError("Enrollment date cannot be in the future.")
        if self.enrollment_date and self.enrollment_date < self.date_of_birth:
            raise ValueError("Enrollment date cannot be earlier than date of birth.")
        if not self.email and not self.phone:
            raise ValueError("Provide at least one contact method: email or phone.")
        return self

class StudentCreate(StudentFields):
    pass

class StudentReplace(StudentFields):
    pass

class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    course: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=250)
    enrollment_date: date | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank.")
        return value

    @field_validator("phone", "course", "address")
    @classmethod
    def clean_optional_text(cls, value):
        if value is None:
            return None
        return value.strip() or None

    @model_validator(mode="after")
    def validate_patch_dates(self):
        today = date.today()
        if self.date_of_birth and self.date_of_birth > today:
            raise ValueError("Date of birth cannot be in the future.")
        if self.enrollment_date and self.enrollment_date > today:
            raise ValueError("Enrollment date cannot be in the future.")
        if self.date_of_birth and self.enrollment_date and self.enrollment_date < self.date_of_birth:
            raise ValueError("Enrollment date cannot be earlier than date of birth.")
        return self

class StudentResponse(StudentFields):
    id: int
    created_at: str
    updated_at: str
    model_config = ConfigDict(from_attributes=True)

class StudentPage(BaseModel):
    items: list[StudentResponse]
    total: int
    limit: int
    offset: int
