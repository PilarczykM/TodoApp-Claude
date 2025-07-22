from src.application.dto import CreateTodoDto, TodoListDto, TodoResponseDto, UpdateTodoDto
from src.domain import Priority, TodoNotFoundError, TodoRepository


class TodoService:
    """Application service for todo operations."""

    def __init__(self, repository: TodoRepository):
        self._repository = repository

    def create_todo(self, dto: CreateTodoDto) -> TodoResponseDto:
        """Create a new todo item."""
        todo = dto.to_domain()
        self._repository.save(todo)
        return TodoResponseDto.from_todo(todo)

    def get_todo_by_id(self, todo_id: str) -> TodoResponseDto:
        """Get a todo item by its ID."""
        todo = self._repository.find_by_id(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return TodoResponseDto.from_todo(todo)

    def get_all_todos(self) -> TodoListDto:
        """Get all todo items."""
        todos = self._repository.find_all()
        return TodoListDto.from_todos(todos)

    def update_todo(self, todo_id: str, dto: UpdateTodoDto) -> TodoResponseDto:
        """Update an existing todo item."""
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

    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo item."""
        return self._repository.delete(todo_id)

    def toggle_completion(self, todo_id: str) -> TodoResponseDto:
        """Toggle completion status of a todo item."""
        todo = self._repository.find_by_id(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)

        if todo.completed:
            todo.mark_incomplete()
        else:
            todo.mark_completed()

        self._repository.update(todo)
        return TodoResponseDto.from_todo(todo)

    def get_todos_by_status(self, completed: bool) -> TodoListDto:
        """Get todos filtered by completion status."""
        all_todos = self._repository.find_all()
        filtered_todos = [todo for todo in all_todos if todo.completed == completed]
        return TodoListDto.from_todos(filtered_todos)

    def get_todos_by_priority(self, priority: Priority) -> TodoListDto:
        """Get todos filtered by priority."""
        all_todos = self._repository.find_all()
        filtered_todos = [todo for todo in all_todos if todo.priority == priority]
        return TodoListDto.from_todos(filtered_todos)

    def get_statistics(self) -> dict:
        """Get statistics about todos."""
        all_todos = self._repository.find_all()

        return {
            "total_count": len(all_todos),
            "completed_count": sum(1 for todo in all_todos if todo.completed),
            "pending_count": sum(1 for todo in all_todos if not todo.completed),
            "by_priority": {
                priority.value: sum(1 for todo in all_todos if todo.priority == priority)
                for priority in Priority
            }
        }
