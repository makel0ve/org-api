from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, department_id: int, full_name: str, position: str, hired_at
    ) -> Employee:
        employee = Employee(
            department_id=department_id,
            full_name=full_name,
            position=position,
            hired_at=hired_at,
        )
        self.session.add(employee)
        await self.session.flush()
        await self.session.refresh(employee)

        return employee

    async def get_by_id(self, employee_id: int) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )

        return result.scalar_one_or_none()

    async def get_by_department(self, department_id: int) -> list[Employee]:
        result = await self.session.execute(
            select(Employee)
            .where(Employee.department_id == department_id)
            .order_by(Employee.created_at)
        )

        return list(result.scalars().all())

    async def reassign(self, from_department_id: int, to_department_id: int) -> None:
        employees = await self.get_by_department(from_department_id)
        for employee in employees:
            employee.department_id = to_department_id

        await self.session.flush()
