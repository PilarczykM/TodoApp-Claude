from unittest.mock import Mock

from src.application.use_cases import DeleteTodoUseCase
from src.domain import TodoRepository


def test_delete_todo_use_case_success():
    mock_repository = Mock(spec=TodoRepository)
    mock_repository.delete.return_value = True

    use_case = DeleteTodoUseCase(mock_repository)
    result = use_case.execute("test-id")

    mock_repository.delete.assert_called_once_with("test-id")
    assert result is True


def test_delete_todo_use_case_not_found():
    mock_repository = Mock(spec=TodoRepository)
    mock_repository.delete.return_value = False

    use_case = DeleteTodoUseCase(mock_repository)
    result = use_case.execute("nonexistent-id")

    mock_repository.delete.assert_called_once_with("nonexistent-id")
    assert result is False
