from unittest.mock import AsyncMock

import pytest

from app.models.department import Department
from app.models.employee import Employee


def make_department(**kwargs) -> Department:
    defaults = {
        "id": 1,
        "name": "Backend",
        "parent_id": None,
        "created_at": "2026-01-01T00:00:00",
    }
    defaults.update(kwargs)
    dept = Department()
    for k, v in defaults.items():
        setattr(dept, k, v)

    return dept


def make_employee(**kwargs) -> Employee:
    defaults = {
        "id": 1,
        "department_id": 1,
        "full_name": "Иван Иванов",
        "position": "Developer",
        "hired_at": None,
        "created_at": "2026-01-01T00:00:00",
    }
    defaults.update(kwargs)
    emp = Employee()
    for k, v in defaults.items():
        setattr(emp, k, v)

    return emp


@pytest.mark.asyncio
async def test_create_employee(client, mock_db):
    dept = make_department()
    emp = make_employee()
    mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: dept))
    mock_db.refresh = AsyncMock(
        side_effect=lambda obj: (
            setattr(obj, "id", 1) or setattr(obj, "created_at", emp.created_at)
        )
    )

    response = client.post(
        "/api/v1/departments/1/employees/",
        json={
            "full_name": "Иван Иванов",
            "position": "Developer",
        },
    )

    assert response.status_code == 201
    assert response.json()["full_name"] == "Иван Иванов"
    assert response.json()["position"] == "Developer"


@pytest.mark.asyncio
async def test_create_employee_department_not_found(client, mock_db):
    mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: None))

    response = client.post(
        "/api/v1/departments/999/employees/",
        json={
            "full_name": "Иван Иванов",
            "position": "Developer",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_employee_empty_full_name(client, mock_db):
    response = client.post(
        "/api/v1/departments/1/employees/",
        json={
            "full_name": "",
            "position": "Developer",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_employee_whitespace_position(client, mock_db):
    response = client.post(
        "/api/v1/departments/1/employees/",
        json={
            "full_name": "Иван Иванов",
            "position": "   ",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_employee_with_hired_at(client, mock_db):
    dept = make_department()
    emp = make_employee(hired_at="2024-01-15")
    mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: dept))
    mock_db.refresh = AsyncMock(
        side_effect=lambda obj: (
            setattr(obj, "id", 1) or setattr(obj, "created_at", emp.created_at)
        )
    )

    response = client.post(
        "/api/v1/departments/1/employees/",
        json={
            "full_name": "Иван Иванов",
            "position": "Developer",
            "hired_at": "2024-01-15",
        },
    )

    assert response.status_code == 201
    assert response.json()["hired_at"] == "2024-01-15"


@pytest.mark.asyncio
async def test_create_employee_missing_position(client, mock_db):
    response = client.post(
        "/api/v1/departments/1/employees/",
        json={
            "full_name": "Иван Иванов",
        },
    )

    assert response.status_code == 422
