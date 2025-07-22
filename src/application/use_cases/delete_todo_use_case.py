from src.domain import TodoRepository


class DeleteTodoUseCase:
    """Use case for deleting a todo."""

    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def execute(self, todo_id: str) -> bool:
        """Execute the delete todo use case."""
        return self._repository.delete(todo_id)
