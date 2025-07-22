from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from src.domain import Priority, Todo


class CreateTodoDto(BaseModel):
    """DTO for creating a new todo."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: str = Field(default="medium")

    @field_validator('title')
    def validate_title(cls, v):
        """Validate title field."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    @field_validator('priority')
    def validate_priority(cls, v):
        """Validate priority field."""
        if v not in [p.value for p in Priority]:
            raise ValueError(f'Priority must be one of: {[p.value for p in Priority]}')
        return v

    def to_domain(self) -> Todo:
        """Convert DTO to domain entity."""
        return Todo(
            title=self.title,
            description=self.description,
            priority=Priority(self.priority)
        )


class UpdateTodoDto(BaseModel):
    """DTO for updating an existing todo."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    priority: str | None = None
    completed: bool | None = None

    @field_validator('title')
    def validate_title(cls, v):
        """Validate title field."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip() if v else v

    @field_validator('priority')
    def validate_priority(cls, v):
        """Validate priority field."""
        if v is not None and v not in [p.value for p in Priority]:
            raise ValueError(f'Priority must be one of: {[p.value for p in Priority]}')
        return v


class TodoResponseDto(BaseModel):
    """DTO for todo responses."""

    id: str
    title: str
    description: str | None
    completed: bool
    priority: str
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_todo(cls, todo: Todo) -> 'TodoResponseDto':
        """Create DTO from domain entity."""
        return cls(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            priority=todo.priority.value,
            created_at=todo.created_at,
            updated_at=todo.updated_at
        )


class TodoListDto(BaseModel):
    """DTO for todo list responses."""

    todos: list[TodoResponseDto]
    total_count: int
    completed_count: int
    pending_count: int

    @classmethod
    def from_todos(cls, todos: list[Todo]) -> 'TodoListDto':
        """Create DTO from list of domain entities."""
        todo_dtos = [TodoResponseDto.from_todo(todo) for todo in todos]
        completed_count = sum(1 for todo in todos if todo.completed)

        return cls(
            todos=todo_dtos,
            total_count=len(todos),
            completed_count=completed_count,
            pending_count=len(todos) - completed_count
        )
