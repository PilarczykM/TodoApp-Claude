import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.connection import get_async_session
from ...domain.exceptions import TaskNotFoundError, ValidationError
from ...domain.models import TaskFilters
from ...services.todo_service import TodoService
from ..dependencies import get_todo_service
from ..schemas import (
    ErrorResponse,
    MessageResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task with title, optional description and category",
    responses={
        201: {"description": "Task created successfully"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_task(
    task_data: TaskCreate,
    service: TodoService = Depends(get_todo_service),
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponse:
    try:
        async with session.begin():
            task = await service.create_task(
                title=task_data.title,
                description=task_data.description,
                category=task_data.category,
            )
            return TaskResponse.model_validate(task)
    except ValidationError as e:
        logger.warning(f"Task creation validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Unexpected error creating task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/",
    response_model=list[TaskResponse],
    summary="Get all tasks",
    description="Retrieve all tasks with optional filtering",
    responses={
        200: {"description": "Tasks retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_tasks(
    category: str | None = Query(None, description="Filter by category"),
    completed: bool | None = Query(None, description="Filter by completion status"),
    search: str | None = Query(None, description="Search in title and description"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    service: TodoService = Depends(get_todo_service),
) -> list[TaskResponse]:
    try:
        filters = TaskFilters(
            category=category, completed=completed, search=search, limit=limit, offset=offset
        )
        tasks = await service.get_filtered_tasks(filters)
        return [TaskResponse.model_validate(task) for task in tasks]
    except Exception:
        logger.exception("Unexpected error retrieving tasks")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID",
    description="Retrieve a specific task by its ID",
    responses={
        200: {"description": "Task retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_task(task_id: UUID, service: TodoService = Depends(get_todo_service)) -> TaskResponse:
    try:
        task = await service.get_task(task_id)
        return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        logger.warning(f"Task not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception("Unexpected error retrieving task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task",
    description="Update a task with new data",
    responses={
        200: {"description": "Task updated successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    service: TodoService = Depends(get_todo_service),
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponse:
    try:
        async with session.begin():
            task = await service.update_task(
                task_id=task_id,
                title=task_data.title,
                description=task_data.description,
                category=task_data.category,
                completed=task_data.completed,
            )
            return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        logger.warning(f"Task not found for update: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Task update validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Unexpected error updating task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
    summary="Delete task",
    description="Delete a task by its ID",
    responses={
        200: {"description": "Task deleted successfully"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_task(
    task_id: UUID,
    service: TodoService = Depends(get_todo_service),
    session: AsyncSession = Depends(get_async_session),
) -> MessageResponse:
    try:
        async with session.begin():
            deleted = await service.delete_task(task_id)
            if not deleted:
                raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
            return MessageResponse(message=f"Task {task_id} deleted successfully")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error deleting task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Mark task as completed",
    description="Mark a specific task as completed",
    responses={
        200: {"description": "Task marked as completed"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def complete_task(
    task_id: UUID,
    service: TodoService = Depends(get_todo_service),
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponse:
    try:
        async with session.begin():
            task = await service.mark_completed(task_id)
            return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        logger.warning(f"Task not found for completion: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception("Unexpected error completing task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch(
    "/{task_id}/uncomplete",
    response_model=TaskResponse,
    summary="Mark task as pending",
    description="Mark a specific task as pending (not completed)",
    responses={
        200: {"description": "Task marked as pending"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def uncomplete_task(
    task_id: UUID,
    service: TodoService = Depends(get_todo_service),
    session: AsyncSession = Depends(get_async_session),
) -> TaskResponse:
    try:
        async with session.begin():
            task = await service.mark_pending(task_id)
            return TaskResponse.model_validate(task)
    except TaskNotFoundError as e:
        logger.warning(f"Task not found for uncommpletion: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception("Unexpected error uncompleting task")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/categories/",
    response_model=list[str],
    summary="Get all categories",
    description="Retrieve all unique task categories",
    responses={
        200: {"description": "Categories retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_categories(service: TodoService = Depends(get_todo_service)) -> list[str]:
    try:
        return await service.get_categories()
    except Exception:
        logger.exception("Unexpected error retrieving categories")
        raise HTTPException(status_code=500, detail="Internal server error")
