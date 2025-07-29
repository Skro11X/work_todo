from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.tasks.router import router as tasks_router
from app.files.router import router as files_router


router = APIRouter()


# Маршрут для главной страницы
@router.get("/")
async def read_index():
    return FileResponse("static/index.html")


router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
router.include_router(files_router, prefix="/files", tags=["Files"])
