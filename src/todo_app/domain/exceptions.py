class TodoAppException(Exception):
    """Base exception for TODO application."""

    pass


class TaskNotFoundError(TodoAppException):
    """Raised when a task is not found."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class ValidationError(TodoAppException):
    """Raised when validation fails."""

    pass


class DatabaseError(TodoAppException):
    """Raised when database operations fail."""

    pass
