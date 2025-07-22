from datetime import datetime
from io import StringIO
from unittest.mock import Mock, patch

import pytest

from src.application import TodoService
from src.application.dto import TodoListDto, TodoResponseDto
from src.domain import Priority, RepositoryError, TodoNotFoundError, TodoValidationError
from src.interfaces.console_interface import ConsoleInterface


@pytest.fixture
def mock_service():
    return Mock(spec=TodoService)


@pytest.fixture
def console_interface(mock_service):
    return ConsoleInterface(mock_service)


class TestConsoleInterface:
    def test_display_main_menu(self, console_interface):
        with patch("src.interfaces.console_utils.ConsoleUtils.display_menu") as mock_display:
            console_interface._display_main_menu()
            mock_display.assert_called_once()

    def test_create_todo_success(self, console_interface, mock_service):
        todo_response = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        mock_service.create_todo.return_value = todo_response

        with patch("builtins.input", side_effect=["Test Task", "", "medium"]):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = console_interface._create_todo()

                mock_service.create_todo.assert_called_once()
                assert result is True

    def test_create_todo_empty_title(self, console_interface):
        with patch("builtins.input", return_value=""):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = console_interface._create_todo()
                assert result is False

    def test_list_todos_empty(self, console_interface, mock_service):
        empty_list = TodoListDto(todos=[], total_count=0, pending_count=0, completed_count=0)
        mock_service.get_all_todos.return_value = empty_list

        with patch("sys.stdout", StringIO()):  # Suppress output
            result = console_interface._list_todos()
            assert result is True

    def test_list_todos_with_data(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_all_todos.return_value = todo_list

        with patch("builtins.input", return_value="5"):  # Back to main menu
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = console_interface._list_todos()
                assert result is True

    def test_select_todo_valid_id(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_all_todos.return_value = todo_list

        with patch("builtins.input", return_value="123e4567"):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = console_interface._select_todo("test")
                assert result == "123e4567-e89b-12d3-a456-426614174000"

    def test_select_todo_no_todos(self, console_interface, mock_service):
        empty_list = TodoListDto(todos=[], total_count=0, pending_count=0, completed_count=0)
        mock_service.get_all_todos.return_value = empty_list

        with patch("sys.stdout", StringIO()):  # Suppress output
            result = console_interface._select_todo("test")
            assert result is None

    def test_exit_application_confirmed(self, console_interface):
        with patch("builtins.input", return_value="y"):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = console_interface._exit_application()
                assert result is True
                assert console_interface._running is False

    def test_exit_application_cancelled(self, console_interface):
        with patch("builtins.input", return_value="n"):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = console_interface._exit_application()
                assert result is True
                assert console_interface._running is True

    def test_handle_menu_choice(self, console_interface, mock_service):
        with patch.object(console_interface, "_list_todos", return_value=True) as mock_list:
            with patch("src.interfaces.console_utils.ConsoleUtils.pause"):
                console_interface._handle_menu_choice(1)
                mock_list.assert_called_once()

    # Test all menu choices
    def test_handle_menu_choice_list_todos(self, console_interface):
        with patch.object(console_interface, "_list_todos", return_value=True) as mock_action:
            with patch("src.interfaces.console_utils.ConsoleUtils.pause"):
                console_interface._handle_menu_choice(1)
                mock_action.assert_called_once()

    def test_handle_menu_choice_create_todo(self, console_interface):
        with patch.object(console_interface, "_create_todo", return_value=True) as mock_action:
            with patch("src.interfaces.console_utils.ConsoleUtils.pause"):
                console_interface._handle_menu_choice(2)
                mock_action.assert_called_once()

    def test_handle_menu_choice_update_todo(self, console_interface):
        with patch.object(console_interface, "_update_todo", return_value=True) as mock_action:
            with patch("src.interfaces.console_utils.ConsoleUtils.pause"):
                console_interface._handle_menu_choice(3)
                mock_action.assert_called_once()

    def test_handle_menu_choice_delete_todo(self, console_interface):
        with patch.object(console_interface, "_delete_todo", return_value=True) as mock_action:
            with patch("src.interfaces.console_utils.ConsoleUtils.pause"):
                console_interface._handle_menu_choice(4)
                mock_action.assert_called_once()

    def test_handle_menu_choice_toggle_completion(self, console_interface):
        with patch.object(console_interface, "_toggle_completion", return_value=True) as mock_action:
            with patch("src.interfaces.console_utils.ConsoleUtils.pause"):
                console_interface._handle_menu_choice(5)
                mock_action.assert_called_once()

    def test_handle_menu_choice_exit(self, console_interface):
        with patch.object(console_interface, "_exit_application", return_value=True) as mock_action:
            console_interface._handle_menu_choice(6)
            mock_action.assert_called_once()

    def test_handle_menu_choice_invalid(self, console_interface):
        console_interface._handle_menu_choice(99)  # Should do nothing

    def test_handle_menu_choice_no_pause_on_exit(self, console_interface):
        with patch.object(console_interface, "_exit_application", return_value=True):
            with patch("src.interfaces.console_utils.ConsoleUtils.pause") as mock_pause:
                console_interface._handle_menu_choice(6)
                mock_pause.assert_not_called()

    # Test run method with various scenarios
    def test_run_keyboard_interrupt(self, console_interface):
        with patch("src.interfaces.console_utils.ConsoleUtils.display_header"):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_info"):
                with patch.object(console_interface, "_display_main_menu"):
                    with patch(
                        "src.interfaces.console_utils.ConsoleUtils.get_menu_choice", side_effect=KeyboardInterrupt
                    ):
                        with patch("src.interfaces.console_utils.ConsoleUtils.display_info") as mock_display:
                            console_interface.run()
                            mock_display.assert_called_with("Goodbye!")

    def test_run_unexpected_exception(self, console_interface):
        with patch("src.interfaces.console_utils.ConsoleUtils.display_header"):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_info"):
                with patch.object(console_interface, "_display_main_menu"):
                    with patch(
                        "src.interfaces.console_utils.ConsoleUtils.get_menu_choice",
                        side_effect=[Exception("Test error"), KeyboardInterrupt],
                    ):
                        with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                            with patch("src.interfaces.console_utils.ConsoleUtils.pause"):
                                with patch("src.interfaces.console_utils.ConsoleUtils.display_info"):
                                    console_interface.run()
                                    mock_error.assert_called_with("Unexpected error: Test error")

    def test_run_normal_flow(self, console_interface):
        with patch("src.interfaces.console_utils.ConsoleUtils.display_header"):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_info"):
                with patch.object(console_interface, "_display_main_menu"):
                    with patch(
                        "src.interfaces.console_utils.ConsoleUtils.get_menu_choice", side_effect=[6, KeyboardInterrupt]
                    ):
                        with patch.object(console_interface, "_handle_menu_choice") as mock_handle:
                            console_interface.run()
                            mock_handle.assert_called_with(6)

    # Test list todos with filtering options
    def test_list_todos_filter_completed(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=True,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=0, completed_count=1)
        completed_list = TodoListDto(todos=[todo], total_count=1, pending_count=0, completed_count=1)

        mock_service.get_all_todos.return_value = todo_list
        mock_service.get_todos_by_status.return_value = completed_list

        with patch("builtins.input", return_value="2"):  # Show completed only
            with patch("sys.stdout", StringIO()):
                result = console_interface._list_todos()
                assert result is True
                mock_service.get_todos_by_status.assert_called_with(True)

    def test_list_todos_filter_pending(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        pending_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)

        mock_service.get_all_todos.return_value = todo_list
        mock_service.get_todos_by_status.return_value = pending_list

        with patch("builtins.input", return_value="3"):  # Show pending only
            with patch("sys.stdout", StringIO()):
                result = console_interface._list_todos()
                assert result is True
                mock_service.get_todos_by_status.assert_called_with(False)

    def test_list_todos_filter_by_priority(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="high",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_all_todos.return_value = todo_list

        with patch("builtins.input", return_value="4"):  # Show by priority
            with patch.object(console_interface, "_show_todos_by_priority") as mock_priority:
                with patch("sys.stdout", StringIO()):
                    result = console_interface._list_todos()
                    assert result is True
                    mock_priority.assert_called_once()

    def test_list_todos_repository_error(self, console_interface, mock_service):
        mock_service.get_all_todos.side_effect = RepositoryError("Database error")

        with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
            result = console_interface._list_todos()
            assert result is False
            mock_error.assert_called_with("Failed to load todos: Database error")

    # Test show todos by priority
    def test_show_todos_by_priority(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="High Priority Task",
            description=None,
            completed=False,
            priority="high",
            created_at=datetime.now(),
            updated_at=None,
        )
        filtered_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_todos_by_priority.return_value = filtered_list

        with patch("builtins.input", return_value="high"):
            with patch("sys.stdout", StringIO()):
                console_interface._show_todos_by_priority()
                mock_service.get_todos_by_priority.assert_called_with(Priority("high"))

    # Test create todo error scenarios
    def test_create_todo_validation_error(self, console_interface, mock_service):
        mock_service.create_todo.side_effect = TodoValidationError("Invalid data")

        with patch("builtins.input", side_effect=["Valid Title", "Description", "high"]):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                with patch("sys.stdout", StringIO()):
                    result = console_interface._create_todo()
                    assert result is False
                    mock_error.assert_called_with("Validation error: Invalid data")

    def test_create_todo_repository_error(self, console_interface, mock_service):
        mock_service.create_todo.side_effect = RepositoryError("Database error")

        with patch("builtins.input", side_effect=["Valid Title", "Description", "high"]):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                with patch("sys.stdout", StringIO()):
                    result = console_interface._create_todo()
                    assert result is False
                    mock_error.assert_called_with("Failed to create todo: Database error")

    # Test update todo scenarios
    def test_update_todo_success(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Original Title",
            description="Original Description",
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        updated_todo = TodoResponseDto(
            id="123",
            title="Updated Title",
            description="Original Description",
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.get_todo_by_id.return_value = todo
        mock_service.update_todo.return_value = updated_todo

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("builtins.input", side_effect=["Updated Title", "", ""]):
                with patch("src.interfaces.console_utils.ConsoleUtils.display_success") as mock_success:
                    with patch("sys.stdout", StringIO()):
                        result = console_interface._update_todo()
                        assert result is True
                        mock_success.assert_called_with("Task 'Updated Title' updated successfully!")

    def test_update_todo_no_selection(self, console_interface):
        with patch.object(console_interface, "_select_todo", return_value=None):
            result = console_interface._update_todo()
            assert result is False

    def test_update_todo_not_found_error(self, console_interface, mock_service):
        with patch.object(console_interface, "_select_todo", return_value="123"):
            mock_service.get_todo_by_id.side_effect = TodoNotFoundError("123")
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                result = console_interface._update_todo()
                assert result is False
                mock_error.assert_called_with("Todo not found")

    def test_update_todo_validation_error(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Original Title",
            description="Original Description",
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.get_todo_by_id.return_value = todo
        mock_service.update_todo.side_effect = TodoValidationError("Invalid data")

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("builtins.input", side_effect=["Updated Title", "", ""]):
                with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                    with patch("sys.stdout", StringIO()):
                        result = console_interface._update_todo()
                        assert result is False
                        mock_error.assert_called_with("Validation error: Invalid data")

    def test_update_todo_repository_error(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Original Title",
            description="Original Description",
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.get_todo_by_id.return_value = todo
        mock_service.update_todo.side_effect = RepositoryError("Database error")

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("builtins.input", side_effect=["Updated Title", "", ""]):
                with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                    with patch("sys.stdout", StringIO()):
                        result = console_interface._update_todo()
                        assert result is False
                        mock_error.assert_called_with("Failed to update todo: Database error")

    # Test delete todo scenarios
    def test_delete_todo_success_confirmed(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.get_todo_by_id.return_value = todo
        mock_service.delete_todo.return_value = True

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("builtins.input", return_value="y"):  # Confirm deletion
                with patch("src.interfaces.console_utils.ConsoleUtils.display_success") as mock_success:
                    with patch("sys.stdout", StringIO()):
                        result = console_interface._delete_todo()
                        assert result is True
                        mock_success.assert_called_with("Task deleted successfully!")

    def test_delete_todo_success_cancelled(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.get_todo_by_id.return_value = todo

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("builtins.input", return_value="n"):  # Cancel deletion
                with patch("src.interfaces.console_utils.ConsoleUtils.display_info") as mock_info:
                    with patch("sys.stdout", StringIO()):
                        result = console_interface._delete_todo()
                        assert result is True
                        mock_info.assert_called_with("Delete cancelled")

    def test_delete_todo_failed(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.get_todo_by_id.return_value = todo
        mock_service.delete_todo.return_value = False

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("builtins.input", return_value="y"):  # Confirm deletion
                with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                    with patch("sys.stdout", StringIO()):
                        result = console_interface._delete_todo()
                        assert result is False
                        mock_error.assert_called_with("Failed to delete task")

    def test_delete_todo_no_selection(self, console_interface):
        with patch.object(console_interface, "_select_todo", return_value=None):
            result = console_interface._delete_todo()
            assert result is False

    def test_delete_todo_not_found_error(self, console_interface, mock_service):
        with patch.object(console_interface, "_select_todo", return_value="123"):
            mock_service.get_todo_by_id.side_effect = TodoNotFoundError("123")
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                result = console_interface._delete_todo()
                assert result is False
                mock_error.assert_called_with("Todo not found")

    def test_delete_todo_repository_error(self, console_interface, mock_service):
        with patch.object(console_interface, "_select_todo", return_value="123"):
            mock_service.get_todo_by_id.side_effect = RepositoryError("Database error")
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                result = console_interface._delete_todo()
                assert result is False
                mock_error.assert_called_with("Failed to delete todo: Database error")

    # Test toggle completion scenarios
    def test_toggle_completion_success(self, console_interface, mock_service):
        updated_todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=True,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.toggle_completion.return_value = updated_todo

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_success") as mock_success:
                result = console_interface._toggle_completion()
                assert result is True
                mock_success.assert_called_with("Task 'Test Task' marked as completed!")

    def test_toggle_completion_to_pending(self, console_interface, mock_service):
        updated_todo = TodoResponseDto(
            id="123",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        mock_service.toggle_completion.return_value = updated_todo

        with patch.object(console_interface, "_select_todo", return_value="123"):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_success") as mock_success:
                result = console_interface._toggle_completion()
                assert result is True
                mock_success.assert_called_with("Task 'Test Task' marked as pending!")

    def test_toggle_completion_no_selection(self, console_interface):
        with patch.object(console_interface, "_select_todo", return_value=None):
            result = console_interface._toggle_completion()
            assert result is False

    def test_toggle_completion_not_found_error(self, console_interface, mock_service):
        with patch.object(console_interface, "_select_todo", return_value="123"):
            mock_service.toggle_completion.side_effect = TodoNotFoundError("123")
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                result = console_interface._toggle_completion()
                assert result is False
                mock_error.assert_called_with("Todo not found")

    def test_toggle_completion_repository_error(self, console_interface, mock_service):
        with patch.object(console_interface, "_select_todo", return_value="123"):
            mock_service.toggle_completion.side_effect = RepositoryError("Database error")
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                result = console_interface._toggle_completion()
                assert result is False
                mock_error.assert_called_with("Failed to update todo: Database error")

    # Test select todo scenarios
    def test_select_todo_short_id(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_all_todos.return_value = todo_list

        with patch("builtins.input", return_value="123"):  # Too short, less than 8 chars
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                with patch("sys.stdout", StringIO()):
                    result = console_interface._select_todo("test")
                    assert result is None
                    mock_error.assert_called_with("Todo not found with that ID")

    def test_select_todo_no_match(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Task",
            description=None,
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_all_todos.return_value = todo_list

        with patch("builtins.input", return_value="99999999"):  # No match
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                with patch("sys.stdout", StringIO()):
                    result = console_interface._select_todo("test")
                    assert result is None
                    mock_error.assert_called_with("Todo not found with that ID")

    def test_select_todo_repository_error(self, console_interface, mock_service):
        mock_service.get_all_todos.side_effect = RepositoryError("Database error")

        with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
            result = console_interface._select_todo("test")
            assert result is None
            mock_error.assert_called_with("Failed to load todos: Database error")
