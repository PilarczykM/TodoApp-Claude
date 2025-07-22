"""Domain-specific exceptions for todo application."""


class TodoDomainError(Exception):
    """Base exception for todo domain errors."""

    pass


class TodoValidationError(TodoDomainError):
    """Raised when todo validation fails."""

    pass


class RepositoryError(TodoDomainError):
    """Base exception for repository operations."""

    pass


class TodoNotFoundError(RepositoryError):
    """Raised when a requested todo item is not found."""

    def __init__(self, todo_id: str):
        super().__init__(f"Todo with ID '{todo_id}' not found")
        self.todo_id = todo_id
