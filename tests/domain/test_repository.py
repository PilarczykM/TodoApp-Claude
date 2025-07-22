import pytest

from src.domain.repository import TodoRepository


class TestTodoRepository:
    def test_repository_interface_methods(self):
        # Test that repository interface defines all required methods
        methods = dir(TodoRepository)
        assert 'save' in methods
        assert 'find_by_id' in methods
        assert 'find_all' in methods
        assert 'delete' in methods
        assert 'exists' in methods
        assert 'update' in methods
        assert 'count' in methods

    def test_abstract_methods(self):
        # Test that repository cannot be instantiated
        with pytest.raises(TypeError):
            TodoRepository()

    def test_is_abstract_base_class(self):
        # Verify it's an abstract base class
        assert hasattr(TodoRepository, '__abstractmethods__')
        assert len(TodoRepository.__abstractmethods__) > 0
