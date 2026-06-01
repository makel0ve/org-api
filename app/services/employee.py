from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeResponse

logger = get_logger(__name__)


class EmployeeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.employee_repo = EmployeeRepository(session)
        self.department_repo = DepartmentRepository(session)

    async def create(
        self, department_id: int, data: EmployeeCreate
    ) -> EmployeeResponse:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise HTTPException(
                status_code=404, detail=f"Подразделение {department_id} не найдено"
            )

        employee = await self.employee_repo.create(
            department_id=department_id,
            full_name=data.full_name,
            position=data.position,
            hired_at=data.hired_at,
        )

        logger.info(
            "Employee created: id=%s department_id=%s", employee.id, department_id
        )
        return EmployeeResponse.model_validate(employee)
