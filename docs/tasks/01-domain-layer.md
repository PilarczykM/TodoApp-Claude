# Phase 1: Domain Layer Implementation Tasks

## Prerequisites
- Project structure exists (`src/`, `tests/` directories)
- Pydantic v2 available for models

## Task Overview
Implement the core domain layer following DDD principles and TDD approach. This layer contains business entities, value objects, and repository interfaces.

---

## Task 1.1: Create Priority Enumeration

**File:** `src/domain/priority.py`

**Test First Approach:**
1. **Write Test** (`tests/domain/test_priority.py`):
   ```python
   def test_priority_enum_values():
       assert Priority.LOW == "low"
       assert Priority.MEDIUM == "medium" 
       assert Priority.HIGH == "high"
   
   def test_priority_enum_membership():
       assert "low" in Priority
       assert "invalid" not in Priority
   ```

2. **Implement:**
   ```python
   from enum import Enum
   
   class Priority(str, Enum):
       LOW = "low"
       MEDIUM = "medium" 
       HIGH = "high"
   ```

3. **Quality Check:**
   ```bash
   make format
   make lint
   make typecheck
   make test
   ```

**Acceptance Criteria:**
- [ ] Priority enum with LOW, MEDIUM, HIGH values
- [ ] Inherits from str and Enum
- [ ] All tests pass
- [ ] No linting violations
- [ ] Type checking passes

---

## Task 1.2: Create Todo Domain Entity

**File:** `src/domain/todo.py`

**Test First Approach:**
1. **Write Test** (`tests/domain/test_todo.py`):
   ```python
   def test_todo_creation():
       todo = Todo(
           title="Test task",
           description="Test description",
           priority=Priority.HIGH
       )
       assert todo.title == "Test task"
       assert todo.description == "Test description"
       assert todo.priority == Priority.HIGH
       assert todo.completed is False
       assert todo.id is not None
       assert todo.created_at is not None
   
   def test_todo_completion_toggle():
       todo = Todo(title="Test")
       todo.mark_completed()
       assert todo.completed is True
       assert todo.updated_at is not None
   
   def test_todo_validation():
       with pytest.raises(ValidationError):
           Todo(title="")  # Empty title should fail
   ```

2. **Implement:**
   ```python
   from datetime import datetime
   from typing import Optional
   from uuid import uuid4
   from pydantic import BaseModel, Field, validator
   from .priority import Priority
   
   class Todo(BaseModel):
       id: str = Field(default_factory=lambda: str(uuid4()))
       title: str = Field(min_length=1, max_length=200)
       description: Optional[str] = Field(None, max_length=1000)
       completed: bool = False
       priority: Priority = Priority.MEDIUM
       created_at: datetime = Field(default_factory=datetime.now)
       updated_at: Optional[datetime] = None
       
       @validator('title')
       def validate_title(cls, v):
           if not v.strip():
               raise ValueError('Title cannot be empty or whitespace')
           return v.strip()
       
       def mark_completed(self) -> None:
           self.completed = True
           self.updated_at = datetime.now()
       
       def mark_incomplete(self) -> None:
           self.completed = False
           self.updated_at = datetime.now()
       
       def update_title(self, new_title: str) -> None:
           self.title = new_title
           self.updated_at = datetime.now()
       
       def update_description(self, new_description: Optional[str]) -> None:
           self.description = new_description
           self.updated_at = datetime.now()
       
       def update_priority(self, new_priority: Priority) -> None:
           self.priority = new_priority
           self.updated_at = datetime.now()
   ```

3. **Quality Check:**
   ```bash
   make format
   make lint
   make typecheck
   make test
   ```

**Acceptance Criteria:**
- [ ] Todo entity with all required fields
- [ ] UUID generation for id field
- [ ] Timestamp management (created_at, updated_at)
- [ ] Business methods for state changes
- [ ] Input validation with Pydantic v2
- [ ] All tests pass with >90% coverage
- [ ] No type checking errors

---

## Task 1.3: Create Domain Exceptions

**File:** `src/domain/exceptions.py`

**Test First Approach:**
1. **Write Test** (`tests/domain/test_exceptions.py`):
   ```python
   def test_todo_not_found_exception():
       exc = TodoNotFoundError("123")
       assert str(exc) == "Todo with id '123' not found"
       assert exc.todo_id == "123"
   
   def test_repository_error():
       exc = RepositoryError("Connection failed")
       assert str(exc) == "Repository operation failed: Connection failed"
   
   def test_validation_error():
       exc = TodoValidationError("Title is required")
       assert "Title is required" in str(exc)
   ```

2. **Implement:**
   ```python
   class TodoDomainError(Exception):
       """Base exception for todo domain errors."""
       pass
   
   class TodoNotFoundError(TodoDomainError):
       """Raised when a todo item is not found."""
       
       def __init__(self, todo_id: str):
           self.todo_id = todo_id
           super().__init__(f"Todo with id '{todo_id}' not found")
   
   class RepositoryError(TodoDomainError):
       """Raised when repository operations fail."""
       
       def __init__(self, message: str):
           super().__init__(f"Repository operation failed: {message}")
   
   class TodoValidationError(TodoDomainError):
       """Raised when todo validation fails."""
       pass
   ```

**Acceptance Criteria:**
- [ ] Domain-specific exception hierarchy
- [ ] Clear error messages with context
- [ ] All tests pass
- [ ] No linting violations

---

## Task 1.4: Create Repository Interface

**File:** `src/domain/repository.py`

**Test First Approach:**
1. **Write Test** (`tests/domain/test_repository.py`):
   ```python
   def test_repository_interface_methods():
       # Test that repository interface defines all required methods
       methods = dir(TodoRepository)
       assert 'save' in methods
       assert 'find_by_id' in methods
       assert 'find_all' in methods
       assert 'delete' in methods
       assert 'exists' in methods
   
   def test_abstract_methods():
       # Test that repository cannot be instantiated
       with pytest.raises(TypeError):
           TodoRepository()
   ```

2. **Implement:**
   ```python
   from abc import ABC, abstractmethod
   from typing import List, Optional
   from .todo import Todo
   
   class TodoRepository(ABC):
       """Abstract base class for todo data persistence."""
       
       @abstractmethod
       def save(self, todo: Todo) -> None:
           """Save a todo item to storage."""
           pass
       
       @abstractmethod
       def find_by_id(self, todo_id: str) -> Optional[Todo]:
           """Find a todo item by its ID."""
           pass
       
       @abstractmethod
       def find_all(self) -> List[Todo]:
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
   ```

**Acceptance Criteria:**
- [ ] Abstract base class with all CRUD operations
- [ ] Type hints for all method signatures
- [ ] Cannot be instantiated directly
- [ ] All tests pass
- [ ] Follows repository pattern principles

---

## Task 1.5: Create Domain Module __init__.py

**File:** `src/domain/__init__.py`

```python
"""Domain layer - Core business entities and rules."""

from .todo import Todo
from .priority import Priority
from .repository import TodoRepository
from .exceptions import (
    TodoDomainError,
    TodoNotFoundError,
    RepositoryError,
    TodoValidationError,
)

__all__ = [
    "Todo",
    "Priority", 
    "TodoRepository",
    "TodoDomainError",
    "TodoNotFoundError",
    "RepositoryError", 
    "TodoValidationError",
]
```

**Acceptance Criteria:**
- [ ] Clean imports for domain layer
- [ ] All domain objects accessible from package
- [ ] No circular imports

---

## Task 1.6: Create Test Directory Structure

**Directories to create:**
- `tests/domain/`
- `tests/domain/__init__.py`

**Test Files Created:**
- `tests/domain/test_priority.py`
- `tests/domain/test_todo.py`
- `tests/domain/test_exceptions.py`
- `tests/domain/test_repository.py`

---

## Phase 1 Completion Checklist

**Code Quality:**
- [ ] All tests pass (`make test`)
- [ ] No linting violations (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Code formatting consistent (`make format`)
- [ ] Test coverage >90% for domain layer

**Architecture:**
- [ ] Domain entities are framework-independent
- [ ] Repository pattern implemented correctly
- [ ] SOLID principles followed (especially SRP, OCP, DIP)
- [ ] Business logic encapsulated in domain objects
- [ ] Clean separation of concerns

**Functionality:**
- [ ] Todo entity with full business methods
- [ ] Priority enumeration working correctly
- [ ] Domain exceptions with clear messages
- [ ] Repository interface defines all operations
- [ ] All validation rules enforced

**Files Created:**
- [ ] `src/domain/priority.py`
- [ ] `src/domain/todo.py`
- [ ] `src/domain/exceptions.py`
- [ ] `src/domain/repository.py`
- [ ] `src/domain/__init__.py`
- [ ] `tests/domain/test_priority.py`
- [ ] `tests/domain/test_todo.py`
- [ ] `tests/domain/test_exceptions.py`
- [ ] `tests/domain/test_repository.py`

---

## Next Phase
Once Phase 1 is complete, do not proceed to **Phase 2: Infrastructure Layer** to implement concrete repository classes for JSON and XML persistence.

Refer to @docs/PRD.md only if additional product context is needed — it contains the full product overview.