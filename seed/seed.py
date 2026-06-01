"""
Данный файл служит наполнение БД тестовыми данными

Файл был написан не лично, а при помощи ИИ

Для запуска рекомендуется использовать команду:
docker exec -it org_api_app sh -c "PYTHONPATH=/code python seed/seed.py" 
"""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.department import Department
from app.models.employee import Employee


async def seed(session: AsyncSession) -> None:
    # Корневые департаменты
    it = Department(name="IT")
    hr = Department(name="HR")
    finance = Department(name="Finance")
    session.add_all([it, hr, finance])
    await session.flush()

    # Дочерние департаменты IT
    backend = Department(name="Backend", parent_id=it.id)
    frontend = Department(name="Frontend", parent_id=it.id)
    devops = Department(name="DevOps", parent_id=it.id)
    session.add_all([backend, frontend, devops])
    await session.flush()

    # Дочерние департаменты Backend
    python_team = Department(name="Python", parent_id=backend.id)
    go_team = Department(name="Go", parent_id=backend.id)
    session.add_all([python_team, go_team])
    await session.flush()

    # Сотрудники IT
    session.add_all([
        Employee(department_id=it.id, full_name="Алексей Смирнов", position="CTO"),
    ])

    # Сотрудники Backend
    session.add_all([
        Employee(department_id=backend.id, full_name="Иван Иванов", position="Team Lead"),
        Employee(department_id=backend.id, full_name="Мария Петрова", position="Senior Developer"),
    ])

    # Сотрудники Python
    session.add_all([
        Employee(department_id=python_team.id, full_name="Дмитрий Козлов", position="Middle Developer"),
        Employee(department_id=python_team.id, full_name="Анна Сидорова", position="Junior Developer"),
    ])

    # Сотрудники Frontend
    session.add_all([
        Employee(department_id=frontend.id, full_name="Сергей Новиков", position="Team Lead"),
        Employee(department_id=frontend.id, full_name="Екатерина Морозова", position="Middle Developer"),
    ])

    # Сотрудники DevOps
    session.add_all([
        Employee(department_id=devops.id, full_name="Павел Волков", position="DevOps Engineer"),
    ])

    # Сотрудники HR
    session.add_all([
        Employee(department_id=hr.id, full_name="Ольга Федорова", position="HR Manager"),
        Employee(department_id=hr.id, full_name="Наталья Михайлова", position="HR Specialist"),
    ])

    # Сотрудники Finance
    session.add_all([
        Employee(department_id=finance.id, full_name="Андрей Белов", position="CFO"),
        Employee(department_id=finance.id, full_name="Юлия Тихонова", position="Accountant"),
    ])

    await session.commit()
    print("✅ База заполнена тестовыми данными")


async def main() -> None:
    async with async_session() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())