"""Tests for JSON repository implementation."""

import tempfile
import json
from pathlib import Path
import pytest

from src.domain.todo import Todo
from src.domain.priority import Priority
from src.domain.exceptions import TodoNotFoundError
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