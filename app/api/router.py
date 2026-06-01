from fastapi import APIRouter

from app.api.v1.departments import router as departments_router
from app.api.v1.employees import router as employees_router


router = APIRouter(prefix="/api/v1")


router.include_router(departments_router)
router.include_router(employees_router)
