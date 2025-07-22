# Phase 4: Interface Layer Implementation Tasks

## Prerequisites
- Phase 1 (Domain Layer) completed successfully
- Phase 2 (Infrastructure Layer) completed successfully
- Phase 3 (Application Layer) completed successfully
- All lower layers working and tested

## Task Overview
Implement the console user interface, format selection, and main application entry point. This layer provides the user interaction and coordinates with the application layer to deliver functionality.

---

## Task 4.1: Create Console Display Utilities

**File:** `src/interfaces/console_utils.py`

**Test First Approach:**
1. **Write Test** (`tests/interfaces/test_console_utils.py`):
   ```python
   from io import StringIO
   import sys
   from unittest.mock import patch
   from interfaces.console_utils import ConsoleUtils
   from application.dto import TodoResponseDto
   from datetime import datetime
   
   def test_display_header():
       output = StringIO()
       with patch('sys.stdout', output):
           ConsoleUtils.display_header("Test Title")
       
       result = output.getvalue()
       assert "Test Title" in result
       assert "=" in result
   
   def test_display_menu():
       output = StringIO()
       menu_options = ["Option 1", "Option 2", "Exit"]
       
       with patch('sys.stdout', output):
           ConsoleUtils.display_menu("Test Menu", menu_options)
       
       result = output.getvalue()
       assert "Test Menu" in result
       assert "1. Option 1" in result
       assert "2. Option 2" in result
       assert "3. Exit" in result
   
   def test_format_todo_display():
       todo = TodoResponseDto(
           id="123",
           title="Test Task",
           description="Test description",
           completed=False,
           priority="high",
           created_at=datetime.now(),
           updated_at=None
       )
       
       result = ConsoleUtils.format_todo_display(todo)
       assert "Test Task" in result
       assert "high" in result
       assert "[ ]" in result  # Incomplete task
   
   def test_get_user_input():
       with patch('builtins.input', return_value='test input'):
           result = ConsoleUtils.get_user_input("Enter something: ")
           assert result == "test input"
   ```

2. **Implement:**
   ```python
   from typing import List, Optional
   from datetime import datetime
   
   from application.dto import TodoResponseDto, TodoListDto
   
   class ConsoleUtils:
       """Utility class for console display and input."""
       
       @staticmethod
       def display_header(title: str, width: int = 60) -> None:
           """Display a formatted header."""
           print("=" * width)
           print(f"{title:^{width}}")
           print("=" * width)
       
       @staticmethod
       def display_menu(title: str, options: List[str]) -> None:
           """Display a menu with numbered options."""
           print(f"\\n{title}")
           print("-" * len(title))
           
           for i, option in enumerate(options, 1):
               print(f"{i}. {option}")
           print()
       
       @staticmethod
       def display_todos(todo_list: TodoListDto) -> None:
           """Display a formatted list of todos."""
           if not todo_list.todos:
               print("No todos found.")
               return
           
           print(f"\\nTodos ({todo_list.total_count} total, "
                 f"{todo_list.pending_count} pending, "
                 f"{todo_list.completed_count} completed):")
           print("-" * 80)
           
           for todo in todo_list.todos:
               print(ConsoleUtils.format_todo_display(todo))
           print("-" * 80)
       
       @staticmethod
       def format_todo_display(todo: TodoResponseDto) -> str:
           """Format a single todo for display."""
           status_symbol = "[✓]" if todo.completed else "[ ]"
           priority_symbol = {
               "low": "▼",
               "medium": "●", 
               "high": "▲"
           }.get(todo.priority, "●")
           
           # Truncate title if too long
           title = todo.title[:50] + "..." if len(todo.title) > 50 else todo.title
           
           # Format creation date
           created = todo.created_at.strftime("%Y-%m-%d %H:%M")
           
           return (f"{status_symbol} {priority_symbol} {title:<55} "
                  f"(ID: {todo.id[:8]}...) [{created}]")
       
       @staticmethod
       def display_todo_details(todo: TodoResponseDto) -> None:
           """Display detailed information about a todo."""
           print("\\nTodo Details:")
           print("-" * 40)
           print(f"ID: {todo.id}")
           print(f"Title: {todo.title}")
           print(f"Description: {todo.description or 'No description'}")
           print(f"Status: {'Completed' if todo.completed else 'Pending'}")
           print(f"Priority: {todo.priority.upper()}")
           print(f"Created: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
           if todo.updated_at:
               print(f"Updated: {todo.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
           print("-" * 40)
       
       @staticmethod
       def get_user_input(prompt: str, default: Optional[str] = None) -> str:
           """Get user input with optional default value."""
           if default:
               prompt = f"{prompt} (default: {default}): "
           else:
               prompt = f"{prompt}: "
           
           user_input = input(prompt).strip()
           return user_input if user_input else (default or "")
       
       @staticmethod
       def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
           """Get user choice from a list of valid options."""
           while True:
               choice = ConsoleUtils.get_user_input(prompt).lower()
               if choice in [c.lower() for c in valid_choices]:
                   return choice
               
               print(f"Invalid choice. Please select from: {', '.join(valid_choices)}")
       
       @staticmethod
       def get_menu_choice(max_option: int) -> int:
           """Get a menu choice as an integer."""
           while True:
               try:
                   choice = int(ConsoleUtils.get_user_input("Enter your choice"))
                   if 1 <= choice <= max_option:
                       return choice
                   else:
                       print(f"Please enter a number between 1 and {max_option}")
               except ValueError:
                   print("Please enter a valid number")
       
       @staticmethod
       def confirm_action(message: str) -> bool:
           """Get confirmation from user."""
           choice = ConsoleUtils.get_user_choice(f"{message} (y/n)", ["y", "yes", "n", "no"])
           return choice in ["y", "yes"]
       
       @staticmethod
       def display_error(message: str) -> None:
           """Display an error message."""
           print(f"\\n❌ Error: {message}\\n")
       
       @staticmethod
       def display_success(message: str) -> None:
           """Display a success message."""
           print(f"\\n✅ {message}\\n")
       
       @staticmethod
       def display_info(message: str) -> None:
           """Display an info message."""
           print(f"\\nℹ️  {message}\\n")
       
       @staticmethod
       def clear_screen() -> None:
           """Clear the console screen."""
           import os
           os.system('cls' if os.name == 'nt' else 'clear')
       
       @staticmethod
       def pause() -> None:
           """Pause and wait for user to press Enter."""
           input("\\nPress Enter to continue...")
   ```

**Acceptance Criteria:**
- [ ] Comprehensive console display utilities
- [ ] User input handling with validation
- [ ] Formatted todo display with status indicators
- [ ] Menu system support
- [ ] Error and success message display
- [ ] All tests pass

---

## Task 4.2: Create Storage Format Selection

**File:** `src/interfaces/format_selector.py`

**Test First Approach:**
1. **Write Test** (`tests/interfaces/test_format_selector.py`):
   ```python
   from unittest.mock import patch
   from interfaces.format_selector import FormatSelector
   
   def test_select_format_json():
       with patch('builtins.input', return_value='1'):
           result = FormatSelector.select_storage_format()
           assert result == "json"
   
   def test_select_format_xml():
       with patch('builtins.input', return_value='2'):
           result = FormatSelector.select_storage_format()
           assert result == "xml"
   
   def test_select_format_invalid_then_valid():
       with patch('builtins.input', side_effect=['invalid', '99', '1']):
           result = FormatSelector.select_storage_format()
           assert result == "json"
   ```

2. **Implement:**
   ```python
   from typing import Literal
   from .console_utils import ConsoleUtils
   
   StorageFormat = Literal["json", "xml"]
   
   class FormatSelector:
       """Handles storage format selection at application startup."""
       
       @staticmethod
       def select_storage_format() -> StorageFormat:
           """Allow user to select storage format."""
           ConsoleUtils.display_header("Todo App - Storage Format Selection")
           
           print("Welcome to the Todo List Application!")
           print("Please choose your preferred data storage format:\\n")
           
           ConsoleUtils.display_menu("Storage Format Options", [
               "JSON format (.json file)",
               "XML format (.xml file)"
           ])
           
           while True:
               try:
                   choice = ConsoleUtils.get_menu_choice(2)
                   
                   if choice == 1:
                       ConsoleUtils.display_success("JSON format selected")
                       return "json"
                   elif choice == 2:
                       ConsoleUtils.display_success("XML format selected")
                       return "xml"
                       
               except Exception as e:
                   ConsoleUtils.display_error(f"Invalid selection: {e}")
       
       @staticmethod
       def display_format_info() -> None:
           """Display information about storage formats."""
           print("Storage Format Information:")
           print("- JSON: Lightweight, human-readable, commonly used")
           print("- XML: Structured, self-documenting, widely supported")
           print()
   ```

**Acceptance Criteria:**
- [ ] Clear format selection interface
- [ ] Input validation and error handling  
- [ ] Informative display about format options
- [ ] Type-safe return values
- [ ] All tests pass

---

## Task 4.3: Create Main Console Interface

**File:** `src/interfaces/console_interface.py`

**Test First Approach:**
1. **Write Test** (`tests/interfaces/test_console_interface.py`):
   ```python
   from unittest.mock import Mock, patch
   from interfaces.console_interface import ConsoleInterface
   from application import TodoService
   from application.dto import TodoResponseDto, TodoListDto
   
   @pytest.fixture
   def mock_service():
       return Mock(spec=TodoService)
   
   @pytest.fixture 
   def console_interface(mock_service):
       return ConsoleInterface(mock_service)
   
   def test_display_main_menu(console_interface):
       with patch('interfaces.console_utils.ConsoleUtils.display_menu') as mock_display:
           console_interface._display_main_menu()
           mock_display.assert_called_once()
   
   def test_create_todo_success(console_interface, mock_service):
       todo_response = TodoResponseDto(
           id="123", title="Test Task", description=None,
           completed=False, priority="medium", 
           created_at=datetime.now(), updated_at=None
       )
       mock_service.create_todo.return_value = todo_response
       
       with patch('builtins.input', side_effect=['Test Task', '', 'medium']):
           result = console_interface._create_todo()
           
           mock_service.create_todo.assert_called_once()
           assert result is True
   ```

2. **Implement:**
   ```python
   from typing import Optional
   
   from application import TodoService, CreateTodoDto, UpdateTodoDto
   from domain import TodoNotFoundError, TodoValidationError, RepositoryError, Priority
   from .console_utils import ConsoleUtils
   
   class ConsoleInterface:
       """Main console interface for the Todo application."""
       
       def __init__(self, todo_service: TodoService):
           self._service = todo_service
           self._running = True
       
       def run(self) -> None:
           """Main application loop."""
           ConsoleUtils.display_header("Todo List Application")
           ConsoleUtils.display_info("Welcome! Manage your tasks efficiently.")
           
           while self._running:
               try:
                   self._display_main_menu()
                   choice = ConsoleUtils.get_menu_choice(6)
                   self._handle_menu_choice(choice)
                   
               except KeyboardInterrupt:
                   ConsoleUtils.display_info("Goodbye!")
                   break
               except Exception as e:
                   ConsoleUtils.display_error(f"Unexpected error: {e}")
                   ConsoleUtils.pause()
       
       def _display_main_menu(self) -> None:
           """Display the main application menu."""
           ConsoleUtils.display_menu("Main Menu", [
               "List all tasks",
               "Add new task", 
               "Update task",
               "Delete task",
               "Mark task complete/incomplete",
               "Exit"
           ])
       
       def _handle_menu_choice(self, choice: int) -> None:
           """Handle user's menu selection."""
           actions = {
               1: self._list_todos,
               2: self._create_todo,
               3: self._update_todo,
               4: self._delete_todo,
               5: self._toggle_completion,
               6: self._exit_application
           }
           
           action = actions.get(choice)
           if action:
               success = action()
               if success and choice != 6:  # Don't pause after exit
                   ConsoleUtils.pause()
       
       def _list_todos(self) -> bool:
           """Display all todos."""
           try:
               todo_list = self._service.get_all_todos()
               
               if not todo_list.todos:
                   ConsoleUtils.display_info("No todos found. Create your first task!")
                   return True
               
               ConsoleUtils.display_todos(todo_list)
               
               # Show filtering options
               print("\\nFiltering options:")
               print("1. Show all (current)")
               print("2. Show completed only") 
               print("3. Show pending only")
               print("4. Show by priority")
               print("5. Back to main menu")
               
               filter_choice = ConsoleUtils.get_menu_choice(5)
               if filter_choice == 2:
                   completed_todos = self._service.get_todos_by_status(True)
                   ConsoleUtils.display_todos(completed_todos)
               elif filter_choice == 3:
                   pending_todos = self._service.get_todos_by_status(False)
                   ConsoleUtils.display_todos(pending_todos)
               elif filter_choice == 4:
                   self._show_todos_by_priority()
               
               return True
               
           except RepositoryError as e:
               ConsoleUtils.display_error(f"Failed to load todos: {e}")
               return False
       
       def _create_todo(self) -> bool:
           """Create a new todo."""
           try:
               ConsoleUtils.display_header("Create New Task")
               
               title = ConsoleUtils.get_user_input("Enter task title")
               if not title:
                   ConsoleUtils.display_error("Title is required")
                   return False
               
               description = ConsoleUtils.get_user_input("Enter description (optional)")
               description = description if description else None
               
               priority = ConsoleUtils.get_user_choice(
                   "Enter priority (low/medium/high)", 
                   ["low", "medium", "high"]
               )
               
               dto = CreateTodoDto(
                   title=title,
                   description=description,
                   priority=priority
               )
               
               todo = self._service.create_todo(dto)
               ConsoleUtils.display_success(f"Task '{todo.title}' created successfully!")
               
               return True
               
           except TodoValidationError as e:
               ConsoleUtils.display_error(f"Validation error: {e}")
               return False
           except RepositoryError as e:
               ConsoleUtils.display_error(f"Failed to create todo: {e}")
               return False
       
       def _update_todo(self) -> bool:
           """Update an existing todo."""
           try:
               todo_id = self._select_todo("update")
               if not todo_id:
                   return False
               
               # Show current todo
               current_todo = self._service.get_todo_by_id(todo_id)
               ConsoleUtils.display_todo_details(current_todo)
               
               ConsoleUtils.display_header("Update Task")
               print("Leave empty to keep current value")
               
               new_title = ConsoleUtils.get_user_input("New title", current_todo.title)
               new_description = ConsoleUtils.get_user_input("New description")
               new_priority = ConsoleUtils.get_user_input("New priority (low/medium/high)")
               
               dto = UpdateTodoDto()
               
               if new_title != current_todo.title:
                   dto.title = new_title
               if new_description:
                   dto.description = new_description
               if new_priority and new_priority != current_todo.priority:
                   dto.priority = new_priority
               
               updated_todo = self._service.update_todo(todo_id, dto)
               ConsoleUtils.display_success(f"Task '{updated_todo.title}' updated successfully!")
               
               return True
               
           except TodoNotFoundError:
               ConsoleUtils.display_error("Todo not found")
               return False
           except TodoValidationError as e:
               ConsoleUtils.display_error(f"Validation error: {e}")
               return False
           except RepositoryError as e:
               ConsoleUtils.display_error(f"Failed to update todo: {e}")
               return False
       
       def _delete_todo(self) -> bool:
           """Delete a todo."""
           try:
               todo_id = self._select_todo("delete")
               if not todo_id:
                   return False
               
               # Show todo before deletion
               todo = self._service.get_todo_by_id(todo_id)
               ConsoleUtils.display_todo_details(todo)
               
               if ConsoleUtils.confirm_action(f"Delete task '{todo.title}'?"):
                   success = self._service.delete_todo(todo_id)
                   
                   if success:
                       ConsoleUtils.display_success("Task deleted successfully!")
                   else:
                       ConsoleUtils.display_error("Failed to delete task")
                       
                   return success
               
               ConsoleUtils.display_info("Delete cancelled")
               return True
               
           except TodoNotFoundError:
               ConsoleUtils.display_error("Todo not found")
               return False
           except RepositoryError as e:
               ConsoleUtils.display_error(f"Failed to delete todo: {e}")
               return False
       
       def _toggle_completion(self) -> bool:
           """Toggle completion status of a todo."""
           try:
               todo_id = self._select_todo("toggle completion for")
               if not todo_id:
                   return False
               
               updated_todo = self._service.toggle_completion(todo_id)
               status = "completed" if updated_todo.completed else "pending"
               
               ConsoleUtils.display_success(f"Task '{updated_todo.title}' marked as {status}!")
               return True
               
           except TodoNotFoundError:
               ConsoleUtils.display_error("Todo not found")
               return False
           except RepositoryError as e:
               ConsoleUtils.display_error(f"Failed to update todo: {e}")
               return False
       
       def _select_todo(self, action: str) -> Optional[str]:
           """Allow user to select a todo by showing list and getting ID."""
           try:
               todo_list = self._service.get_all_todos()
               
               if not todo_list.todos:
                   ConsoleUtils.display_info("No todos available")
                   return None
               
               ConsoleUtils.display_header(f"Select Todo to {action.title()}")
               ConsoleUtils.display_todos(todo_list)
               
               todo_id = ConsoleUtils.get_user_input("Enter todo ID (first 8 characters are enough)")
               
               # Allow partial ID matching
               if len(todo_id) >= 8:
                   for todo in todo_list.todos:
                       if todo.id.startswith(todo_id[:8]):
                           return todo.id
               
               ConsoleUtils.display_error("Todo not found with that ID")
               return None
               
           except RepositoryError as e:
               ConsoleUtils.display_error(f"Failed to load todos: {e}")
               return None
       
       def _show_todos_by_priority(self) -> None:
           """Show todos filtered by priority."""
           priority = ConsoleUtils.get_user_choice(
               "Select priority filter (low/medium/high)",
               ["low", "medium", "high"]
           )
           
           priority_enum = Priority(priority)
           filtered_todos = self._service.get_todos_by_priority(priority_enum)
           
           ConsoleUtils.display_header(f"Tasks with {priority.upper()} Priority")
           ConsoleUtils.display_todos(filtered_todos)
       
       def _exit_application(self) -> bool:
           """Exit the application."""
           if ConsoleUtils.confirm_action("Are you sure you want to exit?"):
               ConsoleUtils.display_info("Thank you for using Todo List Application!")
               self._running = False
           return True
   ```

**Acceptance Criteria:**
- [ ] Complete console interface with all CRUD operations
- [ ] Menu-driven navigation system
- [ ] Error handling and user feedback
- [ ] Input validation and confirmation dialogs
- [ ] Filtering and viewing options
- [ ] All tests pass with good coverage

---

## Task 4.4: Create Application Entry Point

**File:** `src/interfaces/main.py`

**Test First Approach:**
1. **Write Test** (`tests/interfaces/test_main.py`):
   ```python
   from unittest.mock import Mock, patch
   from pathlib import Path
   import tempfile
   
   def test_create_app_components():
       with tempfile.TemporaryDirectory() as temp_dir:
           with patch('interfaces.format_selector.FormatSelector.select_storage_format', return_value='json'):
               from interfaces.main import create_app_components
               
               service, config = create_app_components(Path(temp_dir))
               
               assert service is not None
               assert config is not None
               assert config.storage_format == "json"
   
   @patch('interfaces.console_interface.ConsoleInterface.run')
   @patch('interfaces.format_selector.FormatSelector.select_storage_format', return_value='json')
   def test_main_function(mock_format_select, mock_run):
       from interfaces.main import main
       
       main()
       mock_format_select.assert_called_once()
       mock_run.assert_called_once()
   ```

2. **Implement:**
   ```python
   import sys
   from pathlib import Path
   from typing import Tuple
   
   from domain import RepositoryError
   from application import TodoService, AppConfig
   from infrastructure import RepositoryFactory
   from .format_selector import FormatSelector
   from .console_interface import ConsoleInterface
   from .console_utils import ConsoleUtils
   
   def create_app_components(data_dir: Path) -> Tuple[TodoService, AppConfig]:
       """Create and configure application components."""
       try:
           # Get storage format from user
           storage_format = FormatSelector.select_storage_format()
           
           # Create configuration
           config = AppConfig(
               storage_format=storage_format,
               data_directory=data_dir
           )
           
           # Create repository
           repository = RepositoryFactory.create_repository(storage_format, data_dir)
           
           # Create service
           service = TodoService(repository)
           
           return service, config
           
       except Exception as e:
           ConsoleUtils.display_error(f"Failed to initialize application: {e}")
           sys.exit(1)
   
   def main() -> None:
       """Main application entry point."""
       try:
           # Set up data directory
           data_dir = Path.home() / ".todoapp"
           
           # Create application components
           service, config = create_app_components(data_dir)
           
           # Create and run console interface
           console = ConsoleInterface(service)
           console.run()
           
       except KeyboardInterrupt:
           ConsoleUtils.display_info("\\nApplication interrupted by user")
       except RepositoryError as e:
           ConsoleUtils.display_error(f"Data access error: {e}")
           sys.exit(1)
       except Exception as e:
           ConsoleUtils.display_error(f"Unexpected error: {e}")
           sys.exit(1)
   
   if __name__ == "__main__":
       main()
   ```

**Acceptance Criteria:**
- [ ] Clean application startup and initialization
- [ ] Format selection integration  
- [ ] Dependency injection setup
- [ ] Error handling for startup failures
- [ ] Configuration management
- [ ] All tests pass

---

## Task 4.5: Create CLI Entry Point Script

**File:** `src/todo_app.py` (Main CLI entry point)

```python
#!/usr/bin/env python3
"""
Console Todo List Application

A clean architecture implementation with CRUD operations
and support for both JSON and XML storage formats.
"""

from interfaces.main import main

if __name__ == "__main__":
    main()
```

**File:** Update `pyproject.toml` to add console script:

Add to `pyproject.toml`:
```toml
[project.scripts]
todo-app = "todo_app:main"
```

**Acceptance Criteria:**
- [ ] Simple CLI entry point
- [ ] Proper shebang for Unix systems
- [ ] Console script configuration
- [ ] Clean application startup

---

## Task 4.6: Create Interface Module __init__.py

**File:** `src/interfaces/__init__.py`

```python
"""Interface layer - User interfaces and application entry points."""

from .console_interface import ConsoleInterface
from .console_utils import ConsoleUtils
from .format_selector import FormatSelector
from .main import main, create_app_components

__all__ = [
    "ConsoleInterface", 
    "ConsoleUtils",
    "FormatSelector",
    "main",
    "create_app_components",
]
```

---

## Task 4.7: Create Test Directory Structure

**Directories to create:**
- `tests/interfaces/`
- `tests/interfaces/__init__.py`

**Test Files Created:**
- `tests/interfaces/test_console_utils.py`
- `tests/interfaces/test_format_selector.py`
- `tests/interfaces/test_console_interface.py`
- `tests/interfaces/test_main.py`

---

## Task 4.8: Create Integration Test

**File:** `tests/integration/test_full_application.py`

**Test First Approach:**
1. **Write Test:**
   ```python
   import tempfile
   from pathlib import Path
   from unittest.mock import patch
   
   def test_full_application_flow():
       """Test complete application flow from format selection to CRUD operations."""
       with tempfile.TemporaryDirectory() as temp_dir:
           data_dir = Path(temp_dir)
           
           # Mock user inputs for format selection and operations
           inputs = [
               '1',  # Select JSON format
               '2',  # Create new task
               'Test Task',  # Task title
               'Test Description',  # Task description
               'high',  # Priority
               '1',  # List all tasks
               '6'   # Exit
           ]
           
           with patch('builtins.input', side_effect=inputs):
               from interfaces.main import create_app_components
               from interfaces.console_interface import ConsoleInterface
               
               service, config = create_app_components(data_dir)
               assert config.storage_format == "json"
               
               # Verify data file was created
               json_file = data_dir / "todos.json"
               assert json_file.exists()
   ```

**Acceptance Criteria:**
- [ ] End-to-end integration test
- [ ] Covers format selection and basic operations
- [ ] Verifies data persistence
- [ ] Tests error handling scenarios

---

## Phase 4 Completion Checklist

**Code Quality:**
- [ ] All tests pass (`make test`)
- [ ] No linting violations (`make lint`) 
- [ ] Type checking passes (`make typecheck`)
- [ ] Code formatting consistent (`make format`)
- [ ] Test coverage >90% for interface layer

**Architecture:**
- [ ] Clean separation of interface layer concerns
- [ ] Proper dependency injection from lower layers
- [ ] Console interface independent of business logic
- [ ] Format selection handled cleanly at startup
- [ ] Error handling throughout the interface

**Functionality:**
- [ ] Complete console interface with all CRUD operations
- [ ] Format selection (JSON/XML) at startup
- [ ] Menu-driven navigation system
- [ ] Input validation and error messages
- [ ] Todo listing with filtering options
- [ ] Confirmation dialogs for destructive actions
- [ ] Graceful error handling and recovery

**User Experience:**
- [ ] Clear and intuitive menu system
- [ ] Informative success/error messages
- [ ] Formatted todo display with status indicators  
- [ ] Easy todo selection by partial ID
- [ ] Filtering by status and priority
- [ ] Confirmation for important actions

**Files Created:**
- [ ] `src/interfaces/console_utils.py`
- [ ] `src/interfaces/format_selector.py`
- [ ] `src/interfaces/console_interface.py`
- [ ] `src/interfaces/main.py`
- [ ] `src/interfaces/__init__.py`
- [ ] `src/todo_app.py`
- [ ] `tests/interfaces/test_console_utils.py`
- [ ] `tests/interfaces/test_format_selector.py`
- [ ] `tests/interfaces/test_console_interface.py`
- [ ] `tests/interfaces/test_main.py`
- [ ] `tests/integration/test_full_application.py`

---

## Next Phase
Once Phase 4 is complete, do not proceed to **Phase 5: Testing & Quality Assurance** to ensure comprehensive test coverage and code quality standards are met.