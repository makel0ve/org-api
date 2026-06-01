from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentTree,
    DepartmentUpdate,
)
from app.services.department import DepartmentService


router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
) -> DepartmentResponse:
    service = DepartmentService(db)

    return await service.create(data)


@router.get("/{department_id}", response_model=DepartmentTree)
async def get_department(
    department_id: int,
    depth: int = Query(default=1, ge=1, le=5),
    include_employees: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> DepartmentTree:
    service = DepartmentService(db)

    return await service.get(department_id, depth, include_employees)


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> DepartmentResponse:
    service = DepartmentService(db)

    return await service.update(department_id, data)


@router.delete("/{department_id}", status_code=204)
async def delete_department(
    department_id: int,
    mode: str = Query(..., pattern="^(cascade|reassign)$"),
    reassign_to_department_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = DepartmentService(db)

    await service.delete(department_id, mode, reassign_to_department_id)
