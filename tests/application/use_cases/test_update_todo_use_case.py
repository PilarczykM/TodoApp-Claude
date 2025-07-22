from unittest.mock import Mock

import pytest

from src.application.dto import UpdateTodoDto
from src.application.use_cases import UpdateTodoUseCase
from src.domain import Todo, TodoNotFoundError, TodoRepository


def test_update_todo_use_case_success():
    mock_repository = Mock(spec=TodoRepository)
    todo = Todo(title="Original Task", description="Original description")
    mock_repository.find_by_id.return_value = todo

    use_case = UpdateTodoUseCase(mock_repository)
    update_dto = UpdateTodoDto(title="Updated Task", description="Updated description", priority="high", completed=True)

    result = use_case.execute(todo.id, update_dto)

    mock_repository.find_by_id.assert_called_once_with(todo.id)
    mock_repository.update.assert_called_once_with(todo)
    assert result.title == "Updated Task"
    assert result.description == "Updated description"
    assert result.priority == "high"
    assert result.completed is True


def test_update_todo_use_case_partial_update():
    mock_repository = Mock(spec=TodoRepository)
    todo = Todo(title="Original Task", completed=False)
    mock_repository.find_by_id.return_value = todo

    use_case = UpdateTodoUseCase(mock_repository)
    update_dto = UpdateTodoDto(title="Updated Task")

    result = use_case.execute(todo.id, update_dto)

    assert result.title == "Updated Task"
    assert result.completed is False  # Unchanged


def test_update_todo_use_case_not_found():
    mock_repository = Mock(spec=TodoRepository)
    mock_repository.find_by_id.return_value = None

    use_case = UpdateTodoUseCase(mock_repository)
    update_dto = UpdateTodoDto(title="Updated Task")

    with pytest.raises(TodoNotFoundError):
        use_case.execute("nonexistent-id", update_dto)
