import tempfile
from pathlib import Path
from unittest.mock import patch

from src.application.dto import CreateTodoDto, UpdateTodoDto
from src.interfaces.console_interface import ConsoleInterface
from src.interfaces.main import create_app_components


class TestFullApplication:
    """Integration tests for the complete todo application."""

    def test_application_component_creation_json(self):
        """Test application components are correctly created with JSON storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            with patch("src.interfaces.format_selector.FormatSelector.select_storage_format", return_value="json"):
                service, config = create_app_components(data_dir)

                assert config.storage_format == "json"
                assert service is not None

                # Test basic CRUD operations work
                dto = CreateTodoDto(title="Test Task", description="Test", priority="high")
                todo = service.create_todo(dto)

                assert todo.title == "Test Task"
                assert todo.priority == "high"

                # Verify persistence
                json_file = data_dir / "todos.json"
                assert json_file.exists()

    def test_application_component_creation_xml(self):
        """Test application components are correctly created with XML storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            with patch("src.interfaces.format_selector.FormatSelector.select_storage_format", return_value="xml"):
                service, config = create_app_components(data_dir)

                assert config.storage_format == "xml"
                assert service is not None

                # Test basic CRUD operations work
                dto = CreateTodoDto(title="XML Test Task", description="XML Test", priority="medium")
                todo = service.create_todo(dto)

                assert todo.title == "XML Test Task"
                assert todo.priority == "medium"

                # Verify persistence
                xml_file = data_dir / "todos.xml"
                assert xml_file.exists()

    def test_data_persistence_json(self):
        """Test data persistence with JSON format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            with patch("src.interfaces.format_selector.FormatSelector.select_storage_format", return_value="json"):
                # First session - create data
                service1, config1 = create_app_components(data_dir)
                dto = CreateTodoDto(title="Persistent Task", description="Test persistence", priority="low")
                todo1 = service1.create_todo(dto)

                # Second session - load existing data
                service2, config2 = create_app_components(data_dir)
                todo_list = service2.get_all_todos()

                assert todo_list.total_count == 1
                assert todo_list.todos[0].title == "Persistent Task"
                assert todo_list.todos[0].id == todo1.id

    def test_data_persistence_xml(self):
        """Test data persistence with XML format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            with patch("src.interfaces.format_selector.FormatSelector.select_storage_format", return_value="xml"):
                # First session - create data
                service1, config1 = create_app_components(data_dir)
                dto = CreateTodoDto(title="XML Persistent Task", description="XML Test persistence", priority="high")
                todo1 = service1.create_todo(dto)

                # Second session - load existing data
                service2, config2 = create_app_components(data_dir)
                todo_list = service2.get_all_todos()

                assert todo_list.total_count == 1
                assert todo_list.todos[0].title == "XML Persistent Task"
                assert todo_list.todos[0].id == todo1.id

    def test_full_crud_operations(self):
        """Test complete CRUD operations through the service layer."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            with patch("src.interfaces.format_selector.FormatSelector.select_storage_format", return_value="json"):
                service, config = create_app_components(data_dir)

                # Create
                dto = CreateTodoDto(title="CRUD Test", description="Test all operations", priority="medium")
                todo = service.create_todo(dto)
                todo_id = todo.id

                # Read
                retrieved_todo = service.get_todo_by_id(todo_id)
                assert retrieved_todo.title == "CRUD Test"

                # Update
                update_dto = UpdateTodoDto(title="Updated CRUD Test")
                updated_todo = service.update_todo(todo_id, update_dto)
                assert updated_todo.title == "Updated CRUD Test"

                # Toggle completion
                completed_todo = service.toggle_completion(todo_id)
                assert completed_todo.completed is True

                # List todos
                todo_list = service.get_all_todos()
                assert todo_list.total_count == 1
                assert todo_list.completed_count == 1
                assert todo_list.pending_count == 0

                # Delete
                success = service.delete_todo(todo_id)
                assert success is True

                final_list = service.get_all_todos()
                assert final_list.total_count == 0

    def test_console_interface_initialization(self):
        """Test console interface can be initialized with service."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            with patch("src.interfaces.format_selector.FormatSelector.select_storage_format", return_value="json"):
                service, config = create_app_components(data_dir)

                # Test console interface creation
                console = ConsoleInterface(service)
                assert console is not None
                assert console._service == service
                assert console._running is True

    def test_error_handling_invalid_format(self):
        """Test error handling during application initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            with patch(
                "src.interfaces.format_selector.FormatSelector.select_storage_format",
                side_effect=Exception("Test error"),
            ):
                with patch("src.interfaces.console_utils.ConsoleUtils.display_error"):
                    with patch("sys.exit") as mock_exit:
                        create_app_components(data_dir)
                        mock_exit.assert_called_with(1)
