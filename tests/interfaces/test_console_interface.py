from unittest.mock import Mock, patch
from io import StringIO
from datetime import datetime

import pytest

from src.interfaces.console_interface import ConsoleInterface
from src.application import TodoService
from src.application.dto import TodoResponseDto, TodoListDto


@pytest.fixture
def mock_service():
    return Mock(spec=TodoService)


@pytest.fixture 
def console_interface(mock_service):
    return ConsoleInterface(mock_service)


class TestConsoleInterface:
    def test_display_main_menu(self, console_interface):
        with patch('src.interfaces.console_utils.ConsoleUtils.display_menu') as mock_display:
            console_interface._display_main_menu()
            mock_display.assert_called_once()

    def test_create_todo_success(self, console_interface, mock_service):
        todo_response = TodoResponseDto(
            id="123", title="Test Task", description=None,
            completed=False, priority="medium", 
            created_at=datetime.now(), updated_at=None
        )
        mock_service.create_todo.return_value = todo_response
        
        with patch('builtins.input', side_effect=['Test Task', '', 'medium']):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = console_interface._create_todo()
                
                mock_service.create_todo.assert_called_once()
                assert result is True

    def test_create_todo_empty_title(self, console_interface):
        with patch('builtins.input', return_value=''):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = console_interface._create_todo()
                assert result is False

    def test_list_todos_empty(self, console_interface, mock_service):
        empty_list = TodoListDto(todos=[], total_count=0, pending_count=0, completed_count=0)
        mock_service.get_all_todos.return_value = empty_list
        
        with patch('sys.stdout', StringIO()):  # Suppress output
            result = console_interface._list_todos()
            assert result is True

    def test_list_todos_with_data(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123", title="Test Task", description=None,
            completed=False, priority="medium", 
            created_at=datetime.now(), updated_at=None
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_all_todos.return_value = todo_list
        
        with patch('builtins.input', return_value='5'):  # Back to main menu
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = console_interface._list_todos()
                assert result is True

    def test_select_todo_valid_id(self, console_interface, mock_service):
        todo = TodoResponseDto(
            id="123e4567-e89b-12d3-a456-426614174000", title="Test Task", description=None,
            completed=False, priority="medium", 
            created_at=datetime.now(), updated_at=None
        )
        todo_list = TodoListDto(todos=[todo], total_count=1, pending_count=1, completed_count=0)
        mock_service.get_all_todos.return_value = todo_list
        
        with patch('builtins.input', return_value='123e4567'):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = console_interface._select_todo("test")
                assert result == "123e4567-e89b-12d3-a456-426614174000"

    def test_select_todo_no_todos(self, console_interface, mock_service):
        empty_list = TodoListDto(todos=[], total_count=0, pending_count=0, completed_count=0)
        mock_service.get_all_todos.return_value = empty_list
        
        with patch('sys.stdout', StringIO()):  # Suppress output
            result = console_interface._select_todo("test")
            assert result is None

    def test_exit_application_confirmed(self, console_interface):
        with patch('builtins.input', return_value='y'):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = console_interface._exit_application()
                assert result is True
                assert console_interface._running is False

    def test_exit_application_cancelled(self, console_interface):
        with patch('builtins.input', return_value='n'):
            with patch('sys.stdout', StringIO()):  # Suppress output
                result = console_interface._exit_application()
                assert result is True
                assert console_interface._running is True

    def test_handle_menu_choice(self, console_interface, mock_service):
        with patch.object(console_interface, '_list_todos', return_value=True) as mock_list:
            with patch('src.interfaces.console_utils.ConsoleUtils.pause'):
                console_interface._handle_menu_choice(1)
                mock_list.assert_called_once()