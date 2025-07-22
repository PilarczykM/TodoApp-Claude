
import pytest
from pydantic import ValidationError

from src.domain.priority import Priority
from src.domain.todo import Todo


class TestTodo:
    def test_todo_creation(self):
        todo = Todo(
            title="Test task",
            description="Test description",
            priority=Priority.HIGH
        )
        assert todo.title == "Test task"
        assert todo.description == "Test description"
        assert todo.priority == Priority.HIGH
        assert todo.completed is False
        assert todo.id is not None
        assert todo.created_at is not None

    def test_todo_completion_toggle(self):
        todo = Todo(title="Test")
        todo.mark_completed()
        assert todo.completed is True
        assert todo.updated_at is not None

    def test_todo_validation(self):
        with pytest.raises(ValidationError):
            Todo(title="")  # Empty title should fail
