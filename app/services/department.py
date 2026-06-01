from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentTree,
    DepartmentUpdate,
)

logger = get_logger(__name__)


class DepartmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.department_repo = DepartmentRepository(session)
        self.employee_repo = EmployeeRepository(session)

    async def create(self, data: DepartmentCreate) -> DepartmentResponse:
        if data.parent_id is not None:
            parent = await self.department_repo.get_by_id(data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=404, detail=f"Подразделение {data.parent_id} не найдено"
                )

        department = await self.department_repo.create(
            name=data.name,
            parent_id=data.parent_id,
        )

        logger.info("Department created: id=%s name=%r", department.id, department.name)
        return DepartmentResponse.model_validate(department)

    async def get(
        self,
        department_id: int,
        depth: int,
        include_employees: bool,
    ) -> DepartmentTree:
        department = await self.department_repo.get_with_children(
            department_id=department_id,
            depth=depth,
            include_employees=include_employees,
        )
        if not department:
            raise HTTPException(
                status_code=404, detail=f"Подразделение {department_id} не найдено"
            )

        if include_employees:
            department.employees = await self.employee_repo.get_by_department(
                department_id
            )

        else:
            department.employees = []

        logger.info("Department fetched: id=%s depth=%s", department_id, depth)
        return DepartmentTree.model_validate(department)

    async def update(
        self, department_id: int, data: DepartmentUpdate
    ) -> DepartmentResponse:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise HTTPException(
                status_code=404, detail=f"Подразделение {department_id} не найдено"
            )

        if data.parent_id is not None and data.parent_id == department_id:
            raise HTTPException(
                status_code=409,
                detail="Подразделение не может быть родителем самого себя",
            )

        if data.parent_id is not None:
            descendant_ids = await self.department_repo.get_all_descendant_ids(
                department_id
            )
            if data.parent_id in descendant_ids:
                raise HTTPException(
                    status_code=409,
                    detail="Нельзя переместить подразделение внутрь своего поддерева",
                )

            parent = await self.department_repo.get_by_id(data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=404, detail=f"Подразделение {data.parent_id} не найдено"
                )

        update_data = data.model_dump(exclude_unset=True)
        department = await self.department_repo.update(department, **update_data)

        logger.info("Department updated: id=%s", department_id)
        return DepartmentResponse.model_validate(department)

    async def delete(
        self, department_id: int, mode: str, reassign_to_department_id: int | None
    ) -> None:
        department = await self.department_repo.get_by_id(department_id)
        if not department:
            raise HTTPException(
                status_code=404, detail=f"Подразделение {department_id} не найдено"
            )

        if mode == "reassign":
            if reassign_to_department_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="reassign_to_department_id обязателен при mode=reassign",
                )

            if reassign_to_department_id == department_id:
                raise HTTPException(
                    status_code=400,
                    detail="Нельзя перевести сотрудников в удаляемое подразделение",
                )

            target = await self.department_repo.get_by_id(reassign_to_department_id)
            if not target:
                raise HTTPException(
                    status_code=404,
                    detail=f"Подразделение {reassign_to_department_id} не найдено",
                )

            await self.employee_repo.reassign(
                from_department_id=department_id,
                to_department_id=reassign_to_department_id,
            )

        await self.department_repo.delete(department)
        logger.info("Department deleted: id=%s mode=%s", department_id, mode)
