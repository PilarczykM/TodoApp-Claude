"""Domain-specific exceptions for todo application."""


class TodoDomainError(Exception):
    """Base exception for todo domain errors."""

    pass




class TodoValidationError(TodoDomainError):
    """Raised when todo validation fails."""
    pass


