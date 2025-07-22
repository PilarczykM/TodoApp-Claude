
from src.domain.exceptions import (
    RepositoryError,
    TodoDomainError,
    TodoNotFoundError,
    TodoValidationError,
)


class TestDomainExceptions:
    def test_todo_not_found_exception(self):
        exc = TodoNotFoundError("123")
        assert str(exc) == "Todo with id '123' not found"
        assert exc.todo_id == "123"

    def test_repository_error(self):
        exc = RepositoryError("Connection failed")
        assert str(exc) == "Repository operation failed: Connection failed"

    def test_validation_error(self):
        exc = TodoValidationError("Title is required")
        assert "Title is required" in str(exc)

    def test_exception_hierarchy(self):
        # Test that all exceptions inherit from TodoDomainError
        assert issubclass(TodoNotFoundError, TodoDomainError)
        assert issubclass(RepositoryError, TodoDomainError)
        assert issubclass(TodoValidationError, TodoDomainError)
