# Phase 2: Infrastructure Layer Implementation Tasks

## Prerequisites
- Phase 1 (Domain Layer) completed successfully
- Domain entities and repository interface available
- JSON and XML processing capabilities available

## Task Overview
Implement concrete repository classes for data persistence, supporting both JSON and XML storage formats. This layer handles data access concerns while implementing the repository interfaces from the domain layer.

---

## Task 2.1: Create File Handler Utilities

**File:** `src/infrastructure/file_handler.py`

**Test First Approach:**
1. **Write Test** (`tests/infrastructure/test_file_handler.py`):
   ```python
   import tempfile
   import os
   from pathlib import Path
   
   def test_ensure_data_directory():
       with tempfile.TemporaryDirectory() as temp_dir:
           data_path = Path(temp_dir) / "data"
           FileHandler.ensure_data_directory(data_path)
           assert data_path.exists()
           assert data_path.is_dir()
   
   def test_backup_file():
       with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
           f.write("test content")
           temp_file = Path(f.name)
       
       backup_path = FileHandler.create_backup(temp_file)
       assert backup_path.exists()
       assert backup_path.read_text() == "test content"
   
   def test_safe_write():
       with tempfile.TemporaryDirectory() as temp_dir:
           file_path = Path(temp_dir) / "test.txt"
           FileHandler.safe_write(file_path, "test content")
           assert file_path.read_text() == "test content"
   ```

2. **Implement:**
   ```python
   import os
   import shutil
   from pathlib import Path
   from typing import Union
   from datetime import datetime
   
   class FileHandler:
       """Utility class for safe file operations."""
       
       @staticmethod
       def ensure_data_directory(path: Path) -> None:
           """Create directory if it doesn't exist."""
           path.mkdir(parents=True, exist_ok=True)
       
       @staticmethod
       def create_backup(file_path: Path) -> Path:
           """Create a backup of existing file."""
           if not file_path.exists():
               raise FileNotFoundError(f"File {file_path} does not exist")
           
           timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
           backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
           shutil.copy2(file_path, backup_path)
           return backup_path
       
       @staticmethod
       def safe_write(file_path: Path, content: str) -> None:
           """Safely write content to file with atomic operation."""
           temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
           
           try:
               # Write to temporary file first
               temp_path.write_text(content, encoding='utf-8')
               
               # Atomic move to final location
               if os.name == 'nt':  # Windows
                   if file_path.exists():
                       file_path.unlink()
               temp_path.replace(file_path)
               
           except Exception:
               # Clean up temporary file if something goes wrong
               if temp_path.exists():
                   temp_path.unlink()
               raise
       
       @staticmethod
       def file_exists_and_readable(file_path: Path) -> bool:
           """Check if file exists and is readable."""
           return file_path.exists() and os.access(file_path, os.R_OK)
   ```

**Acceptance Criteria:**
- [ ] Safe file operations with atomic writes
- [ ] Directory creation utilities
- [ ] Backup functionality for data safety
- [ ] Cross-platform file handling
- [ ] All tests pass
- [ ] No linting violations

---

## Task 2.2: Create JSON Repository Implementation

**File:** `src/infrastructure/json_repository.py`

**Test First Approach:**
1. **Write Test** (`tests/infrastructure/test_json_repository.py`):
   ```python
   import tempfile
   import json
   from pathlib import Path
   from domain import Todo, Priority, TodoNotFoundError
   
   def test_json_repository_save_and_find():
       with tempfile.TemporaryDirectory() as temp_dir:
           repo = JsonTodoRepository(Path(temp_dir) / "todos.json")
           
           todo = Todo(title="Test Task", priority=Priority.HIGH)
           repo.save(todo)
           
           found_todo = repo.find_by_id(todo.id)
           assert found_todo is not None
           assert found_todo.title == "Test Task"
           assert found_todo.priority == Priority.HIGH
   
   def test_json_repository_find_all():
       with tempfile.TemporaryDirectory() as temp_dir:
           repo = JsonTodoRepository(Path(temp_dir) / "todos.json")
           
           todo1 = Todo(title="Task 1")
           todo2 = Todo(title="Task 2") 
           repo.save(todo1)
           repo.save(todo2)
           
           all_todos = repo.find_all()
           assert len(all_todos) == 2
   
   def test_json_repository_delete():
       with tempfile.TemporaryDirectory() as temp_dir:
           repo = JsonTodoRepository(Path(temp_dir) / "todos.json")
           
           todo = Todo(title="Test Task")
           repo.save(todo)
           
           deleted = repo.delete(todo.id)
           assert deleted is True
           assert repo.find_by_id(todo.id) is None
   
   def test_json_repository_persistence():
       with tempfile.TemporaryDirectory() as temp_dir:
           file_path = Path(temp_dir) / "todos.json"
           
           # First repository instance
           repo1 = JsonTodoRepository(file_path)
           todo = Todo(title="Persistent Task")
           repo1.save(todo)
           
           # Second repository instance (simulating app restart)
           repo2 = JsonTodoRepository(file_path)
           found_todo = repo2.find_by_id(todo.id)
           assert found_todo is not None
           assert found_todo.title == "Persistent Task"
   ```

2. **Implement:**
   ```python
   import json
   from pathlib import Path
   from typing import List, Optional, Dict, Any
   from datetime import datetime
   
   from domain import Todo, TodoRepository, RepositoryError, TodoNotFoundError
   from .file_handler import FileHandler
   
   class JsonTodoRepository(TodoRepository):
       """JSON file-based implementation of TodoRepository."""
       
       def __init__(self, file_path: Path):
           self.file_path = file_path
           self._ensure_file_exists()
       
       def save(self, todo: Todo) -> None:
           """Save a todo item to JSON storage."""
           try:
               todos = self._load_all_todos()
               todos[todo.id] = self._todo_to_dict(todo)
               self._save_all_todos(todos)
           except Exception as e:
               raise RepositoryError(f"Failed to save todo: {e}")
       
       def find_by_id(self, todo_id: str) -> Optional[Todo]:
           """Find a todo item by its ID."""
           try:
               todos = self._load_all_todos()
               if todo_id in todos:
                   return self._dict_to_todo(todos[todo_id])
               return None
           except Exception as e:
               raise RepositoryError(f"Failed to find todo: {e}")
       
       def find_all(self) -> List[Todo]:
           """Retrieve all todo items."""
           try:
               todos = self._load_all_todos()
               return [self._dict_to_todo(data) for data in todos.values()]
           except Exception as e:
               raise RepositoryError(f"Failed to load todos: {e}")
       
       def delete(self, todo_id: str) -> bool:
           """Delete a todo item by ID."""
           try:
               todos = self._load_all_todos()
               if todo_id in todos:
                   del todos[todo_id]
                   self._save_all_todos(todos)
                   return True
               return False
           except Exception as e:
               raise RepositoryError(f"Failed to delete todo: {e}")
       
       def exists(self, todo_id: str) -> bool:
           """Check if a todo item exists."""
           return self.find_by_id(todo_id) is not None
       
       def update(self, todo: Todo) -> None:
           """Update an existing todo item."""
           if not self.exists(todo.id):
               raise TodoNotFoundError(todo.id)
           self.save(todo)
       
       def count(self) -> int:
           """Return the total number of todo items."""
           todos = self._load_all_todos()
           return len(todos)
       
       def _load_all_todos(self) -> Dict[str, Dict[str, Any]]:
           """Load all todos from JSON file."""
           if not self.file_path.exists():
               return {}
           
           try:
               content = self.file_path.read_text(encoding='utf-8')
               if not content.strip():
                   return {}
               return json.loads(content)
           except json.JSONDecodeError as e:
               raise RepositoryError(f"Invalid JSON format: {e}")
       
       def _save_all_todos(self, todos: Dict[str, Dict[str, Any]]) -> None:
           """Save all todos to JSON file."""
           try:
               # Create backup if file exists
               if self.file_path.exists():
                   FileHandler.create_backup(self.file_path)
               
               content = json.dumps(todos, indent=2, ensure_ascii=False)
               FileHandler.safe_write(self.file_path, content)
           except Exception as e:
               raise RepositoryError(f"Failed to write JSON file: {e}")
       
       def _todo_to_dict(self, todo: Todo) -> Dict[str, Any]:
           """Convert Todo object to dictionary."""
           return {
               "id": todo.id,
               "title": todo.title,
               "description": todo.description,
               "completed": todo.completed,
               "priority": todo.priority.value,
               "created_at": todo.created_at.isoformat(),
               "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
           }
       
       def _dict_to_todo(self, data: Dict[str, Any]) -> Todo:
           """Convert dictionary to Todo object."""
           return Todo(
               id=data["id"],
               title=data["title"],
               description=data.get("description"),
               completed=data["completed"],
               priority=data["priority"],
               created_at=datetime.fromisoformat(data["created_at"]),
               updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
           )
       
       def _ensure_file_exists(self) -> None:
           """Ensure the data directory and file exist."""
           FileHandler.ensure_data_directory(self.file_path.parent)
           if not self.file_path.exists():
               self.file_path.write_text('{}', encoding='utf-8')
   ```

**Acceptance Criteria:**
- [ ] Full CRUD operations implemented
- [ ] JSON serialization/deserialization working
- [ ] Data persistence between sessions
- [ ] Error handling with domain exceptions
- [ ] Backup functionality for data safety
- [ ] All tests pass with >90% coverage

---

## Task 2.3: Create XML Repository Implementation

**File:** `src/infrastructure/xml_repository.py`

**Test First Approach:**
1. **Write Test** (`tests/infrastructure/test_xml_repository.py`):
   ```python
   import tempfile
   from pathlib import Path
   from domain import Todo, Priority
   
   def test_xml_repository_save_and_find():
       with tempfile.TemporaryDirectory() as temp_dir:
           repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")
           
           todo = Todo(title="Test Task", priority=Priority.HIGH)
           repo.save(todo)
           
           found_todo = repo.find_by_id(todo.id)
           assert found_todo is not None
           assert found_todo.title == "Test Task"
           assert found_todo.priority == Priority.HIGH
   
   def test_xml_repository_find_all():
       with tempfile.TemporaryDirectory() as temp_dir:
           repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")
           
           todo1 = Todo(title="Task 1")
           todo2 = Todo(title="Task 2")
           repo.save(todo1)
           repo.save(todo2)
           
           all_todos = repo.find_all()
           assert len(all_todos) == 2
   
   def test_xml_repository_persistence():
       with tempfile.TemporaryDirectory() as temp_dir:
           file_path = Path(temp_dir) / "todos.xml"
           
           # First repository instance
           repo1 = XmlTodoRepository(file_path)
           todo = Todo(title="Persistent Task")
           repo1.save(todo)
           
           # Second repository instance
           repo2 = XmlTodoRepository(file_path)
           found_todo = repo2.find_by_id(todo.id)
           assert found_todo is not None
           assert found_todo.title == "Persistent Task"
   ```

2. **Implement:**
   ```python
   import xml.etree.ElementTree as ET
   from pathlib import Path
   from typing import List, Optional
   from datetime import datetime
   
   from domain import Todo, TodoRepository, RepositoryError, TodoNotFoundError, Priority
   from .file_handler import FileHandler
   
   class XmlTodoRepository(TodoRepository):
       """XML file-based implementation of TodoRepository."""
       
       def __init__(self, file_path: Path):
           self.file_path = file_path
           self._ensure_file_exists()
       
       def save(self, todo: Todo) -> None:
           """Save a todo item to XML storage."""
           try:
               root = self._load_xml_root()
               
               # Remove existing todo with same ID if it exists
               for existing in root.findall(f".//todo[@id='{todo.id}']"):
                   root.remove(existing)
               
               # Add updated todo
               todo_element = self._todo_to_xml_element(todo)
               root.append(todo_element)
               
               self._save_xml_root(root)
           except Exception as e:
               raise RepositoryError(f"Failed to save todo: {e}")
       
       def find_by_id(self, todo_id: str) -> Optional[Todo]:
           """Find a todo item by its ID."""
           try:
               root = self._load_xml_root()
               todo_element = root.find(f".//todo[@id='{todo_id}']")
               
               if todo_element is not None:
                   return self._xml_element_to_todo(todo_element)
               return None
           except Exception as e:
               raise RepositoryError(f"Failed to find todo: {e}")
       
       def find_all(self) -> List[Todo]:
           """Retrieve all todo items."""
           try:
               root = self._load_xml_root()
               todos = []
               
               for todo_element in root.findall(".//todo"):
                   todos.append(self._xml_element_to_todo(todo_element))
               
               return todos
           except Exception as e:
               raise RepositoryError(f"Failed to load todos: {e}")
       
       def delete(self, todo_id: str) -> bool:
           """Delete a todo item by ID."""
           try:
               root = self._load_xml_root()
               todo_element = root.find(f".//todo[@id='{todo_id}']")
               
               if todo_element is not None:
                   root.remove(todo_element)
                   self._save_xml_root(root)
                   return True
               return False
           except Exception as e:
               raise RepositoryError(f"Failed to delete todo: {e}")
       
       def exists(self, todo_id: str) -> bool:
           """Check if a todo item exists."""
           return self.find_by_id(todo_id) is not None
       
       def update(self, todo: Todo) -> None:
           """Update an existing todo item."""
           if not self.exists(todo.id):
               raise TodoNotFoundError(todo.id)
           self.save(todo)
       
       def count(self) -> int:
           """Return the total number of todo items."""
           root = self._load_xml_root()
           return len(root.findall(".//todo"))
       
       def _load_xml_root(self) -> ET.Element:
           """Load XML root element from file."""
           if not self.file_path.exists():
               return ET.Element("todos")
           
           try:
               tree = ET.parse(self.file_path)
               return tree.getroot()
           except ET.ParseError as e:
               raise RepositoryError(f"Invalid XML format: {e}")
       
       def _save_xml_root(self, root: ET.Element) -> None:
           """Save XML root element to file."""
           try:
               # Create backup if file exists
               if self.file_path.exists():
                   FileHandler.create_backup(self.file_path)
               
               # Format XML with proper indentation
               self._indent_xml(root)
               tree = ET.ElementTree(root)
               
               # Write to temporary file then move atomically
               xml_content = ET.tostring(root, encoding='unicode', xml_declaration=True)
               FileHandler.safe_write(self.file_path, xml_content)
               
           except Exception as e:
               raise RepositoryError(f"Failed to write XML file: {e}")
       
       def _todo_to_xml_element(self, todo: Todo) -> ET.Element:
           """Convert Todo object to XML element."""
           todo_elem = ET.Element("todo", id=todo.id)
           
           title_elem = ET.SubElement(todo_elem, "title")
           title_elem.text = todo.title
           
           if todo.description:
               desc_elem = ET.SubElement(todo_elem, "description")
               desc_elem.text = todo.description
           
           completed_elem = ET.SubElement(todo_elem, "completed")
           completed_elem.text = str(todo.completed).lower()
           
           priority_elem = ET.SubElement(todo_elem, "priority")
           priority_elem.text = todo.priority.value
           
           created_elem = ET.SubElement(todo_elem, "created_at")
           created_elem.text = todo.created_at.isoformat()
           
           if todo.updated_at:
               updated_elem = ET.SubElement(todo_elem, "updated_at")
               updated_elem.text = todo.updated_at.isoformat()
           
           return todo_elem
       
       def _xml_element_to_todo(self, element: ET.Element) -> Todo:
           """Convert XML element to Todo object."""
           todo_id = element.get("id")
           title = element.find("title").text
           description_elem = element.find("description")
           description = description_elem.text if description_elem is not None else None
           completed = element.find("completed").text.lower() == "true"
           priority = Priority(element.find("priority").text)
           created_at = datetime.fromisoformat(element.find("created_at").text)
           
           updated_elem = element.find("updated_at")
           updated_at = datetime.fromisoformat(updated_elem.text) if updated_elem is not None else None
           
           return Todo(
               id=todo_id,
               title=title,
               description=description,
               completed=completed,
               priority=priority,
               created_at=created_at,
               updated_at=updated_at,
           )
       
       def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
           """Add proper indentation to XML elements."""
           indent = "\\n" + level * "  "
           if len(elem):
               if not elem.text or not elem.text.strip():
                   elem.text = indent + "  "
               if not elem.tail or not elem.tail.strip():
                   elem.tail = indent
               for child in elem:
                   self._indent_xml(child, level + 1)
               if not child.tail or not child.tail.strip():
                   child.tail = indent
           else:
               if level and (not elem.tail or not elem.tail.strip()):
                   elem.tail = indent
       
       def _ensure_file_exists(self) -> None:
           """Ensure the data directory and file exist."""
           FileHandler.ensure_data_directory(self.file_path.parent)
           if not self.file_path.exists():
               root = ET.Element("todos")
               self._save_xml_root(root)
   ```

**Acceptance Criteria:**
- [ ] Full CRUD operations implemented
- [ ] XML serialization/deserialization working
- [ ] Proper XML formatting with indentation
- [ ] Data persistence between sessions
- [ ] Error handling with domain exceptions
- [ ] All tests pass with >90% coverage

---

## Task 2.4: Create Repository Factory

**File:** `src/infrastructure/repository_factory.py`

**Test First Approach:**
1. **Write Test** (`tests/infrastructure/test_repository_factory.py`):
   ```python
   from pathlib import Path
   import tempfile
   from infrastructure import RepositoryFactory, JsonTodoRepository, XmlTodoRepository
   
   def test_create_json_repository():
       with tempfile.TemporaryDirectory() as temp_dir:
           data_dir = Path(temp_dir)
           repo = RepositoryFactory.create_repository("json", data_dir)
           assert isinstance(repo, JsonTodoRepository)
   
   def test_create_xml_repository():
       with tempfile.TemporaryDirectory() as temp_dir:
           data_dir = Path(temp_dir)
           repo = RepositoryFactory.create_repository("xml", data_dir)
           assert isinstance(repo, XmlTodoRepository)
   
   def test_invalid_format():
       with tempfile.TemporaryDirectory() as temp_dir:
           data_dir = Path(temp_dir)
           with pytest.raises(ValueError):
               RepositoryFactory.create_repository("invalid", data_dir)
   ```

2. **Implement:**
   ```python
   from pathlib import Path
   from typing import Literal
   
   from domain import TodoRepository
   from .json_repository import JsonTodoRepository
   from .xml_repository import XmlTodoRepository
   
   StorageFormat = Literal["json", "xml"]
   
   class RepositoryFactory:
       """Factory class for creating repository instances."""
       
       @staticmethod
       def create_repository(format_type: StorageFormat, data_dir: Path) -> TodoRepository:
           """Create a repository instance based on format type."""
           if format_type == "json":
               file_path = data_dir / "todos.json"
               return JsonTodoRepository(file_path)
           elif format_type == "xml":
               file_path = data_dir / "todos.xml"
               return XmlTodoRepository(file_path)
           else:
               raise ValueError(f"Unsupported storage format: {format_type}")
       
       @staticmethod
       def get_supported_formats() -> List[str]:
           """Get list of supported storage formats."""
           return ["json", "xml"]
   ```

**Acceptance Criteria:**
- [ ] Factory pattern implementation
- [ ] Support for JSON and XML repositories
- [ ] Type safety with Literal types
- [ ] Clear error handling for invalid formats
- [ ] All tests pass

---

## Task 2.5: Create Infrastructure Module __init__.py

**File:** `src/infrastructure/__init__.py`

```python
"""Infrastructure layer - Data persistence implementations."""

from .file_handler import FileHandler
from .json_repository import JsonTodoRepository
from .xml_repository import XmlTodoRepository
from .repository_factory import RepositoryFactory, StorageFormat

__all__ = [
    "FileHandler",
    "JsonTodoRepository",
    "XmlTodoRepository",
    "RepositoryFactory",
    "StorageFormat",
]
```

---

## Task 2.6: Create Test Directory Structure

**Directories to create:**
- `tests/infrastructure/`
- `tests/infrastructure/__init__.py`

**Test Files Created:**
- `tests/infrastructure/test_file_handler.py`
- `tests/infrastructure/test_json_repository.py`
- `tests/infrastructure/test_xml_repository.py`
- `tests/infrastructure/test_repository_factory.py`

---

## Phase 2 Completion Checklist

**Code Quality:**
- [ ] All tests pass (`make test`)
- [ ] No linting violations (`make lint`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Code formatting consistent (`make format`)
- [ ] Test coverage >90% for infrastructure layer

**Architecture:**
- [ ] Repository pattern implemented correctly
- [ ] Strategy pattern used for different storage formats
- [ ] Factory pattern for repository creation
- [ ] Clean separation from domain layer
- [ ] SOLID principles followed

**Functionality:**
- [ ] JSON persistence working correctly
- [ ] XML persistence working correctly
- [ ] File operations are safe and atomic
- [ ] Backup functionality implemented
- [ ] Error handling with appropriate exceptions
- [ ] Data integrity maintained across formats

**Files Created:**
- [ ] `src/infrastructure/file_handler.py`
- [ ] `src/infrastructure/json_repository.py`
- [ ] `src/infrastructure/xml_repository.py`
- [ ] `src/infrastructure/repository_factory.py`
- [ ] `src/infrastructure/__init__.py`
- [ ] `tests/infrastructure/test_file_handler.py`
- [ ] `tests/infrastructure/test_json_repository.py`
- [ ] `tests/infrastructure/test_xml_repository.py`
- [ ] `tests/infrastructure/test_repository_factory.py`

---

## Next Phase
Once Phase 2 is complete, do not proceed to **Phase 3: Application Layer** to implement business logic and use cases that coordinate between domain and infrastructure layers.