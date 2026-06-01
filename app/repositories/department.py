from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.employee import EmployeeRepository


class DepartmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, name: str, parent_id: int | None) -> Department:
        department = Department(name=name, parent_id=parent_id)
        self.session.add(department)
        await self.session.flush()
        await self.session.refresh(department)

        return department

    async def get_by_id(self, department_id: int) -> Department | None:
        result = await self.session.execute(
            select(Department).where(Department.id == department_id)
        )

        return result.scalar_one_or_none()

    async def get_children(self, department_id: int) -> list[Department]:
        result = await self.session.execute(
            select(Department).where(Department.parent_id == department_id)
        )

        return list(result.scalars().all())

    async def get_all_descendant_ids(self, department_id: int) -> list[int]:
        cte = (
            select(Department.id)
            .where(Department.id == department_id)
            .cte(name="descendants", recursive=True)
        )
        cte = cte.union_all(
            select(Department.id).where(Department.parent_id == cte.c.id)
        )

        result = await self.session.execute(select(cte.c.id))
        ids = result.scalars().all()

        return [i for i in ids if i != department_id]

    async def update(self, department: Department, **kwargs) -> Department:
        for key, value in kwargs.items():
            setattr(department, key, value)

        await self.session.flush()
        await self.session.refresh(department)

        return department

    async def delete(self, department: Department) -> None:
        children = await self.get_children(department.id)
        for child in children:
            await self.delete(child)
            
        await self.session.delete(department)
        await self.session.flush()

    async def get_with_children(
        self,
        department_id: int,
        depth: int,
        include_employees: bool,
    ) -> Department | None:
        department = await self.get_by_id(department_id)
        if not department:
            return None

        await self._load_children(department, depth, include_employees)

        return department

    async def _load_children(
        self,
        department: Department,
        depth: int,
        include_employees: bool,
    ) -> None:
        if depth <= 0:
            department.children = []
            return

        children = await self.get_children(department.id)

        if include_employees:
            emp_repo = EmployeeRepository(self.session)

            for child in children:
                child.employees = await emp_repo.get_by_department(child.id)

        for child in children:
            await self._load_children(child, depth - 1, include_employees)

        department.children = children
