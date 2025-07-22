import re

from src.domain import Priority, TodoValidationError


class ValidationService:
    """Service for input validation."""

    @staticmethod
    def validate_title(title: str) -> None:
        """Validate todo title."""
        if not title or not title.strip():
            raise TodoValidationError("Title cannot be empty")

        if len(title.strip()) > 200:
            raise TodoValidationError("Title cannot exceed 200 characters")

    @staticmethod
    def validate_description(description: str | None) -> None:
        """Validate todo description."""
        if description and len(description) > 1000:
            raise TodoValidationError("Description cannot exceed 1000 characters")

    @staticmethod
    def validate_priority(priority: str) -> None:
        """Validate priority value."""
        if priority not in [p.value for p in Priority]:
            valid_priorities = [p.value for p in Priority]
            raise TodoValidationError(f"Priority must be one of: {valid_priorities}")

    @staticmethod
    def validate_todo_id(todo_id: str) -> None:
        """Validate todo ID format."""
        if not todo_id or not todo_id.strip():
            raise TodoValidationError("Todo ID cannot be empty")

        # UUID format validation
        uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        if not re.match(uuid_pattern, todo_id.strip()):
            raise TodoValidationError("Invalid todo ID format")
