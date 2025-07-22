from src.application.dto import TodoListDto
from src.domain import TodoRepository


class ListTodosUseCase:
    """Use case for listing all todos."""

    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def execute(self) -> TodoListDto:
        """Execute the list todos use case."""
        todos = self._repository.find_all()
        return TodoListDto.from_todos(todos)
