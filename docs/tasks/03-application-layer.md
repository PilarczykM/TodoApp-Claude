# Phase 3: Application Layer Implementation Tasks

## Prerequisites
- Phase 1 (Domain Layer) completed successfully
- Phase 2 (Infrastructure Layer) completed successfully
- Domain entities and repository interfaces available
- Concrete repository implementations available

## Task Overview
Implement the application layer containing business logic, use cases, and service orchestration. This layer coordinates between domain entities and infrastructure, providing a clean API for the interface layer.

---

## Task 3.1: Create Data Transfer Objects (DTOs)

**File:** `src/application/dto/todo_dto.py`

**Test First Approach:**
1. **Write Test** (`tests/application/dto/test_todo_dto.py`):
   ```python
   from domain import Todo, Priority
   from application.dto import CreateTodoDto, UpdateTodoDto, TodoResponseDto
   
   def test_create_todo_dto():
       dto = CreateTodoDto(
           title="Test Task",
           description="Test description",
           priority="high"
       )
       assert dto.title == "Test Task"
       assert dto.description == "Test description"
       assert dto.priority == Priority.HIGH
   
   def test_create_todo_dto_validation():
       with pytest.raises(ValidationError):
           CreateTodoDto(title="")  # Empty title
       
       with pytest.raises(ValidationError):
           CreateTodoDto(title="Test", priority="invalid")  # Invalid priority
   
   def test_update_todo_dto():
       dto = UpdateTodoDto(
           title="Updated Task",
           description="Updated description",
           priority="low",
           completed=True
       )
       assert dto.title == "Updated Task"
       assert dto.completed is True
   
   def test_todo_response_dto_from_todo():
       todo = Todo(title="Test Task", priority=Priority.HIGH)
       dto = TodoResponseDto.from_todo(todo)
       
       assert dto.id == todo.id
       assert dto.title == todo.title
       assert dto.priority == "high"
       assert dto.completed is False
   ```

2. **Implement:**
   ```python
   from typing import Optional
   from datetime import datetime
   from pydantic import BaseModel, Field, validator
   
   from domain import Todo, Priority
   
   class CreateTodoDto(BaseModel):
       """DTO for creating a new todo."""
       title: str = Field(min_length=1, max_length=200)
       description: Optional[str] = Field(None, max_length=1000)
       priority: str = Field(default="medium")
       
       @validator('title')
       def validate_title(cls, v):
           if not v.strip():
               raise ValueError('Title cannot be empty or whitespace')
           return v.strip()
       
       @validator('priority')
       def validate_priority(cls, v):
           if v not in [p.value for p in Priority]:
               raise ValueError(f'Priority must be one of: {[p.value for p in Priority]}')
           return v
       
       def to_domain(self) -> Todo:
           """Convert DTO to domain entity."""
           return Todo(
               title=self.title,
               description=self.description,
               priority=Priority(self.priority)
           )
   
   class UpdateTodoDto(BaseModel):
       """DTO for updating an existing todo."""
       title: Optional[str] = Field(None, min_length=1, max_length=200)
       description: Optional[str] = Field(None, max_length=1000)
       priority: Optional[str] = None
       completed: Optional[bool] = None
       
       @validator('title')
       def validate_title(cls, v):
           if v is not None and not v.strip():
               raise ValueError('Title cannot be empty or whitespace')
           return v.strip() if v else v
       
       @validator('priority')
       def validate_priority(cls, v):
           if v is not None and v not in [p.value for p in Priority]:
               raise ValueError(f'Priority must be one of: {[p.value for p in Priority]}')
           return v
   
   class TodoResponseDto(BaseModel):
       """DTO for todo responses."""
       id: str
       title: str
       description: Optional[str]
       completed: bool
       priority: str
       created_at: datetime
       updated_at: Optional[datetime]
       
       @classmethod
       def from_todo(cls, todo: Todo) -> 'TodoResponseDto':
           """Create DTO from domain entity."""
           return cls(
               id=todo.id,
               title=todo.title,
               description=todo.description,
               completed=todo.completed,
               priority=todo.priority.value,
               created_at=todo.created_at,
               updated_at=todo.updated_at
           )
   
   class TodoListDto(BaseModel):
       """DTO for todo list responses."""
       todos: list[TodoResponseDto]
       total_count: int
       completed_count: int
       pending_count: int
       
       @classmethod
       def from_todos(cls, todos: list[Todo]) -> 'TodoListDto':
           """Create DTO from list of domain entities."""
           todo_dtos = [TodoResponseDto.from_todo(todo) for todo in todos]
           completed_count = sum(1 for todo in todos if todo.completed)
           
           return cls(
               todos=todo_dtos,
               total_count=len(todos),
               completed_count=completed_count,
               pending_count=len(todos) - completed_count
           )
   ```

**Acceptance Criteria:**
- [ ] DTOs for create, update, and response operations
- [ ] Input validation with Pydantic v2
- [ ] Conversion methods between DTOs and domain entities
- [ ] All tests pass
- [ ] No linting violations

---

## Task 3.2: Create Todo Service (Core Business Logic)

**File:** `src/application/todo_service.py`

**Test First Approach:**
1. **Write Test** (`tests/application/test_todo_service.py`):
   ```python
   from unittest.mock import Mock
   import pytest
   from domain import Todo, Priority, TodoNotFoundError, TodoRepository
   from application import TodoService, CreateTodoDto, UpdateTodoDto
   
   @pytest.fixture
   def mock_repository():
       return Mock(spec=TodoRepository)
   
   @pytest.fixture
   def todo_service(mock_repository):
       return TodoService(mock_repository)
   
   def test_create_todo(todo_service, mock_repository):
       dto = CreateTodoDto(title="Test Task", priority="high")
       
       result = todo_service.create_todo(dto)
       
       mock_repository.save.assert_called_once()
       assert result.title == "Test Task"
       assert result.priority == "high"
       assert result.completed is False
   
   def test_get_todo_by_id(todo_service, mock_repository):
       todo = Todo(title="Test Task")
       mock_repository.find_by_id.return_value = todo
       
       result = todo_service.get_todo_by_id(todo.id)
       
       mock_repository.find_by_id.assert_called_once_with(todo.id)
       assert result.title == "Test Task"
   
   def test_get_todo_by_id_not_found(todo_service, mock_repository):
       mock_repository.find_by_id.return_value = None
       
       with pytest.raises(TodoNotFoundError):
           todo_service.get_todo_by_id("nonexistent")
   
   def test_update_todo(todo_service, mock_repository):
       todo = Todo(title="Original Task")
       mock_repository.find_by_id.return_value = todo
       mock_repository.exists.return_value = True
       
       update_dto = UpdateTodoDto(title="Updated Task", completed=True)
       result = todo_service.update_todo(todo.id, update_dto)
       
       mock_repository.update.assert_called_once()
       assert result.title == "Updated Task"
       assert result.completed is True
   
   def test_delete_todo(todo_service, mock_repository):
       mock_repository.delete.return_value = True
       
       result = todo_service.delete_todo("test-id")
       
       mock_repository.delete.assert_called_once_with("test-id")
       assert result is True
   
   def test_get_all_todos(todo_service, mock_repository):
       todos = [
           Todo(title="Task 1"),
           Todo(title="Task 2", completed=True)
       ]
       mock_repository.find_all.return_value = todos
       
       result = todo_service.get_all_todos()
       
       mock_repository.find_all.assert_called_once()
       assert result.total_count == 2
       assert result.completed_count == 1
       assert result.pending_count == 1
   
   def test_toggle_completion(todo_service, mock_repository):
       todo = Todo(title="Test Task", completed=False)
       mock_repository.find_by_id.return_value = todo
       mock_repository.exists.return_value = True
       
       result = todo_service.toggle_completion(todo.id)
       
       mock_repository.update.assert_called_once()
       assert result.completed is True
   ```

2. **Implement:**
   ```python
   from typing import List, Optional
   from domain import TodoRepository, Todo, TodoNotFoundError, Priority
   from .dto import CreateTodoDto, UpdateTodoDto, TodoResponseDto, TodoListDto
   
   class TodoService:
       """Application service for todo operations."""
       
       def __init__(self, repository: TodoRepository):
           self._repository = repository
       
       def create_todo(self, dto: CreateTodoDto) -> TodoResponseDto:
           """Create a new todo item."""
           todo = dto.to_domain()
           self._repository.save(todo)
           return TodoResponseDto.from_todo(todo)
       
       def get_todo_by_id(self, todo_id: str) -> TodoResponseDto:
           """Get a todo item by its ID."""
           todo = self._repository.find_by_id(todo_id)
           if todo is None:
               raise TodoNotFoundError(todo_id)
           return TodoResponseDto.from_todo(todo)
       
       def get_all_todos(self) -> TodoListDto:
           """Get all todo items."""
           todos = self._repository.find_all()
           return TodoListDto.from_todos(todos)
       
       def update_todo(self, todo_id: str, dto: UpdateTodoDto) -> TodoResponseDto:
           """Update an existing todo item."""
           todo = self._repository.find_by_id(todo_id)
           if todo is None:
               raise TodoNotFoundError(todo_id)
           
           # Update fields that are provided in DTO
           if dto.title is not None:
               todo.update_title(dto.title)
           
           if dto.description is not None:
               todo.update_description(dto.description)
           
           if dto.priority is not None:
               todo.update_priority(Priority(dto.priority))
           
           if dto.completed is not None:
               if dto.completed:
                   todo.mark_completed()
               else:
                   todo.mark_incomplete()
           
           self._repository.update(todo)
           return TodoResponseDto.from_todo(todo)
       
       def delete_todo(self, todo_id: str) -> bool:
           """Delete a todo item."""
           return self._repository.delete(todo_id)
       
       def toggle_completion(self, todo_id: str) -> TodoResponseDto:
           """Toggle completion status of a todo item."""
           todo = self._repository.find_by_id(todo_id)
           if todo is None:
               raise TodoNotFoundError(todo_id)
           
           if todo.completed:
               todo.mark_incomplete()
           else:
               todo.mark_completed()
           
           self._repository.update(todo)
           return TodoResponseDto.from_todo(todo)
       
       def get_todos_by_status(self, completed: bool) -> TodoListDto:
           """Get todos filtered by completion status."""
           all_todos = self._repository.find_all()
           filtered_todos = [todo for todo in all_todos if todo.completed == completed]
           return TodoListDto.from_todos(filtered_todos)
       
       def get_todos_by_priority(self, priority: Priority) -> TodoListDto:
           """Get todos filtered by priority."""
           all_todos = self._repository.find_all()
           filtered_todos = [todo for todo in all_todos if todo.priority == priority]
           return TodoListDto.from_todos(filtered_todos)
       
       def get_statistics(self) -> dict:
           """Get statistics about todos."""
           all_todos = self._repository.find_all()
           
           return {
               "total_count": len(all_todos),
               "completed_count": sum(1 for todo in all_todos if todo.completed),
               "pending_count": sum(1 for todo in all_todos if not todo.completed),
               "by_priority": {
                   priority.value: sum(1 for todo in all_todos if todo.priority == priority)
                   for priority in Priority
               }
           }
   ```

**Acceptance Criteria:**
- [ ] All CRUD operations implemented
- [ ] Business logic for todo management
- [ ] DTO conversions handled properly
- [ ] Filtering and statistics functionality
- [ ] Comprehensive error handling
- [ ] All tests pass with >90% coverage
- [ ] No direct coupling to infrastructure layer

---

## Task 3.3: Create Application Configuration

**File:** `src/application/config.py`

**Test First Approach:**
1. **Write Test** (`tests/application/test_config.py`):
   ```python
   import tempfile
   from pathlib import Path
   from application import AppConfig
   
   def test_app_config_creation():
       with tempfile.TemporaryDirectory() as temp_dir:
           config = AppConfig(
               storage_format="json",
               data_directory=Path(temp_dir)
           )
           assert config.storage_format == "json"
           assert config.data_directory == Path(temp_dir)
           assert config.backup_enabled is True
   
   def test_app_config_validation():
       with tempfile.TemporaryDirectory() as temp_dir:
           with pytest.raises(ValueError):
               AppConfig(
                   storage_format="invalid",
                   data_directory=Path(temp_dir)
               )
   ```

2. **Implement:**
   ```python
   from pathlib import Path
   from typing import Literal
   from pydantic import BaseModel, validator
   
   from infrastructure import StorageFormat
   
   class AppConfig(BaseModel):
       """Application configuration."""
       
       storage_format: StorageFormat = "json"
       data_directory: Path = Path.home() / ".todoapp"
       backup_enabled: bool = True
       max_backups: int = 5
       
       @validator('data_directory')
       def validate_data_directory(cls, v):
           """Ensure data directory exists."""
           v.mkdir(parents=True, exist_ok=True)
           return v
       
       class Config:
           arbitrary_types_allowed = True
   ```

**Acceptance Criteria:**
- [ ] Configuration management with validation
- [ ] Default values for all settings
- [ ] Path handling for data directory
- [ ] Type safety with Pydantic v2

---

## Task 3.4: Create Use Case Classes

**File:** `src/application/use_cases/create_todo_use_case.py`

**Test First Approach:**
1. **Write Test** (`tests/application/use_cases/test_create_todo_use_case.py`):
   ```python
   from unittest.mock import Mock
   from domain import TodoRepository
   from application.use_cases import CreateTodoUseCase
   from application.dto import CreateTodoDto
   
   def test_create_todo_use_case():
       mock_repository = Mock(spec=TodoRepository)
       use_case = CreateTodoUseCase(mock_repository)
       
       dto = CreateTodoDto(title="Test Task", priority="high")
       result = use_case.execute(dto)
       
       mock_repository.save.assert_called_once()
       assert result.title == "Test Task"
   ```

2. **Implement:**
   ```python
   from domain import TodoRepository
   from ..dto import CreateTodoDto, TodoResponseDto
   
   class CreateTodoUseCase:
       """Use case for creating a new todo."""
       
       def __init__(self, repository: TodoRepository):
           self._repository = repository
       
       def execute(self, dto: CreateTodoDto) -> TodoResponseDto:
           """Execute the create todo use case."""
           todo = dto.to_domain()
           self._repository.save(todo)
           return TodoResponseDto.from_todo(todo)
   ```

**Additional Use Case Files:**
- `src/application/use_cases/get_todo_use_case.py`
- `src/application/use_cases/update_todo_use_case.py`
- `src/application/use_cases/delete_todo_use_case.py`
- `src/application/use_cases/list_todos_use_case.py`

**Acceptance Criteria:**
- [ ] Separate use case for each major operation
- [ ] Single responsibility principle followed
- [ ] Clear separation of concerns
- [ ] All tests pass

---

## Task 3.5: Create Input Validation Service

**File:** `src/application/validation_service.py`

**Test First Approach:**
1. **Write Test** (`tests/application/test_validation_service.py`):
   ```python
   from application import ValidationService, TodoValidationError
   
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
   ```

2. **Implement:**
   ```python
   import re
   from typing import Optional
   from domain import Priority, TodoValidationError
   
   class ValidationService:
       """Service for input validation."""
       
       @staticmethod
       def validate_title(title: str) -> None:
           """Validate todo title."""
           if not title or not title.strip():
               raise TodoValidationError("Title cannot be empty")
           
           if len(title.strip()) > 200:
               raise TodoValidationError("Title cannot exceed 200 characters")
       
       @staticmethod
       def validate_description(description: Optional[str]) -> None:
           """Validate todo description."""
           if description and len(description) > 1000:
               raise TodoValidationError("Description cannot exceed 1000 characters")
       
       @staticmethod
       def validate_priority(priority: str) -> None:
           """Validate priority value."""
           if priority not in [p.value for p in Priority]:
               valid_priorities = [p.value for p in Priority]
               raise TodoValidationError(f"Priority must be one of: {valid_priorities}")
       
       @staticmethod
       def validate_todo_id(todo_id: str) -> None:
           """Validate todo ID format."""
           if not todo_id or not todo_id.strip():
               raise TodoValidationError("Todo ID cannot be empty")
           
           # UUID format validation
           uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
           if not re.match(uuid_pattern, todo_id.strip()):
               raise TodoValidationError("Invalid todo ID format")
   ```

**Acceptance Criteria:**
- [ ] Comprehensive input validation
- [ ] Clear error messages
- [ ] Reusable validation methods
- [ ] All edge cases covered in tests

---

## Task 3.6: Create Application Module __init__.py

**File:** `src/application/__init__.py`

```python
"""Application layer - Business logic and use cases."""

from .todo_service import TodoService
from .config import AppConfig
from .validation_service import ValidationService
from .dto import (
    CreateTodoDto,
    UpdateTodoDto,
    TodoResponseDto,
    TodoListDto,
)

__all__ = [
    "TodoService",
    "AppConfig",
    "ValidationService",
    "CreateTodoDto",
    "UpdateTodoDto", 
    "TodoResponseDto",
    "TodoListDto",
]
```

---

## Task 3.7: Create Test Directory Structure

**Directories to create:**
- `tests/application/`
- `tests/application/dto/`
- `tests/application/use_cases/`
- `tests/application/__init__.py`
- `tests/application/dto/__init__.py`
- `tests/application/use_cases/__init__.py`

**Test Files Created:**
- `tests/application/test_todo_service.py`
- `tests/application/test_config.py`
- `tests/application/test_validation_service.py`
- `tests/application/dto/test_todo_dto.py`
- `tests/application/use_cases/test_create_todo_use_case.py`

---

## Phase 3 Completion Checklist

**Code Quality:**
- [ ] All tests pass (`make test`)
- [ ] No linting violations (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Code formatting consistent (`make format`)
- [ ] Test coverage >90% for application layer

**Architecture:**
- [ ] Clean separation between application and domain layers
- [ ] No direct dependencies on infrastructure layer
- [ ] Use cases implement single responsibility principle
- [ ] DTOs provide clean data transformation
- [ ] Service layer orchestrates business logic correctly

**Functionality:**
- [ ] All CRUD operations implemented in service
- [ ] Input validation comprehensive and robust
- [ ] Configuration management working
- [ ] Error handling with appropriate exceptions
- [ ] DTO conversions working correctly
- [ ] Business logic encapsulated properly

**Files Created:**
- [ ] `src/application/todo_service.py`
- [ ] `src/application/config.py`
- [ ] `src/application/validation_service.py`
- [ ] `src/application/dto/todo_dto.py`
- [ ] `src/application/use_cases/create_todo_use_case.py`
- [ ] `src/application/__init__.py`
- [ ] `src/application/dto/__init__.py`
- [ ] `src/application/use_cases/__init__.py`
- [ ] All corresponding test files

---

## Next Phase
Once Phase 3 is complete, do not proceed to **Phase 4: Interface Layer** to implement the console user interface and application entry point.