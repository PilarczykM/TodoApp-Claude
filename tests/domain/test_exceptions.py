
from src.domain.exceptions import (
    TodoDomainError,
    TodoValidationError,
)


class TestDomainExceptions:
    def test_validation_error(self):
        exc = TodoValidationError("Title is required")
        assert "Title is required" in str(exc)

    def test_exception_hierarchy(self):
        # Test that all exceptions inherit from TodoDomainError
        assert issubclass(TodoValidationError, TodoDomainError)
