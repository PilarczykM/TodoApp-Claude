from io import StringIO
from unittest.mock import patch

from src.interfaces.format_selector import FormatSelector


class TestFormatSelector:
    def test_select_format_json(self):
        with patch("builtins.input", return_value="1"):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = FormatSelector.select_storage_format()
                assert result == "json"

    def test_select_format_xml(self):
        with patch("builtins.input", return_value="2"):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = FormatSelector.select_storage_format()
                assert result == "xml"

    def test_select_format_invalid_then_valid(self):
        with patch("builtins.input", side_effect=["invalid", "99", "1"]):
            with patch("sys.stdout", StringIO()):  # Suppress output
                result = FormatSelector.select_storage_format()
                assert result == "json"

    def test_display_format_info(self):
        output = StringIO()
        with patch("sys.stdout", output):
            FormatSelector.display_format_info()

        result = output.getvalue()
        assert "JSON" in result
        assert "XML" in result
        assert "Storage Format Information:" in result

    def test_select_format_with_exception_handling(self):
        # Test the error handling path in select_storage_format
        with patch(
            "src.interfaces.console_utils.ConsoleUtils.get_menu_choice", side_effect=[Exception("Test error"), 1]
        ):
            with patch("src.interfaces.console_utils.ConsoleUtils.display_error") as mock_error:
                with patch("sys.stdout", StringIO()):  # Suppress output
                    result = FormatSelector.select_storage_format()
                    assert result == "json"
                    mock_error.assert_called_with("Invalid selection: Test error")
