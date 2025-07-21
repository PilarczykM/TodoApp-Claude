from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.exceptions import DatabaseError, TaskNotFoundError
from ..domain.models import TaskFilters
from .models import Base, TaskORM

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        self.session = session
        self.model_class = model_class

    async def create(self, **kwargs: object) -> T:
        try:
            instance = self.model_class(**kwargs)
            self.session.add(instance)
            await self.session.flush()
            await self.session.refresh(instance)
            return instance
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to create {self.model_class.__name__}: {e}") from e

    async def get_by_id(self, id_value: UUID) -> T | None:
        try:
            result = await self.session.execute(
                select(self.model_class).where(self.model_class.id == id_value)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseError(f"Failed to get {self.model_class.__name__} by id: {e}") from e

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        try:
            result = await self.session.execute(
                select(self.model_class).offset(offset).limit(limit)
            )
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(f"Failed to get all {self.model_class.__name__}: {e}") from e

    async def update(self, id_value: UUID, **kwargs: object) -> T:
        try:
            instance = await self.get_by_id(id_value)
            if not instance:
                raise TaskNotFoundError(str(id_value))

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            await self.session.flush()
            await self.session.refresh(instance)
            return instance
        except TaskNotFoundError:
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to update {self.model_class.__name__}: {e}") from e

    async def delete(self, id_value: UUID) -> bool:
        try:
            instance = await self.get_by_id(id_value)
            if not instance:
                return False

            await self.session.delete(instance)
            await self.session.flush()
            return True
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to delete {self.model_class.__name__}: {e}") from e


class TaskRepository(BaseRepository[TaskORM]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TaskORM)

    async def get_with_filters(self, filters: TaskFilters) -> list[TaskORM]:
        try:
            query = select(self.model_class)
            conditions = []

            if filters.category:
                conditions.append(self.model_class.category == filters.category)

            if filters.completed is not None:
                conditions.append(self.model_class.completed == filters.completed)

            if filters.search:
                search_term = f"%{filters.search}%"
                conditions.append(
                    or_(
                        self.model_class.title.ilike(search_term),
                        self.model_class.description.ilike(search_term),
                    )
                )

            if conditions:
                query = query.where(and_(*conditions))

            query = query.offset(filters.offset).limit(filters.limit)

            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks with filters: {e}") from e

    async def get_categories(self) -> list[str]:
        try:
            result = await self.session.execute(select(self.model_class.category).distinct())
            return [category for category in result.scalars().all() if category]
        except Exception as e:
            raise DatabaseError(f"Failed to get categories: {e}") from e
