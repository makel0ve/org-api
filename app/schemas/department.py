from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    parent_id: int | None = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Поле не может быть пустым или состоять из пробелов")

        return v


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    parent_id: int | None = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Поле не может быть пустым или состоять из пробелов")

        return v


class DepartmentResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentTree(BaseModel):
    id: int
    name: str
    parent_id: int | None
    created_at: datetime
    employees: list["EmployeeResponse"] = []
    children: list["DepartmentTree"] = []

    model_config = {"from_attributes": True}


from app.schemas.employee import EmployeeResponse

DepartmentTree.model_rebuild()
