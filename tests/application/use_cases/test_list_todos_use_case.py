from unittest.mock import Mock

from src.application.use_cases import ListTodosUseCase
from src.domain import Todo, TodoRepository


def test_list_todos_use_case_with_todos():
    mock_repository = Mock(spec=TodoRepository)
    todos = [
        Todo(title="Task 1", completed=False),
        Todo(title="Task 2", completed=True),
        Todo(title="Task 3", completed=False)
    ]
    mock_repository.find_all.return_value = todos

    use_case = ListTodosUseCase(mock_repository)
    result = use_case.execute()

    mock_repository.find_all.assert_called_once()
    assert result.total_count == 3
    assert result.completed_count == 1
    assert result.pending_count == 2
    assert len(result.todos) == 3
    assert result.todos[0].title == "Task 1"


def test_list_todos_use_case_empty():
    mock_repository = Mock(spec=TodoRepository)
    mock_repository.find_all.return_value = []

    use_case = ListTodosUseCase(mock_repository)
    result = use_case.execute()

    mock_repository.find_all.assert_called_once()
    assert result.total_count == 0
    assert result.completed_count == 0
    assert result.pending_count == 0
    assert len(result.todos) == 0
