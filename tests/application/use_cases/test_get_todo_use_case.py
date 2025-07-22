from unittest.mock import Mock

import pytest

from src.application.use_cases import GetTodoUseCase
from src.domain import Todo, TodoNotFoundError, TodoRepository


def test_get_todo_use_case_success():
    mock_repository = Mock(spec=TodoRepository)
    todo = Todo(title="Test Task", description="Test description")
    mock_repository.find_by_id.return_value = todo

    use_case = GetTodoUseCase(mock_repository)
    result = use_case.execute(todo.id)

    mock_repository.find_by_id.assert_called_once_with(todo.id)
    assert result.id == todo.id
    assert result.title == "Test Task"
    assert result.description == "Test description"


def test_get_todo_use_case_not_found():
    mock_repository = Mock(spec=TodoRepository)
    mock_repository.find_by_id.return_value = None

    use_case = GetTodoUseCase(mock_repository)

    with pytest.raises(TodoNotFoundError):
        use_case.execute("nonexistent-id")
