from datetime import UTC, datetime
from uuid import UUID

from ..database.repository import TaskRepository
from ..domain.exceptions import TaskNotFoundError, ValidationError
from ..domain.models import Task, TaskFilters


class TodoService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    async def create_task(
        self, title: str, description: str | None = None, category: str = "General"
    ) -> Task:
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")

        task_data = {
            "title": title.strip(),
            "description": description.strip() if description else None,
            "category": category.strip() or "General",
            "completed": False,
        }

        db_task = await self.repository.create(**task_data)
        return Task.model_validate(db_task)

    async def get_task(self, task_id: UUID) -> Task:
        db_task = await self.repository.get_by_id(task_id)
        if not db_task:
            raise TaskNotFoundError(str(task_id))
        return Task.model_validate(db_task)

    async def get_all_tasks(self, limit: int = 100, offset: int = 0) -> list[Task]:
        db_tasks = await self.repository.get_all(limit=limit, offset=offset)
        return [Task.model_validate(task) for task in db_tasks]

    async def get_filtered_tasks(self, filters: TaskFilters) -> list[Task]:
        db_tasks = await self.repository.get_with_filters(filters)
        return [Task.model_validate(task) for task in db_tasks]

    async def update_task(
        self,
        task_id: UUID,
        title: str | None = None,
        description: str | None = None,
        category: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        update_data = {"updated_at": datetime.now(UTC)}

        if title is not None:
            if not title.strip():
                raise ValidationError("Title cannot be empty")
            update_data["title"] = title.strip()

        if description is not None:
            update_data["description"] = description.strip() if description else None

        if category is not None:
            update_data["category"] = category.strip() or "General"

        if completed is not None:
            update_data["completed"] = completed

        db_task = await self.repository.update(task_id, **update_data)
        return Task.model_validate(db_task)

    async def delete_task(self, task_id: UUID) -> bool:
        return await self.repository.delete(task_id)

    async def mark_completed(self, task_id: UUID) -> Task:
        return await self.update_task(task_id, completed=True)

    async def mark_pending(self, task_id: UUID) -> Task:
        return await self.update_task(task_id, completed=False)

    async def get_categories(self) -> list[str]:
        return await self.repository.get_categories()

    async def get_completed_tasks(self) -> list[Task]:
        filters = TaskFilters(completed=True)
        return await self.get_filtered_tasks(filters)

    async def get_pending_tasks(self) -> list[Task]:
        filters = TaskFilters(completed=False)
        return await self.get_filtered_tasks(filters)

    async def search_tasks(self, query: str, limit: int = 100) -> list[Task]:
        if not query.strip():
            return await self.get_all_tasks(limit=limit)

        filters = TaskFilters(search=query.strip(), limit=limit)
        return await self.get_filtered_tasks(filters)
