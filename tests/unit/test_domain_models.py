import pytest
from pydantic import ValidationError

from src.todo_app.domain.models import Task, TaskFilters


class TestTask:
    def test_create_task_with_valid_data(self):
        """Test creating a task with valid data."""
        task = Task(
            title="Test Task",
            description="Test Description",
            category="Test Category"
        )
        
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.category == "Test Category"
        assert task.completed is False
        assert task.id is not None
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_with_minimal_data(self):
        """Test creating a task with minimal required data."""
        task = Task(title="Minimal Task")
        
        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.category == "General"
        assert task.completed is False

    def test_create_task_empty_title_fails(self):
        """Test that empty title fails validation."""
        with pytest.raises(ValidationError):
            Task(title="")

    def test_create_task_whitespace_title_fails(self):
        """Test that whitespace-only title fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            Task(title="   ")
        
        assert "Title cannot be empty" in str(exc_info.value)

    def test_title_validation_strips_whitespace(self):
        """Test that title validation strips whitespace."""
        task = Task(title="  Test Task  ")
        assert task.title == "Test Task"

    def test_category_validation_strips_whitespace(self):
        """Test that category validation strips whitespace."""
        task = Task(title="Test", category="  Work  ")
        assert task.category == "Work"

    def test_category_validation_empty_becomes_general(self):
        """Test that empty category becomes General."""
        task = Task(title="Test", category="")
        assert task.category == "General"

    def test_title_max_length_validation(self):
        """Test title maximum length validation."""
        long_title = "x" * 201
        with pytest.raises(ValidationError):
            Task(title=long_title)

    def test_description_max_length_validation(self):
        """Test description maximum length validation."""
        long_description = "x" * 1001
        with pytest.raises(ValidationError):
            Task(title="Test", description=long_description)

    def test_category_max_length_validation(self):
        """Test category maximum length validation."""
        long_category = "x" * 51
        with pytest.raises(ValidationError):
            Task(title="Test", category=long_category)


class TestTaskFilters:
    def test_create_filters_with_defaults(self):
        """Test creating filters with default values."""
        filters = TaskFilters()
        
        assert filters.category is None
        assert filters.completed is None
        assert filters.search is None
        assert filters.limit == 100
        assert filters.offset == 0

    def test_create_filters_with_custom_values(self):
        """Test creating filters with custom values."""
        filters = TaskFilters(
            category="Work",
            completed=True,
            search="important",
            limit=50,
            offset=10
        )
        
        assert filters.category == "Work"
        assert filters.completed is True
        assert filters.search == "important"
        assert filters.limit == 50
        assert filters.offset == 10

    def test_limit_validation(self):
        """Test limit validation bounds."""
        # Test minimum limit
        with pytest.raises(ValidationError):
            TaskFilters(limit=0)
        
        # Test maximum limit
        with pytest.raises(ValidationError):
            TaskFilters(limit=1001)

    def test_offset_validation(self):
        """Test offset validation."""
        # Valid offset
        filters = TaskFilters(offset=0)
        assert filters.offset == 0
        
        # Invalid negative offset
        with pytest.raises(ValidationError):
            TaskFilters(offset=-1)