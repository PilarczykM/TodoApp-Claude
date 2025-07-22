from unittest.mock import patch
from io import StringIO

import pytest

from src.interfaces.format_selector import FormatSelector


class TestFormatSelector:
    def test_select_format_json(self):
        with patch('builtins.input', return_value='1'):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = FormatSelector.select_storage_format()
                assert result == "json"

    def test_select_format_xml(self):
        with patch('builtins.input', return_value='2'):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = FormatSelector.select_storage_format()
                assert result == "xml"

    def test_select_format_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['invalid', '99', '1']):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = FormatSelector.select_storage_format()
                assert result == "json"

    def test_display_format_info(self):
        output = StringIO()
        with patch('sys.stdout', output):
            FormatSelector.display_format_info()
        
        result = output.getvalue()
        assert "JSON" in result
        assert "XML" in result
        assert "Storage Format Information:" in result