from unittest.mock import Mock

from src.application.dto import CreateTodoDto
from src.application.use_cases import CreateTodoUseCase
from src.domain import TodoRepository


def test_create_todo_use_case():
    mock_repository = Mock(spec=TodoRepository)
    use_case = CreateTodoUseCase(mock_repository)

    dto = CreateTodoDto(title="Test Task", priority="high")
    result = use_case.execute(dto)

    mock_repository.save.assert_called_once()
    assert result.title == "Test Task"
