from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from .exceptions import TodoValidationError
from .priority import Priority


class Todo(BaseModel):
    """Todo domain entity representing a task."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(max_length=200)
    description: str | None = Field(None, max_length=1000)
    completed: bool = False
    priority: Priority = Priority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean the title field."""
        if not v.strip():
            raise TodoValidationError('Title cannot be empty or whitespace')
        return v.strip()

    def mark_completed(self) -> None:
        """Mark the todo as completed."""
        self.completed = True
        self.updated_at = datetime.now()

    def mark_incomplete(self) -> None:
        """Mark the todo as incomplete."""
        self.completed = False
        self.updated_at = datetime.now()

    def update_title(self, new_title: str) -> None:
        """Update the todo title."""
        self.title = new_title
        self.updated_at = datetime.now()

    def update_description(self, new_description: str | None) -> None:
        """Update the todo description."""
        self.description = new_description
        self.updated_at = datetime.now()

    def update_priority(self, new_priority: Priority) -> None:
        """Update the todo priority."""
        self.priority = new_priority
        self.updated_at = datetime.now()
