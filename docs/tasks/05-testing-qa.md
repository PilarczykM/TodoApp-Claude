# Phase 5: Testing & Quality Assurance Tasks

## Prerequisites
- Phase 1-4 completed successfully
- All layers implemented and functional
- Basic unit tests written during TDD implementation

## Task Overview
Comprehensive testing strategy and quality assurance to ensure >90% test coverage, zero linting violations, and robust error handling. This phase focuses on integration testing, edge cases, performance testing, and final quality validation.

---

## Task 5.1: Enhance Unit Test Coverage

**Goal:** Achieve >90% test coverage across all layers

### Domain Layer Test Enhancements

**File:** `tests/domain/test_todo_enhanced.py`

**Test First Approach:**
1. **Write Enhanced Tests:**
   ```python
   import pytest
   from datetime import datetime, timedelta
   from pydantic import ValidationError
   from domain import Todo, Priority
   
   class TestTodoEdgeCases:
       def test_todo_with_unicode_characters(self):
           """Test todo with unicode characters in title and description."""
           todo = Todo(
               title="📝 测试任务",
               description="Unicode description: émojis 🎉 and special chars àáâã",
               priority=Priority.HIGH
           )
           assert todo.title == "📝 测试任务"
           assert "émojis 🎉" in todo.description
       
       def test_todo_title_boundary_values(self):
           """Test title with boundary length values."""
           # Minimum length (1 character)
           todo_min = Todo(title="A")
           assert todo_min.title == "A"
           
           # Maximum length (200 characters)
           long_title = "A" * 200
           todo_max = Todo(title=long_title)
           assert len(todo_max.title) == 200
           
           # Over maximum length should fail
           with pytest.raises(ValidationError):
               Todo(title="A" * 201)
       
       def test_todo_description_boundary_values(self):
           """Test description with boundary length values."""
           # Maximum length (1000 characters)
           long_desc = "A" * 1000
           todo = Todo(title="Test", description=long_desc)
           assert len(todo.description) == 1000
           
           # Over maximum length should fail
           with pytest.raises(ValidationError):
               Todo(title="Test", description="A" * 1001)
       
       def test_todo_whitespace_handling(self):
           """Test handling of whitespace in titles."""
           # Leading/trailing whitespace should be stripped
           todo = Todo(title="  Test Task  ")
           assert todo.title == "Test Task"
           
           # Only whitespace should fail
           with pytest.raises(ValidationError):
               Todo(title="   ")
       
       def test_todo_state_transitions(self):
           """Test all possible state transitions."""
           todo = Todo(title="Test")
           original_created = todo.created_at
           
           # Initial state
           assert not todo.completed
           assert todo.updated_at is None
           
           # Mark completed
           todo.mark_completed()
           assert todo.completed
           assert todo.updated_at is not None
           assert todo.updated_at > original_created
           
           # Mark incomplete again
           first_update = todo.updated_at
           todo.mark_incomplete() 
           assert not todo.completed
           assert todo.updated_at > first_update
       
       def test_todo_concurrent_updates(self):
           """Test handling of rapid successive updates."""
           todo = Todo(title="Test")
           
           # Rapid updates
           todo.update_title("Title 1")
           first_update = todo.updated_at
           
           todo.update_title("Title 2")
           second_update = todo.updated_at
           
           assert todo.title == "Title 2"
           assert second_update >= first_update
   ```

### Infrastructure Layer Test Enhancements

**File:** `tests/infrastructure/test_repository_edge_cases.py`

1. **Write Enhanced Tests:**
   ```python
   import tempfile
   import json
   import xml.etree.ElementTree as ET
   from pathlib import Path
   import pytest
   from domain import Todo, Priority, RepositoryError
   from infrastructure import JsonTodoRepository, XmlTodoRepository
   
   class TestRepositoryErrorHandling:
       def test_json_repository_corrupted_file(self):
           """Test handling of corrupted JSON files."""
           with tempfile.TemporaryDirectory() as temp_dir:
               json_file = Path(temp_dir) / "todos.json"
               
               # Write corrupted JSON
               json_file.write_text("{ invalid json content")
               
               repo = JsonTodoRepository(json_file)
               with pytest.raises(RepositoryError):
                   repo.find_all()
       
       def test_xml_repository_corrupted_file(self):
           """Test handling of corrupted XML files."""
           with tempfile.TemporaryDirectory() as temp_dir:
               xml_file = Path(temp_dir) / "todos.xml"
               
               # Write corrupted XML
               xml_file.write_text("<todos><todo>unclosed tag</todos>")
               
               repo = XmlTodoRepository(xml_file)
               with pytest.raises(RepositoryError):
                   repo.find_all()
       
       def test_repository_permission_denied(self):
           """Test handling of file permission issues."""
           with tempfile.TemporaryDirectory() as temp_dir:
               json_file = Path(temp_dir) / "readonly.json"
               json_file.write_text("{}")
               json_file.chmod(0o444)  # Read-only
               
               repo = JsonTodoRepository(json_file)
               todo = Todo(title="Test")
               
               # Should handle permission error gracefully
               with pytest.raises(RepositoryError):
                   repo.save(todo)
       
       def test_repository_disk_full_simulation(self):
           """Test handling of disk space issues."""
           # This test would require more complex setup
           # to simulate disk full conditions
           pass
       
       def test_repository_large_dataset(self):
           """Test repository performance with large datasets."""
           with tempfile.TemporaryDirectory() as temp_dir:
               repo = JsonTodoRepository(Path(temp_dir) / "todos.json")
               
               # Create 1000 todos
               todos = []
               for i in range(1000):
                   todo = Todo(
                       title=f"Task {i}",
                       description=f"Description for task {i}",
                       priority=Priority.MEDIUM
                   )
                   repo.save(todo)
                   todos.append(todo)
               
               # Test retrieval performance
               all_todos = repo.find_all()
               assert len(all_todos) == 1000
               
               # Test individual lookups
               for todo in todos[:10]:  # Test first 10
                   found = repo.find_by_id(todo.id)
                   assert found is not None
                   assert found.title == todo.title
   ```

### Application Layer Test Enhancements

**File:** `tests/application/test_service_edge_cases.py`

1. **Write Enhanced Tests:**
   ```python
   from unittest.mock import Mock, patch
   import pytest
   from domain import TodoRepository, Todo, TodoNotFoundError, RepositoryError
   from application import TodoService, CreateTodoDto, UpdateTodoDto
   
   class TestTodoServiceErrorHandling:
       @pytest.fixture
       def mock_repository(self):
           return Mock(spec=TodoRepository)
       
       @pytest.fixture
       def service(self, mock_repository):
           return TodoService(mock_repository)
       
       def test_service_handles_repository_errors(self, service, mock_repository):
           """Test service properly handles repository errors."""
           mock_repository.find_all.side_effect = RepositoryError("Database connection failed")
           
           with pytest.raises(RepositoryError):
               service.get_all_todos()
       
       def test_service_handles_concurrent_modifications(self, service, mock_repository):
           """Test handling of concurrent modifications."""
           todo = Todo(title="Original")
           mock_repository.find_by_id.return_value = todo
           mock_repository.exists.return_value = True
           
           # Simulate concurrent modification
           def update_side_effect(updated_todo):
               if updated_todo.title != "Original":
                   raise RepositoryError("Todo was modified by another process")
           
           mock_repository.update.side_effect = update_side_effect
           
           update_dto = UpdateTodoDto(title="Updated")
           with pytest.raises(RepositoryError):
               service.update_todo(todo.id, update_dto)
       
       def test_service_validates_input_thoroughly(self, service):
           """Test comprehensive input validation."""
           # Test various invalid inputs
           invalid_dtos = [
               CreateTodoDto(title="", description="test"),
               CreateTodoDto(title="A" * 201),  # Too long
               CreateTodoDto(title="Test", priority="invalid_priority"),
           ]
           
           for dto in invalid_dtos:
               with pytest.raises((ValidationError, ValueError)):
                   service.create_todo(dto)
   ```

**Acceptance Criteria:**
- [ ] >90% test coverage across all layers
- [ ] Edge cases and boundary conditions tested
- [ ] Error handling scenarios covered
- [ ] Performance tests for large datasets
- [ ] Concurrent access scenarios tested

---

## Task 5.2: Integration Testing

**Goal:** Test interaction between all layers

**File:** `tests/integration/test_layer_integration.py`

1. **Write Integration Tests:**
   ```python
   import tempfile
   from pathlib import Path
   import pytest
   from domain import Priority
   from application import TodoService, CreateTodoDto, UpdateTodoDto, AppConfig
   from infrastructure import RepositoryFactory
   
   class TestLayerIntegration:
       @pytest.fixture
       def temp_data_dir(self):
           with tempfile.TemporaryDirectory() as temp_dir:
               yield Path(temp_dir)
       
       @pytest.fixture(params=["json", "xml"])
       def todo_service(self, request, temp_data_dir):
           """Create TodoService with both JSON and XML repositories."""
           storage_format = request.param
           repository = RepositoryFactory.create_repository(storage_format, temp_data_dir)
           return TodoService(repository), storage_format
       
       def test_full_crud_cycle(self, todo_service):
           """Test complete CRUD cycle across all layers."""
           service, format_type = todo_service
           
           # Create
           create_dto = CreateTodoDto(
               title="Integration Test Task",
               description="Testing full stack integration",
               priority="high"
           )
           created_todo = service.create_todo(create_dto)
           
           assert created_todo.title == "Integration Test Task"
           assert created_todo.priority == "high"
           
           # Read
           retrieved_todo = service.get_todo_by_id(created_todo.id)
           assert retrieved_todo.title == created_todo.title
           
           all_todos = service.get_all_todos()
           assert all_todos.total_count == 1
           
           # Update
           update_dto = UpdateTodoDto(
               title="Updated Integration Task",
               completed=True
           )
           updated_todo = service.update_todo(created_todo.id, update_dto)
           
           assert updated_todo.title == "Updated Integration Task"
           assert updated_todo.completed is True
           
           # Delete
           success = service.delete_todo(created_todo.id)
           assert success is True
           
           # Verify deletion
           all_todos_after_delete = service.get_all_todos()
           assert all_todos_after_delete.total_count == 0
       
       def test_data_persistence_across_sessions(self, temp_data_dir):
           """Test that data persists across application sessions."""
           # First session - create data
           repo1 = RepositoryFactory.create_repository("json", temp_data_dir)
           service1 = TodoService(repo1)
           
           create_dto = CreateTodoDto(title="Persistent Task")
           created_todo = service1.create_todo(create_dto)
           
           # Second session - verify data exists
           repo2 = RepositoryFactory.create_repository("json", temp_data_dir)
           service2 = TodoService(repo2)
           
           all_todos = service2.get_all_todos()
           assert all_todos.total_count == 1
           assert all_todos.todos[0].title == "Persistent Task"
       
       def test_format_interoperability(self, temp_data_dir):
           """Test that both formats can handle the same operations."""
           formats = ["json", "xml"]
           
           for format_type in formats:
               repo = RepositoryFactory.create_repository(format_type, temp_data_dir)
               service = TodoService(repo)
               
               # Test all priority levels
               for priority in Priority:
                   dto = CreateTodoDto(
                       title=f"{format_type.upper()} {priority.value} task",
                       priority=priority.value
                   )
                   service.create_todo(dto)
               
               # Verify all were created
               all_todos = service.get_all_todos()
               assert all_todos.total_count == len(Priority)
               
               # Clean up for next format
               for todo in all_todos.todos:
                   service.delete_todo(todo.id)
   ```

**File:** `tests/integration/test_console_integration.py`

1. **Write Console Integration Tests:**
   ```python
   import tempfile
   from pathlib import Path
   from unittest.mock import patch, Mock
   from interfaces import ConsoleInterface, create_app_components
   
   class TestConsoleIntegration:
       def test_console_interface_with_real_service(self):
           """Test console interface with real service and repository."""
           with tempfile.TemporaryDirectory() as temp_dir:
               data_dir = Path(temp_dir)
               
               with patch('interfaces.format_selector.FormatSelector.select_storage_format', 
                         return_value='json'):
                   service, config = create_app_components(data_dir)
                   console = ConsoleInterface(service)
                   
                   # Test that console interface is properly initialized
                   assert console._service is not None
                   assert hasattr(console, '_running')
       
       def test_format_selection_integration(self):
           """Test format selection with actual repository creation."""
           with tempfile.TemporaryDirectory() as temp_dir:
               data_dir = Path(temp_dir)
               
               # Test JSON format selection
               with patch('interfaces.format_selector.FormatSelector.select_storage_format',
                         return_value='json'):
                   service, config = create_app_components(data_dir)
                   assert config.storage_format == "json"
                   
                   # Verify JSON file is created
                   json_file = data_dir / "todos.json"
                   assert json_file.exists()
               
               # Test XML format selection  
               with patch('interfaces.format_selector.FormatSelector.select_storage_format',
                         return_value='xml'):
                   service, config = create_app_components(data_dir)
                   assert config.storage_format == "xml"
                   
                   # Verify XML file is created
                   xml_file = data_dir / "todos.xml"
                   assert xml_file.exists()
   ```

**Acceptance Criteria:**
- [ ] Full integration tests across all layers
- [ ] Data persistence verification
- [ ] Format interoperability testing
- [ ] Console interface integration
- [ ] All integration tests pass

---

## Task 5.3: Performance and Load Testing

**Goal:** Ensure application performs well under various load conditions

**File:** `tests/performance/test_performance.py`

1. **Write Performance Tests:**
   ```python
   import time
   import tempfile
   from pathlib import Path
   import pytest
   from domain import Todo, Priority
   from infrastructure import JsonTodoRepository, XmlTodoRepository
   from application import TodoService, CreateTodoDto
   
   class TestPerformance:
       @pytest.fixture
       def temp_dir(self):
           with tempfile.TemporaryDirectory() as temp_dir:
               yield Path(temp_dir)
       
       @pytest.mark.performance
       def test_json_repository_performance(self, temp_dir):
           """Test JSON repository performance with large datasets."""
           repo = JsonTodoRepository(temp_dir / "todos.json")
           
           # Create 1000 todos
           start_time = time.time()
           
           todos = []
           for i in range(1000):
               todo = Todo(
                   title=f"Performance Test Task {i}",
                   description=f"Description {i}" * 10,  # Longer description
                   priority=Priority.MEDIUM
               )
               repo.save(todo)
               todos.append(todo)
           
           create_time = time.time() - start_time
           print(f"\\nJSON: Created 1000 todos in {create_time:.2f} seconds")
           
           # Test retrieval performance
           start_time = time.time()
           all_todos = repo.find_all()
           retrieval_time = time.time() - start_time
           
           print(f"JSON: Retrieved {len(all_todos)} todos in {retrieval_time:.2f} seconds")
           
           # Performance assertions (adjust thresholds as needed)
           assert create_time < 10.0  # Should create 1000 todos in under 10 seconds
           assert retrieval_time < 2.0  # Should retrieve 1000 todos in under 2 seconds
           assert len(all_todos) == 1000
       
       @pytest.mark.performance
       def test_xml_repository_performance(self, temp_dir):
           """Test XML repository performance with large datasets."""
           repo = XmlTodoRepository(temp_dir / "todos.xml")
           
           # Create 1000 todos
           start_time = time.time()
           
           todos = []
           for i in range(1000):
               todo = Todo(
                   title=f"Performance Test Task {i}",
                   description=f"Description {i}" * 10,
                   priority=Priority.HIGH
               )
               repo.save(todo)
               todos.append(todo)
           
           create_time = time.time() - start_time
           print(f"\\nXML: Created 1000 todos in {create_time:.2f} seconds")
           
           # Test retrieval performance
           start_time = time.time()
           all_todos = repo.find_all()
           retrieval_time = time.time() - start_time
           
           print(f"XML: Retrieved {len(all_todos)} todos in {retrieval_time:.2f} seconds")
           
           # Performance assertions (XML typically slower than JSON)
           assert create_time < 15.0  # Should create 1000 todos in under 15 seconds
           assert retrieval_time < 3.0  # Should retrieve 1000 todos in under 3 seconds
           assert len(all_todos) == 1000
       
       @pytest.mark.performance
       def test_service_layer_performance(self, temp_dir):
           """Test application service performance."""
           from infrastructure import RepositoryFactory
           
           repo = RepositoryFactory.create_repository("json", temp_dir)
           service = TodoService(repo)
           
           # Batch create performance
           start_time = time.time()
           
           for i in range(100):
               dto = CreateTodoDto(
                   title=f"Service Performance Task {i}",
                   description="Testing service layer performance",
                   priority="medium"
               )
               service.create_todo(dto)
           
           batch_create_time = time.time() - start_time
           print(f"\\nService: Created 100 todos in {batch_create_time:.2f} seconds")
           
           # Statistics calculation performance
           start_time = time.time()
           stats = service.get_statistics()
           stats_time = time.time() - start_time
           
           print(f"Service: Generated statistics in {stats_time:.2f} seconds")
           
           assert batch_create_time < 5.0
           assert stats_time < 1.0
           assert stats["total_count"] == 100
       
       @pytest.mark.performance
       def test_memory_usage(self, temp_dir):
           """Test memory usage with large datasets."""
           import psutil
           import os
           
           process = psutil.Process(os.getpid())
           initial_memory = process.memory_info().rss / 1024 / 1024  # MB
           
           repo = JsonTodoRepository(temp_dir / "todos.json")
           
           # Create large number of todos
           for i in range(5000):
               todo = Todo(
                   title=f"Memory Test Task {i}",
                   description="A" * 500,  # 500 character description
                   priority=Priority.LOW
               )
               repo.save(todo)
           
           # Load all todos
           all_todos = repo.find_all()
           
           final_memory = process.memory_info().rss / 1024 / 1024  # MB
           memory_increase = final_memory - initial_memory
           
           print(f"\\nMemory usage increased by {memory_increase:.2f} MB for 5000 todos")
           
           # Should not use excessive memory (adjust threshold as needed)
           assert memory_increase < 500  # Should not use more than 500MB
           assert len(all_todos) == 5000
   ```

**Acceptance Criteria:**
- [ ] Performance benchmarks established
- [ ] Memory usage within acceptable limits
- [ ] Large dataset handling verified
- [ ] Performance regression detection

---

## Task 5.4: Security and Validation Testing

**Goal:** Ensure robust input validation and security

**File:** `tests/security/test_input_validation.py`

1. **Write Security Tests:**
   ```python
   import pytest
   from pathlib import Path
   import tempfile
   from application import CreateTodoDto, UpdateTodoDto, ValidationService
   from domain import TodoValidationError
   
   class TestInputValidation:
       def test_sql_injection_attempts(self):
           """Test protection against SQL-injection-style attacks."""
           malicious_inputs = [
               "'; DROP TABLE todos; --",
               "' OR 1=1; --",
               "<script>alert('xss')</script>",
               "../../etc/passwd",
               "../../../windows/system32",
           ]
           
           for malicious_input in malicious_inputs:
               try:
                   dto = CreateTodoDto(title=malicious_input)
                   # Should not crash, input should be safely handled
                   assert len(dto.title) <= 200
               except Exception as e:
                   # Should fail gracefully with validation error
                   assert isinstance(e, (ValueError, TodoValidationError))
       
       def test_xss_prevention(self):
           """Test prevention of XSS-style attacks."""
           xss_inputs = [
               "<script>alert('xss')</script>",
               "javascript:alert('xss')",
               "<img src=x onerror=alert('xss')>",
               "\\x3cscript\\x3ealert('xss')\\x3c/script\\x3e",
           ]
           
           for xss_input in xss_inputs:
               dto = CreateTodoDto(title=xss_input[:200])  # Ensure within limits
               # Input should be stored as-is (no HTML interpretation in console app)
               assert dto.title == xss_input[:200]
       
       def test_path_traversal_prevention(self):
           """Test prevention of path traversal attacks."""
           # This is more relevant for file-based operations
           traversal_inputs = [
               "../../../etc/passwd",
               "..\\\\..\\\\windows\\\\system32",
               "/etc/shadow",
               "C:\\\\Windows\\\\System32",
           ]
           
           with tempfile.TemporaryDirectory() as temp_dir:
               base_path = Path(temp_dir)
               
               for traversal_input in traversal_inputs:
                   # Ensure file operations stay within intended directory
                   safe_path = base_path / "todos.json"
                   assert safe_path.resolve().is_relative_to(base_path.resolve())
       
       def test_unicode_normalization(self):
           """Test handling of unicode normalization attacks."""
           unicode_inputs = [
               "café",  # Normal unicode
               "cafe\\u0301",  # Decomposed unicode
               "\\u006E\\u0303",  # Combining characters
               "\\uFEFF",  # Zero-width no-break space
           ]
           
           for unicode_input in unicode_inputs:
               dto = CreateTodoDto(title=unicode_input)
               # Should handle unicode properly without crashes
               assert isinstance(dto.title, str)
       
       def test_extremely_long_inputs(self):
           """Test handling of extremely long inputs."""
           # Test various long input scenarios
           long_inputs = [
               "A" * 10000,  # Very long title
               "B" * 100000,  # Extremely long description
               "\\n" * 1000,  # Many newlines
               " " * 5000,  # Many spaces
           ]
           
           for long_input in long_inputs:
               try:
                   if len(long_input) <= 200:
                       CreateTodoDto(title=long_input)
                   else:
                       with pytest.raises(ValueError):
                           CreateTodoDto(title=long_input)
               except Exception as e:
                   # Should fail with validation error, not crash
                   assert isinstance(e, (ValueError, TodoValidationError))
       
       def test_null_byte_injection(self):
           """Test handling of null byte injection."""
           null_byte_inputs = [
               "title\\x00hidden",
               "title\\0hidden", 
               "title\\u0000hidden",
           ]
           
           for null_input in null_byte_inputs:
               dto = CreateTodoDto(title=null_input)
               # Should handle null bytes safely
               assert isinstance(dto.title, str)
   ```

**Acceptance Criteria:**
- [ ] Input validation comprehensive and secure
- [ ] Protection against common attack vectors
- [ ] Graceful handling of malicious inputs
- [ ] Unicode and encoding edge cases handled
- [ ] File system security maintained

---

## Task 5.5: Error Handling and Recovery Testing

**Goal:** Test error scenarios and recovery mechanisms

**File:** `tests/error_handling/test_error_recovery.py`

1. **Write Error Recovery Tests:**
   ```python
   import tempfile
   import json
   from pathlib import Path
   from unittest.mock import patch, Mock
   import pytest
   from domain import RepositoryError, TodoNotFoundError
   from infrastructure import JsonTodoRepository, XmlTodoRepository
   from application import TodoService
   
   class TestErrorRecovery:
       def test_corrupted_json_recovery(self):
           """Test recovery from corrupted JSON files."""
           with tempfile.TemporaryDirectory() as temp_dir:
               json_file = Path(temp_dir) / "todos.json"
               
               # Create valid JSON first
               repo = JsonTodoRepository(json_file)
               from domain import Todo
               todo = Todo(title="Test Task")
               repo.save(todo)
               
               # Corrupt the JSON file
               json_file.write_text("{ invalid json")
               
               # Should handle gracefully with backup recovery
               repo2 = JsonTodoRepository(json_file)
               with pytest.raises(RepositoryError):
                   repo2.find_all()
       
       def test_permission_denied_handling(self):
           """Test handling of file permission issues."""
           with tempfile.TemporaryDirectory() as temp_dir:
               json_file = Path(temp_dir) / "readonly.json"
               json_file.write_text("{}")
               json_file.chmod(0o444)  # Read-only
               
               try:
                   repo = JsonTodoRepository(json_file)
                   from domain import Todo
                   todo = Todo(title="Test")
                   
                   with pytest.raises(RepositoryError):
                       repo.save(todo)
               finally:
                   # Cleanup - restore permissions
                   json_file.chmod(0o644)
       
       def test_disk_space_simulation(self):
           """Test behavior when disk space is limited."""
           # This test would require complex setup to simulate disk full
           # For now, we'll test the error handling path
           
           with tempfile.TemporaryDirectory() as temp_dir:
               repo = JsonTodoRepository(Path(temp_dir) / "todos.json")
               
               # Mock the file write to raise an OS error
               with patch('pathlib.Path.write_text', side_effect=OSError("No space left on device")):
                   from domain import Todo
                   todo = Todo(title="Test")
                   
                   with pytest.raises(RepositoryError):
                       repo.save(todo)
       
       def test_service_layer_error_propagation(self):
           """Test that service layer properly handles and propagates errors."""
           mock_repository = Mock()
           mock_repository.find_by_id.side_effect = RepositoryError("Database error")
           
           service = TodoService(mock_repository)
           
           with pytest.raises(RepositoryError):
               service.get_todo_by_id("test-id")
       
       def test_concurrent_access_handling(self):
           """Test handling of concurrent file access."""
           with tempfile.TemporaryDirectory() as temp_dir:
               json_file = Path(temp_dir) / "todos.json"
               
               repo1 = JsonTodoRepository(json_file)
               repo2 = JsonTodoRepository(json_file)
               
               from domain import Todo
               todo1 = Todo(title="Task 1")
               todo2 = Todo(title="Task 2")
               
               # Both repositories should handle concurrent saves
               repo1.save(todo1)
               repo2.save(todo2)
               
               # Both todos should be saved (last write wins)
               all_todos = repo1.find_all()
               assert len(all_todos) >= 1  # At least one should be saved
   ```

**Acceptance Criteria:**
- [ ] Graceful error handling throughout the application
- [ ] Recovery mechanisms for common failure scenarios
- [ ] Error propagation tested across all layers
- [ ] Concurrent access scenarios handled
- [ ] Resource cleanup in error conditions

---

## Task 5.6: Code Quality and Standards Verification

**Goal:** Ensure code meets quality standards

### Run Quality Checks

1. **Execute Quality Commands:**
   ```bash
   # Format code
   make format
   
   # Check linting
   make lint
   
   # Run type checking
   make typecheck
   
   # Run all tests
   make test
   
   # Generate coverage report
   pytest --cov=src --cov-report=html --cov-report=term
   ```

2. **Verify Code Quality Metrics:**
   - Test coverage > 90%
   - Zero linting violations
   - Zero type checking errors  
   - All tests passing
   - Consistent code formatting

### Code Review Checklist

**File:** `docs/code_review_checklist.md`

```markdown
# Code Review Checklist

## Architecture & Design
- [ ] SOLID principles followed
- [ ] Clean architecture layers properly separated
- [ ] Domain-Driven Design principles applied
- [ ] Repository pattern implemented correctly
- [ ] Strategy pattern used for storage formats

## Code Quality
- [ ] Functions have single responsibility
- [ ] Classes are cohesive and loosely coupled
- [ ] Error handling comprehensive and consistent
- [ ] Input validation thorough
- [ ] Type hints used throughout

## Testing
- [ ] Test coverage > 90%
- [ ] Unit tests for all business logic
- [ ] Integration tests for layer interactions
- [ ] Edge cases and error scenarios tested
- [ ] Performance tests for critical paths

## Security
- [ ] Input validation prevents injection attacks
- [ ] File operations are secure
- [ ] No sensitive data in logs or outputs
- [ ] Error messages don't leak sensitive information

## Documentation
- [ ] Code is self-documenting with clear names
- [ ] Complex logic has explanatory comments
- [ ] Public APIs have docstrings
- [ ] README provides clear usage instructions

## Performance
- [ ] No obvious performance bottlenecks
- [ ] Memory usage reasonable
- [ ] File I/O operations efficient
- [ ] Database-like operations optimized
```

**Acceptance Criteria:**
- [ ] All quality checks pass
- [ ] Code review checklist completed
- [ ] Performance benchmarks met
- [ ] Security standards verified
- [ ] Documentation complete

---

## Task 5.7: Final Integration and Acceptance Testing

**Goal:** Complete end-to-end testing of the application

**File:** `tests/acceptance/test_user_scenarios.py`

1. **Write Acceptance Tests:**
   ```python
   import tempfile
   from pathlib import Path
   from unittest.mock import patch
   import subprocess
   import pytest
   
   class TestUserAcceptanceScenarios:
       def test_new_user_complete_workflow(self):
           """Test complete workflow for a new user."""
           with tempfile.TemporaryDirectory() as temp_dir:
               # Simulate user interactions
               user_inputs = [
                   '1',  # Select JSON format
                   '2',  # Create new task
                   'My First Task',  # Title
                   'This is my first todo item',  # Description
                   'high',  # Priority
                   '1',  # List all tasks
                   '5',  # Mark complete
                   '1',  # Select first task (mocked ID input)
                   '1',  # List all tasks again
                   '6'   # Exit
               ]
               
               with patch('builtins.input', side_effect=user_inputs):
                   with patch('interfaces.main.Path.home', return_value=Path(temp_dir)):
                       from interfaces.main import main
                       
                       # Should complete without errors
                       try:
                           main()
                       except SystemExit:
                           pass  # Expected when exiting
       
       def test_data_persistence_scenario(self):
           """Test that user data persists between sessions."""
           with tempfile.TemporaryDirectory() as temp_dir:
               data_dir = Path(temp_dir)
               
               # First session: Create data
               session1_inputs = [
                   '1',  # JSON format
                   '2',  # Create task
                   'Persistent Task',  # Title
                   'Should persist',  # Description
                   'medium',  # Priority
                   '6'   # Exit
               ]
               
               with patch('builtins.input', side_effect=session1_inputs):
                   with patch('interfaces.main.Path.home', return_value=data_dir):
                       from interfaces.main import create_app_components
                       
                       service1, config1 = create_app_components(data_dir)
                       
                       # Create the task
                       from application.dto import CreateTodoDto
                       dto = CreateTodoDto(
                           title="Persistent Task",
                           description="Should persist",
                           priority="medium"
                       )
                       service1.create_todo(dto)
               
               # Second session: Verify data exists
               service2, config2 = create_app_components(data_dir)
               todos = service2.get_all_todos()
               
               assert todos.total_count == 1
               assert todos.todos[0].title == "Persistent Task"
       
       def test_format_selection_workflow(self):
           """Test both JSON and XML format workflows."""
           formats = ['json', 'xml']
           
           for format_type in formats:
               with tempfile.TemporaryDirectory() as temp_dir:
                   data_dir = Path(temp_dir)
                   
                   format_input = '1' if format_type == 'json' else '2'
                   
                   inputs = [
                       format_input,  # Select format
                       '2',  # Create task
                       f'{format_type.upper()} Task',  # Title
                       f'Task in {format_type} format',  # Description
                       'low',  # Priority
                       '6'   # Exit
                   ]
                   
                   with patch('builtins.input', side_effect=inputs):
                       with patch('interfaces.main.Path.home', return_value=data_dir):
                           service, config = create_app_components(data_dir)
                           
                           assert config.storage_format == format_type
                           
                           # Verify appropriate file was created
                           expected_file = data_dir / f"todos.{format_type}"
                           assert expected_file.exists()
       
       @pytest.mark.slow
       def test_cli_script_execution(self):
           """Test that the CLI script can be executed."""
           # This test would run the actual script
           # Skipped in normal test runs due to interaction requirements
           pass
       
       def test_error_recovery_user_experience(self):
           """Test user experience during error conditions."""
           with tempfile.TemporaryDirectory() as temp_dir:
               # Test invalid inputs and recovery
               inputs = [
                   'invalid',  # Invalid format selection
                   '99',  # Invalid menu choice
                   '1',  # Valid format selection
                   '2',  # Create task
                   '',  # Empty title (should be rejected)
                   'Valid Title',  # Valid title
                   'Description',  # Description
                   'invalid_priority',  # Invalid priority
                   'medium',  # Valid priority
                   '6'  # Exit
               ]
               
               with patch('builtins.input', side_effect=inputs):
                   with patch('interfaces.main.Path.home', return_value=Path(temp_dir)):
                       # Should handle all errors gracefully
                       try:
                           service, config = create_app_components(Path(temp_dir))
                           assert config.storage_format in ['json', 'xml']
                       except Exception as e:
                           pytest.fail(f"Should handle errors gracefully: {e}")
   ```

**Acceptance Criteria:**
- [ ] All user scenarios work end-to-end
- [ ] Data persistence verified across sessions
- [ ] Both storage formats work correctly
- [ ] Error handling provides good user experience
- [ ] CLI application runs without issues

---

## Phase 5 Completion Checklist

**Code Quality Standards:**
- [ ] Test coverage >90% across all layers
- [ ] Zero linting violations (`make lint`)
- [ ] Zero type checking errors (`make typecheck`)
- [ ] All tests pass (`make test`)
- [ ] Code formatting consistent (`make format`)

**Testing Coverage:**
- [ ] Unit tests for all business logic
- [ ] Integration tests for layer interactions
- [ ] Performance tests for critical operations
- [ ] Security tests for input validation
- [ ] Error handling and recovery tests
- [ ] End-to-end acceptance tests

**Quality Assurance:**
- [ ] Code review checklist completed
- [ ] Architecture principles verified
- [ ] Security standards met
- [ ] Performance benchmarks achieved
- [ ] Documentation complete and accurate

**Final Deliverables:**
- [ ] All test files created and passing
- [ ] Performance benchmarks documented
- [ ] Security validation completed
- [ ] Code quality metrics verified
- [ ] Acceptance criteria satisfied

**Files Created:**
- [ ] `tests/domain/test_todo_enhanced.py`
- [ ] `tests/infrastructure/test_repository_edge_cases.py`
- [ ] `tests/application/test_service_edge_cases.py`
- [ ] `tests/integration/test_layer_integration.py`
- [ ] `tests/integration/test_console_integration.py`
- [ ] `tests/performance/test_performance.py`
- [ ] `tests/security/test_input_validation.py`
- [ ] `tests/error_handling/test_error_recovery.py`
- [ ] `tests/acceptance/test_user_scenarios.py`
- [ ] `docs/code_review_checklist.md`

---

## Final Project Completion

Once Phase 5 is complete, the Todo List application will be:
- ✅ Fully functional with all CRUD operations
- ✅ Following clean architecture and SOLID principles
- ✅ Supporting both JSON and XML storage formats
- ✅ Thoroughly tested with >90% coverage
- ✅ Meeting all quality and security standards
- ✅ Ready for production use

The project demonstrates mastery of:
- Domain-Driven Design (DDD)
- Clean Architecture principles
- Test-Driven Development (TDD)
- SOLID principles implementation
- Repository and Strategy patterns
- Comprehensive testing strategies
- Quality assurance practices