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
