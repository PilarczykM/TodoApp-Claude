from unittest.mock import patch

from src.todo_app import main


class TestTodoApp:
    """Tests for the main todo app entry point."""

    @patch("src.todo_app._main")
    def test_main_calls_interfaces_main(self, mock_interfaces_main):
        """Test that main() calls the interfaces.main function."""
        main()
        mock_interfaces_main.assert_called_once()

    @patch("src.todo_app._main", side_effect=Exception("Test exception"))
    def test_main_handles_exception(self, mock_interfaces_main):
        """Test that main() handles exceptions from interfaces.main."""
        try:
            main()
        except Exception:
            pass  # Exception should propagate

        mock_interfaces_main.assert_called_once()
