from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connection import get_async_session
from ..database.repository import TaskRepository
from ..services.todo_service import TodoService


async def get_task_repository(session: AsyncSession = Depends(get_async_session)) -> TaskRepository:
    return TaskRepository(session)


async def get_todo_service(
    repository: TaskRepository = Depends(get_task_repository),
) -> TodoService:
    return TodoService(repository)
