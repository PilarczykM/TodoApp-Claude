"""Domain-specific exceptions for todo application."""


class TodoDomainError(Exception):
    """Base exception for todo domain errors."""

    pass


class TodoNotFoundError(TodoDomainError):
    """Raised when a todo item is not found."""

    def __init__(self, todo_id: str):
        self.todo_id = todo_id
        super().__init__(f"Todo with id '{todo_id}' not found")


class RepositoryError(TodoDomainError):
    """Raised when repository operations fail."""

    def __init__(self, message: str):
        super().__init__(f"Repository operation failed: {message}")


class TodoValidationError(TodoDomainError):
    """Raised when todo validation fails."""

    pass
