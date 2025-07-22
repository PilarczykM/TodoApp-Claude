from src.application.dto import TodoResponseDto, UpdateTodoDto
from src.domain import Priority, TodoNotFoundError, TodoRepository


class UpdateTodoUseCase:
    """Use case for updating an existing todo."""

    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def execute(self, todo_id: str, dto: UpdateTodoDto) -> TodoResponseDto:
        """Execute the update todo use case."""
        todo = self._repository.find_by_id(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)

        # Update fields that are provided in DTO
        if dto.title is not None:
            todo.update_title(dto.title)

        if dto.description is not None:
            todo.update_description(dto.description)

        if dto.priority is not None:
            todo.update_priority(Priority(dto.priority))

        if dto.completed is not None:
            if dto.completed:
                todo.mark_completed()
            else:
                todo.mark_incomplete()

        self._repository.update(todo)
        return TodoResponseDto.from_todo(todo)
