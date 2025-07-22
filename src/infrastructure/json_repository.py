"""JSON file-based implementation of TodoRepository."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.domain.exceptions import RepositoryError, TodoNotFoundError
from src.domain.repository import TodoRepository
from src.domain.todo import Todo
from src.infrastructure.file_handler import FileHandler


class JsonTodoRepository(TodoRepository):
    """JSON file-based implementation of TodoRepository."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_file_exists()

    def save(self, todo: Todo) -> None:
        """Save a todo item to JSON storage."""
        try:
            todos = self._load_all_todos()
            todos[todo.id] = self._todo_to_dict(todo)
            self._save_all_todos(todos)
        except Exception as e:
            raise RepositoryError(f"Failed to save todo: {e}")

    def find_by_id(self, todo_id: str) -> Todo | None:
        """Find a todo item by its ID."""
        try:
            todos = self._load_all_todos()
            if todo_id in todos:
                return self._dict_to_todo(todos[todo_id])
            else:
                return None
        except Exception as e:
            raise RepositoryError(f"Failed to find todo: {e}")

    def find_all(self) -> list[Todo]:
        """Retrieve all todo items."""
        try:
            todos = self._load_all_todos()
            return [self._dict_to_todo(data) for data in todos.values()]
        except Exception as e:
            raise RepositoryError(f"Failed to load todos: {e}")

    def delete(self, todo_id: str) -> bool:
        """Delete a todo item by ID."""
        try:
            todos = self._load_all_todos()
            if todo_id in todos:
                del todos[todo_id]
                self._save_all_todos(todos)
                return True
            else:
                return False
        except Exception as e:
            raise RepositoryError(f"Failed to delete todo: {e}")

    def exists(self, todo_id: str) -> bool:
        """Check if a todo item exists."""
        return self.find_by_id(todo_id) is not None

    def update(self, todo: Todo) -> None:
        """Update an existing todo item."""
        if not self.exists(todo.id):
            raise TodoNotFoundError(todo.id)
        self.save(todo)

    def count(self) -> int:
        """Return the total number of todo items."""
        todos = self._load_all_todos()
        return len(todos)

    def _load_all_todos(self) -> dict[str, dict[str, Any]]:
        """Load all todos from JSON file."""
        if not self.file_path.exists():
            return {}

        try:
            content = self.file_path.read_text(encoding='utf-8')
            if not content.strip():
                return {}
            result = json.loads(content)
            if not isinstance(result, dict):
                raise RepositoryError("Invalid JSON format: expected object")
            else:
                return result
        except json.JSONDecodeError as e:
            raise RepositoryError(f"Invalid JSON format: {e}")

    def _save_all_todos(self, todos: dict[str, dict[str, Any]]) -> None:
        """Save all todos to JSON file."""
        try:
            # Create backup if file exists
            if self.file_path.exists():
                FileHandler.create_backup(self.file_path)

            content = json.dumps(todos, indent=2, ensure_ascii=False)
            FileHandler.safe_write(self.file_path, content)
        except Exception as e:
            raise RepositoryError(f"Failed to write JSON file: {e}")

    def _todo_to_dict(self, todo: Todo) -> dict[str, Any]:
        """Convert Todo object to dictionary."""
        return {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "priority": todo.priority.value,
            "created_at": todo.created_at.isoformat(),
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
        }

    def _dict_to_todo(self, data: dict[str, Any]) -> Todo:
        """Convert dictionary to Todo object."""
        return Todo(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            completed=data["completed"],
            priority=data["priority"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )

    def _ensure_file_exists(self) -> None:
        """Ensure the data directory and file exist."""
        FileHandler.ensure_data_directory(self.file_path.parent)
        if not self.file_path.exists():
            self.file_path.write_text('{}', encoding='utf-8')
