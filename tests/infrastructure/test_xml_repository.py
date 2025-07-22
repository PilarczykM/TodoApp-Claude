"""Tests for XML repository implementation."""

import tempfile
from pathlib import Path

import pytest

from src.domain.exceptions import TodoNotFoundError
from src.domain.priority import Priority
from src.domain.todo import Todo
from src.infrastructure.xml_repository import XmlTodoRepository


class TestXmlTodoRepository:
    """Test cases for XmlTodoRepository."""

    def test_xml_repository_save_and_find(self):
        """Test saving and finding a todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task", priority=Priority.HIGH)
            repo.save(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Test Task"
            assert found_todo.priority == Priority.HIGH

    def test_xml_repository_find_all(self):
        """Test finding all todo items."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo1 = Todo(title="Task 1")
            todo2 = Todo(title="Task 2")
            repo.save(todo1)
            repo.save(todo2)

            all_todos = repo.find_all()
            assert len(all_todos) == 2

    def test_xml_repository_delete(self):
        """Test deleting a todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task")
            repo.save(todo)

            deleted = repo.delete(todo.id)
            assert deleted is True
            assert repo.find_by_id(todo.id) is None

    def test_xml_repository_delete_nonexistent(self):
        """Test deleting a non-existent todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            deleted = repo.delete("nonexistent-id")
            assert deleted is False

    def test_xml_repository_persistence(self):
        """Test data persistence between repository instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "todos.xml"

            # First repository instance
            repo1 = XmlTodoRepository(file_path)
            todo = Todo(title="Persistent Task")
            repo1.save(todo)

            # Second repository instance
            repo2 = XmlTodoRepository(file_path)
            found_todo = repo2.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Persistent Task"

    def test_xml_repository_exists(self):
        """Test checking if a todo exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task")
            repo.save(todo)

            assert repo.exists(todo.id) is True
            assert repo.exists("nonexistent-id") is False

    def test_xml_repository_update(self):
        """Test updating an existing todo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

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

    def test_xml_repository_update_nonexistent(self):
        """Test updating a non-existent todo raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Nonexistent Task")
            with pytest.raises(TodoNotFoundError):
                repo.update(todo)

    def test_xml_repository_count(self):
        """Test counting todo items."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            assert repo.count() == 0

            todo1 = Todo(title="Task 1")
            todo2 = Todo(title="Task 2")
            repo.save(todo1)
            repo.save(todo2)

            assert repo.count() == 2

    def test_xml_repository_with_description(self):
        """Test XML repository with todo that has description."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task", description="Detailed description")
            repo.save(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.description == "Detailed description"
