from unittest.mock import AsyncMock

import pytest

from app.models.department import Department


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


@pytest.mark.asyncio
async def test_create_department(client, mock_db):
    dept = make_department()
    mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: None))
    mock_db.refresh = AsyncMock(
        side_effect=lambda obj: (
            setattr(obj, "id", 1) or setattr(obj, "created_at", dept.created_at)
        )
    )

    response = client.post("/api/v1/departments/", json={"name": "Backend"})

    assert response.status_code == 201
    assert response.json()["name"] == "Backend"


@pytest.mark.asyncio
async def test_create_department_empty_name(client, mock_db):
    response = client.post("/api/v1/departments/", json={"name": ""})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_department_whitespace_name(client, mock_db):
    response = client.post("/api/v1/departments/", json={"name": "   "})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_department_not_found(client, mock_db):
    mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: None))

    response = client.get("/api/v1/departments/999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_department_self_parent(client, mock_db):
    dept = make_department()
    mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: dept))

    response = client.patch("/api/v1/departments/1", json={"parent_id": 1})

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_department_reassign_without_target(client, mock_db):
    mock_db.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=lambda: make_department()))
    response = client.delete("/api/v1/departments/1?mode=reassign")
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_department_invalid_mode(client, mock_db):
    response = client.delete("/api/v1/departments/1?mode=invalid")

    assert response.status_code == 422
