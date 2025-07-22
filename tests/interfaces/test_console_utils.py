from io import StringIO
import sys
from unittest.mock import patch
from datetime import datetime

import pytest

from src.interfaces.console_utils import ConsoleUtils
from src.application.dto import TodoResponseDto


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
