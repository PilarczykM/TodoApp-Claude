"""Tests for JSON repository implementation."""

import tempfile
import unittest.mock
from pathlib import Path

import pytest

from src.domain.exceptions import RepositoryError, TodoNotFoundError
from src.domain.priority import Priority
from src.domain.todo import Todo
from src.infrastructure.json_repository import JsonTodoRepository


class TestJsonTodoRepository:
    """Test cases for JsonTodoRepository."""

    def test_json_repository_save_and_find(self):
        """Test saving and finding a todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            todo = Todo(title="Test Task", priority=Priority.HIGH)
            repo.save(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Test Task"
            assert found_todo.priority == Priority.HIGH

    def test_json_repository_find_all(self):
        """Test finding all todo items."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            todo1 = Todo(title="Task 1")
            todo2 = Todo(title="Task 2")
            repo.save(todo1)
            repo.save(todo2)

            all_todos = repo.find_all()
            assert len(all_todos) == 2

    def test_json_repository_delete(self):
        """Test deleting a todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            todo = Todo(title="Test Task")
            repo.save(todo)

            deleted = repo.delete(todo.id)
            assert deleted is True
            assert repo.find_by_id(todo.id) is None

    def test_json_repository_delete_nonexistent(self):
        """Test deleting a non-existent todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            deleted = repo.delete("nonexistent-id")
            assert deleted is False

    def test_json_repository_persistence(self):
        """Test data persistence between repository instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "todos.json"

            # First repository instance
            repo1 = JsonTodoRepository(file_path)
            todo = Todo(title="Persistent Task")
            repo1.save(todo)

            # Second repository instance (simulating app restart)
            repo2 = JsonTodoRepository(file_path)
            found_todo = repo2.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Persistent Task"

    def test_json_repository_exists(self):
        """Test checking if a todo exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            todo = Todo(title="Test Task")
            repo.save(todo)

            assert repo.exists(todo.id) is True
            assert repo.exists("nonexistent-id") is False

    def test_json_repository_update(self):
        """Test updating an existing todo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            todo = Todo(title="Original Task")
            repo.save(todo)

            # Update the todo
            todo.title = "Updated Task"
            todo.completed = True
            repo.update(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Updated Task"
            assert found_todo.completed is True

    def test_json_repository_update_nonexistent(self):
        """Test updating a non-existent todo raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            todo = Todo(title="Nonexistent Task")
            with pytest.raises(TodoNotFoundError):
                repo.update(todo)

    def test_json_repository_count(self):
        """Test counting todo items."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            assert repo.count() == 0

            todo1 = Todo(title="Task 1")
            todo2 = Todo(title="Task 2")
            repo.save(todo1)
            repo.save(todo2)

            assert repo.count() == 2

    def test_json_repository_save_error_handling(self):
        """Test error handling in save method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")
            todo = Todo(title="Test Task")

            # Mock _save_all_todos to raise exception
            with unittest.mock.patch.object(repo, "_save_all_todos", side_effect=Exception("Save error")):
                with pytest.raises(RepositoryError, match="Failed to save todo"):
                    repo.save(todo)

    def test_json_repository_find_by_id_error_handling(self):
        """Test error handling in find_by_id method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            # Mock _load_all_todos to raise exception
            with unittest.mock.patch.object(repo, "_load_all_todos", side_effect=Exception("Load error")):
                with pytest.raises(RepositoryError, match="Failed to find todo"):
                    repo.find_by_id("test-id")

    def test_json_repository_find_all_error_handling(self):
        """Test error handling in find_all method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            # Mock _load_all_todos to raise exception
            with unittest.mock.patch.object(repo, "_load_all_todos", side_effect=Exception("Load error")):
                with pytest.raises(RepositoryError, match="Failed to load todos"):
                    repo.find_all()

    def test_json_repository_delete_error_handling(self):
        """Test error handling in delete method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            # Mock _load_all_todos to raise exception
            with unittest.mock.patch.object(repo, "_load_all_todos", side_effect=Exception("Load error")):
                with pytest.raises(RepositoryError, match="Failed to delete todo"):
                    repo.delete("test-id")

    def test_json_repository_load_empty_file(self):
        """Test loading from empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "empty.json"
            file_path.write_text("", encoding="utf-8")

            repo = JsonTodoRepository(file_path)
            todos = repo._load_all_todos()
            assert todos == {}

    def test_json_repository_load_invalid_json(self):
        """Test loading from file with invalid JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.json"
            file_path.write_text("not valid json", encoding="utf-8")

            repo = JsonTodoRepository(file_path)
            with pytest.raises(RepositoryError, match="Invalid JSON format"):
                repo._load_all_todos()

    def test_json_repository_load_non_dict_json(self):
        """Test loading from file with JSON that's not a dict."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "list.json"
            file_path.write_text('["not", "a", "dict"]', encoding="utf-8")

            repo = JsonTodoRepository(file_path)
            with pytest.raises(RepositoryError, match="Invalid JSON format: expected object"):
                repo._load_all_todos()

    def test_json_repository_save_error_in_write(self):
        """Test error handling when file write fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = JsonTodoRepository(Path(temp_dir) / "todos.json")

            # Mock FileHandler.safe_write to raise exception
            with unittest.mock.patch(
                "src.infrastructure.json_repository.FileHandler.safe_write", side_effect=Exception("Write error")
            ):
                with pytest.raises(RepositoryError, match="Failed to write JSON file"):
                    repo._save_all_todos({})

    def test_json_repository_load_nonexistent_file(self):
        """Test loading from non-existent file returns empty dict."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "nonexistent.json"
            repo = JsonTodoRepository(file_path)

            # Remove the file that was created during initialization
            file_path.unlink()

            todos = repo._load_all_todos()
            assert todos == {}
