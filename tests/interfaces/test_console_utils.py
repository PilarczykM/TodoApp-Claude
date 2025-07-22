from datetime import datetime
from io import StringIO
from unittest.mock import patch

from src.application.dto import TodoResponseDto, TodoListDto
from src.interfaces.console_utils import ConsoleUtils


class TestConsoleUtils:
    def test_display_header(self):
        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_header("Test Title")

        result = output.getvalue()
        assert "Test Title" in result
        assert "=" in result

    def test_display_menu(self):
        output = StringIO()
        menu_options = ["Option 1", "Option 2", "Exit"]

        with patch("sys.stdout", output):
            ConsoleUtils.display_menu("Test Menu", menu_options)

        result = output.getvalue()
        assert "Test Menu" in result
        assert "1. Option 1" in result
        assert "2. Option 2" in result
        assert "3. Exit" in result

    def test_format_todo_display(self):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Task",
            description="Test description",
            completed=False,
            priority="high",
            created_at=datetime.now(),
            updated_at=None,
        )

        result = ConsoleUtils.format_todo_display(todo)
        assert "Test Task" in result
        assert "▲" in result  # High priority symbol
        assert "[ ]" in result  # Incomplete task

    def test_format_todo_display_completed(self):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Completed Task",
            description="Test description",
            completed=True,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )

        result = ConsoleUtils.format_todo_display(todo)
        assert "Completed Task" in result
        assert "●" in result  # Medium priority symbol
        assert "[✓]" in result  # Completed task

    def test_get_user_input(self):
        with patch("builtins.input", return_value="test input"):
            result = ConsoleUtils.get_user_input("Enter something")
            assert result == "test input"

    def test_get_user_input_with_default(self):
        with patch("builtins.input", return_value=""):
            result = ConsoleUtils.get_user_input("Enter something", "default_value")
            assert result == "default_value"

    def test_get_user_choice_valid(self):
        with patch("builtins.input", return_value="yes"):
            result = ConsoleUtils.get_user_choice("Choose", ["yes", "no"])
            assert result == "yes"

    def test_get_user_choice_case_insensitive(self):
        with patch("builtins.input", return_value="YES"):
            result = ConsoleUtils.get_user_choice("Choose", ["yes", "no"])
            assert result == "yes"

    def test_get_menu_choice_valid(self):
        with patch("builtins.input", return_value="2"):
            result = ConsoleUtils.get_menu_choice(3)
            assert result == 2

    def test_get_menu_choice_invalid_then_valid(self):
        with patch("builtins.input", side_effect=["0", "4", "2"]):
            with patch("sys.stdout", StringIO()):  # Suppress error messages
                result = ConsoleUtils.get_menu_choice(3)
                assert result == 2

    def test_confirm_action_yes(self):
        with patch("builtins.input", return_value="y"):
            result = ConsoleUtils.confirm_action("Are you sure?")
            assert result is True

    def test_confirm_action_no(self):
        with patch("builtins.input", return_value="n"):
            result = ConsoleUtils.confirm_action("Are you sure?")
            assert result is False

    def test_display_error(self):
        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_error("Test error")

        result = output.getvalue()
        assert "❌ Error: Test error" in result

    def test_display_success(self):
        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_success("Success message")

        result = output.getvalue()
        assert "✅ Success message" in result

    def test_display_info(self):
        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_info("Info message")

        result = output.getvalue()
        assert "ℹ️  Info message" in result

    def test_display_todos_empty(self):
        empty_list = TodoListDto(todos=[], total_count=0, pending_count=0, completed_count=0)

        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_todos(empty_list)

        result = output.getvalue()
        assert "No todos found." in result

    def test_display_todos_with_data(self):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Todo",
            description="Test description",
            completed=False,
            priority="medium",
            created_at=datetime.now(),
            updated_at=None,
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)

        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_todos(todo_list)

        result = output.getvalue()
        assert "Test Todo" in result
        assert "1 total" in result
        assert "1 pending" in result

    def test_display_todo_details(self):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Detailed Task",
            description="Detailed description",
            completed=True,
            priority="high",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 2, 12, 0, 0),
        )

        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_todo_details(todo)

        result = output.getvalue()
        assert "Detailed Task" in result
        assert "Detailed description" in result
        assert "Completed" in result
        assert "HIGH" in result
        assert "2023-01-01" in result
        assert "2023-01-02" in result

    def test_display_todo_details_no_description_no_updated(self):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000",
            title="Simple Task",
            description=None,
            completed=False,
            priority="low",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=None,
        )

        output = StringIO()
        with patch("sys.stdout", output):
            ConsoleUtils.display_todo_details(todo)

        result = output.getvalue()
        assert "Simple Task" in result
        assert "No description" in result
        assert "Pending" in result
        assert "LOW" in result

    def test_clear_screen(self):
        with patch("os.system") as mock_system:
            ConsoleUtils.clear_screen()
            mock_system.assert_called_once()

    def test_pause(self):
        with patch("builtins.input", return_value=""):
            ConsoleUtils.pause()  # Should not raise any exceptions
