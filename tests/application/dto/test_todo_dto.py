import pytest
from pydantic import ValidationError

from src.application.dto import CreateTodoDto, TodoResponseDto, UpdateTodoDto
from src.domain import Priority, Todo


def test_create_todo_dto():
    dto = CreateTodoDto(
        title="Test Task",
        description="Test description",
        priority="high"
    )
    assert dto.title == "Test Task"
    assert dto.description == "Test description"
    assert dto.priority == "high"


def test_create_todo_dto_validation():
    with pytest.raises(ValidationError):
        CreateTodoDto(title="")  # Empty title

    with pytest.raises(ValidationError):
        CreateTodoDto(title="Test", priority="invalid")  # Invalid priority


def test_update_todo_dto():
    dto = UpdateTodoDto(
        title="Updated Task",
        description="Updated description",
        priority="low",
        completed=True
    )
    assert dto.title == "Updated Task"
    assert dto.completed is True


def test_todo_response_dto_from_todo():
    todo = Todo(title="Test Task", priority=Priority.HIGH)
    dto = TodoResponseDto.from_todo(todo)

    assert dto.id == todo.id
    assert dto.title == todo.title
    assert dto.priority == "high"
    assert dto.completed is False
