"""Repository interface for todo persistence."""

from abc import ABC, abstractmethod

from .todo import Todo


class TodoRepository(ABC):
    """Abstract base class for todo data persistence."""

    @abstractmethod
    def save(self, todo: Todo) -> None:
        """Save a todo item to storage."""
        pass

    @abstractmethod
    def find_by_id(self, todo_id: str) -> Todo | None:
        """Find a todo item by its ID."""
        pass

    @abstractmethod
    def find_all(self) -> list[Todo]:
        """Retrieve all todo items."""
        pass

    @abstractmethod
    def delete(self, todo_id: str) -> bool:
        """Delete a todo item by ID. Returns True if deleted."""
        pass

    @abstractmethod
    def exists(self, todo_id: str) -> bool:
        """Check if a todo item exists."""
        pass

    @abstractmethod
    def update(self, todo: Todo) -> None:
        """Update an existing todo item."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the total number of todo items."""
        pass
