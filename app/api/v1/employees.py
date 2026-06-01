from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.services.employee import EmployeeService


router = APIRouter(prefix="/departments", tags=["employees"])


@router.post(
    "/{department_id}/employees/", response_model=EmployeeResponse, status_code=201
)
async def create_employee(
    department_id: int,
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
) -> EmployeeResponse:
    service = EmployeeService(db)

    return await service.create(department_id, data)
