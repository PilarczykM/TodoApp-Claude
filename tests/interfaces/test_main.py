from unittest.mock import Mock, patch
from pathlib import Path
import tempfile

import pytest

from src.interfaces.main import create_app_components, main


class TestMain:
    def test_create_app_components_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.interfaces.format_selector.FormatSelector.select_storage_format', return_value='json'):
                service, config = create_app_components(Path(temp_dir))
                
                assert service is not None
                assert config is not None
                assert config.storage_format == "json"

    def test_create_app_components_xml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.interfaces.format_selector.FormatSelector.select_storage_format', return_value='xml'):
                service, config = create_app_components(Path(temp_dir))
                
                assert service is not None
                assert config is not None
                assert config.storage_format == "xml"

    @patch('src.interfaces.console_interface.ConsoleInterface.run')
    @patch('src.interfaces.format_selector.FormatSelector.select_storage_format', return_value='json')
    def test_main_function(self, mock_format_select, mock_run):
        main()
        mock_format_select.assert_called_once()
        mock_run.assert_called_once()

    @patch('src.interfaces.console_interface.ConsoleInterface.run', side_effect=KeyboardInterrupt)
    @patch('src.interfaces.format_selector.FormatSelector.select_storage_format', return_value='json')
    @patch('src.interfaces.console_utils.ConsoleUtils.display_info')
    def test_main_function_keyboard_interrupt(self, mock_display_info, mock_format_select, mock_run):
        main()
        mock_display_info.assert_called_with("\nApplication interrupted by user")

    @patch('src.interfaces.format_selector.FormatSelector.select_storage_format', side_effect=Exception("Test error"))
    @patch('src.interfaces.console_utils.ConsoleUtils.display_error')
    @patch('sys.exit')
    def test_create_app_components_error(self, mock_exit, mock_display_error, mock_format_select):
        with tempfile.TemporaryDirectory() as temp_dir:
            create_app_components(Path(temp_dir))
            
            mock_display_error.assert_called_with("Failed to initialize application: Test error")
            mock_exit.assert_called_with(1)