from src.application.dto import CreateTodoDto, TodoResponseDto
from src.domain import TodoRepository


class CreateTodoUseCase:
    """Use case for creating a new todo."""

    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def execute(self, dto: CreateTodoDto) -> TodoResponseDto:
        """Execute the create todo use case."""
        todo = dto.to_domain()
        self._repository.save(todo)
        return TodoResponseDto.from_todo(todo)
