
import pytest

from src.domain.exceptions import TodoValidationError
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
        with pytest.raises(TodoValidationError):
            Todo(title="")  # Empty title should fail

    def test_mark_incomplete(self):
        todo = Todo(title="Test")
        todo.mark_completed()
        assert todo.completed is True

        todo.mark_incomplete()
        assert todo.completed is False
        assert todo.updated_at is not None

    def test_update_title(self):
        todo = Todo(title="Original")
        original_updated_at = todo.updated_at

        todo.update_title("New Title")
        assert todo.title == "New Title"
        assert todo.updated_at != original_updated_at

    def test_update_description(self):
        todo = Todo(title="Test", description="Original")
        original_updated_at = todo.updated_at

        todo.update_description("New Description")
        assert todo.description == "New Description"
        assert todo.updated_at != original_updated_at

    def test_update_priority(self):
        todo = Todo(title="Test", priority=Priority.LOW)
        original_updated_at = todo.updated_at

        todo.update_priority(Priority.HIGH)
        assert todo.priority == Priority.HIGH
        assert todo.updated_at != original_updated_at
