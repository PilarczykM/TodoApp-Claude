from unittest.mock import Mock

import pytest

from src.application import CreateTodoDto, TodoService, UpdateTodoDto
from src.domain import Todo, TodoNotFoundError, TodoRepository


@pytest.fixture
def mock_repository():
    return Mock(spec=TodoRepository)


@pytest.fixture
def todo_service(mock_repository):
    return TodoService(mock_repository)


def test_create_todo(todo_service, mock_repository):
    dto = CreateTodoDto(title="Test Task", priority="high")

    result = todo_service.create_todo(dto)

    mock_repository.save.assert_called_once()
    assert result.title == "Test Task"
    assert result.priority == "high"
    assert result.completed is False


def test_get_todo_by_id(todo_service, mock_repository):
    todo = Todo(title="Test Task")
    mock_repository.find_by_id.return_value = todo

    result = todo_service.get_todo_by_id(todo.id)

    mock_repository.find_by_id.assert_called_once_with(todo.id)
    assert result.title == "Test Task"


def test_get_todo_by_id_not_found(todo_service, mock_repository):
    mock_repository.find_by_id.return_value = None

    with pytest.raises(TodoNotFoundError):
        todo_service.get_todo_by_id("nonexistent")


def test_update_todo(todo_service, mock_repository):
    todo = Todo(title="Original Task")
    mock_repository.find_by_id.return_value = todo
    mock_repository.exists.return_value = True

    update_dto = UpdateTodoDto(title="Updated Task", completed=True)
    result = todo_service.update_todo(todo.id, update_dto)

    mock_repository.update.assert_called_once()
    assert result.title == "Updated Task"
    assert result.completed is True


def test_delete_todo(todo_service, mock_repository):
    mock_repository.delete.return_value = True

    result = todo_service.delete_todo("test-id")

    mock_repository.delete.assert_called_once_with("test-id")
    assert result is True


def test_get_all_todos(todo_service, mock_repository):
    todos = [
        Todo(title="Task 1"),
        Todo(title="Task 2", completed=True)
    ]
    mock_repository.find_all.return_value = todos

    result = todo_service.get_all_todos()

    mock_repository.find_all.assert_called_once()
    assert result.total_count == 2
    assert result.completed_count == 1
    assert result.pending_count == 1


def test_toggle_completion(todo_service, mock_repository):
    todo = Todo(title="Test Task", completed=False)
    mock_repository.find_by_id.return_value = todo
    mock_repository.exists.return_value = True

    result = todo_service.toggle_completion(todo.id)

    mock_repository.update.assert_called_once()
    assert result.completed is True
