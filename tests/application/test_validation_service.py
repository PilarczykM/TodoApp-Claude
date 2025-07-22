import pytest

from src.application import ValidationService
from src.domain import TodoValidationError


def test_validate_todo_title():
    ValidationService.validate_title("Valid Title")  # Should not raise

    with pytest.raises(TodoValidationError):
        ValidationService.validate_title("")  # Empty title

    with pytest.raises(TodoValidationError):
        ValidationService.validate_title("   ")  # Whitespace only


def test_validate_priority():
    ValidationService.validate_priority("high")  # Should not raise

    with pytest.raises(TodoValidationError):
        ValidationService.validate_priority("invalid")


def test_validate_title_length():
    # Test max length validation
    with pytest.raises(TodoValidationError) as exc_info:
        ValidationService.validate_title("a" * 201)  # 201 chars
    assert "cannot exceed 200 characters" in str(exc_info.value)


def test_validate_description():
    ValidationService.validate_description("Valid description")  # Should not raise
    ValidationService.validate_description(None)  # Should not raise

    with pytest.raises(TodoValidationError) as exc_info:
        ValidationService.validate_description("a" * 1001)  # 1001 chars
    assert "cannot exceed 1000 characters" in str(exc_info.value)


def test_validate_todo_id():
    # Valid UUID
    ValidationService.validate_todo_id("12345678-1234-1234-1234-123456789abc")

    with pytest.raises(TodoValidationError) as exc_info:
        ValidationService.validate_todo_id("")
    assert "cannot be empty" in str(exc_info.value)

    with pytest.raises(TodoValidationError) as exc_info:
        ValidationService.validate_todo_id("   ")
    assert "cannot be empty" in str(exc_info.value)

    with pytest.raises(TodoValidationError) as exc_info:
        ValidationService.validate_todo_id("invalid-uuid")
    assert "Invalid todo ID format" in str(exc_info.value)
