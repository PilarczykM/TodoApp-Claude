from src.application.dto import TodoResponseDto
from src.domain import TodoNotFoundError, TodoRepository


class GetTodoUseCase:
    """Use case for getting a todo by ID."""

    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def execute(self, todo_id: str) -> TodoResponseDto:
        """Execute the get todo use case."""
        todo = self._repository.find_by_id(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return TodoResponseDto.from_todo(todo)
