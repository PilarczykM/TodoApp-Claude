import pytest
from pydantic import ValidationError

from src.application.dto import CreateTodoDto, TodoListDto, TodoResponseDto, UpdateTodoDto
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


def test_create_todo_dto_defaults():
    dto = CreateTodoDto(title="Test Task")
    assert dto.title == "Test Task"
    assert dto.description is None
    assert dto.priority == "medium"


def test_create_todo_dto_to_domain():
    dto = CreateTodoDto(
        title="Test Task",
        description="Test description",
        priority="low"
    )
    todo = dto.to_domain()

    assert todo.title == "Test Task"
    assert todo.description == "Test description"
    assert todo.priority == Priority.LOW
    assert todo.completed is False


def test_update_todo_dto_validation_empty_title():
    with pytest.raises(ValidationError):
        UpdateTodoDto(title="   ")  # Whitespace only


def test_update_todo_dto_all_none():
    dto = UpdateTodoDto()
    assert dto.title is None
    assert dto.description is None
    assert dto.priority is None
    assert dto.completed is None


def test_todo_list_dto_from_todos():
    todos = [
        Todo(title="Task 1", completed=False),
        Todo(title="Task 2", completed=True),
        Todo(title="Task 3", completed=False)
    ]

    dto = TodoListDto.from_todos(todos)

    assert dto.total_count == 3
    assert dto.completed_count == 1
    assert dto.pending_count == 2
    assert len(dto.todos) == 3


def test_todo_list_dto_empty():
    dto = TodoListDto.from_todos([])

    assert dto.total_count == 0
    assert dto.completed_count == 0
    assert dto.pending_count == 0
    assert len(dto.todos) == 0
