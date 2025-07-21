from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.todo_app.domain.exceptions import TaskNotFoundError, ValidationError
from src.todo_app.domain.models import Task, TaskFilters
from src.todo_app.services.todo_service import TodoService


class TestTodoService:
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, mock_repository, mock_task_orm):
        """Test successful task creation."""
        # Arrange
        mock_repository.create.return_value = mock_task_orm
        service = TodoService(mock_repository)
        
        # Act
        result = await service.create_task(
            title="Test Task",
            description="Test Description",
            category="Test Category"
        )
        
        # Assert
        assert isinstance(result, Task)
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_empty_title_fails(self, mock_repository):
        """Test that creating a task with empty title fails."""
        service = TodoService(mock_repository)
        
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            await service.create_task(title="")

    @pytest.mark.asyncio
    async def test_create_task_whitespace_title_fails(self, mock_repository):
        """Test that creating a task with whitespace-only title fails."""
        service = TodoService(mock_repository)
        
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            await service.create_task(title="   ")

    @pytest.mark.asyncio
    async def test_get_task_success(self, mock_repository, mock_task_orm):
        """Test successful task retrieval."""
        # Arrange
        task_id = uuid4()
        mock_repository.get_by_id.return_value = mock_task_orm
        service = TodoService(mock_repository)
        
        # Act
        result = await service.get_task(task_id)
        
        # Assert
        assert isinstance(result, Task)
        mock_repository.get_by_id.assert_called_once_with(task_id)

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, mock_repository):
        """Test getting a non-existent task."""
        # Arrange
        task_id = uuid4()
        mock_repository.get_by_id.return_value = None
        service = TodoService(mock_repository)
        
        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            await service.get_task(task_id)

    @pytest.mark.asyncio
    async def test_get_all_tasks(self, mock_repository, mock_task_orm):
        """Test getting all tasks."""
        # Arrange
        mock_repository.get_all.return_value = [mock_task_orm, mock_task_orm]
        service = TodoService(mock_repository)
        
        # Act
        result = await service.get_all_tasks(limit=50, offset=10)
        
        # Assert
        assert len(result) == 2
        assert all(isinstance(task, Task) for task in result)
        mock_repository.get_all.assert_called_once_with(limit=50, offset=10)

    @pytest.mark.asyncio
    async def test_get_filtered_tasks(self, mock_repository, mock_task_orm):
        """Test getting filtered tasks."""
        # Arrange
        mock_repository.get_with_filters.return_value = [mock_task_orm]
        service = TodoService(mock_repository)
        filters = TaskFilters(category="Work", completed=False)
        
        # Act
        result = await service.get_filtered_tasks(filters)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Task)
        mock_repository.get_with_filters.assert_called_once_with(filters)

    @pytest.mark.asyncio
    async def test_update_task_success(self, mock_repository, mock_task_orm):
        """Test successful task update."""
        # Arrange
        task_id = uuid4()
        mock_repository.update.return_value = mock_task_orm
        service = TodoService(mock_repository)
        
        # Act
        result = await service.update_task(
            task_id,
            title="Updated Title",
            description="Updated Description"
        )
        
        # Assert
        assert isinstance(result, Task)
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_empty_title_fails(self, mock_repository):
        """Test that updating with empty title fails."""
        service = TodoService(mock_repository)
        task_id = uuid4()
        
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            await service.update_task(task_id, title="")

    @pytest.mark.asyncio
    async def test_delete_task_success(self, mock_repository):
        """Test successful task deletion."""
        # Arrange
        task_id = uuid4()
        mock_repository.delete.return_value = True
        service = TodoService(mock_repository)
        
        # Act
        result = await service.delete_task(task_id)
        
        # Assert
        assert result is True
        mock_repository.delete.assert_called_once_with(task_id)

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, mock_repository):
        """Test deleting a non-existent task."""
        # Arrange
        task_id = uuid4()
        mock_repository.delete.return_value = False
        service = TodoService(mock_repository)
        
        # Act
        result = await service.delete_task(task_id)
        
        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_mark_completed(self, mock_repository, mock_task_orm):
        """Test marking a task as completed."""
        # Arrange
        task_id = uuid4()
        mock_repository.update.return_value = mock_task_orm
        service = TodoService(mock_repository)
        
        # Act
        result = await service.mark_completed(task_id)
        
        # Assert
        assert isinstance(result, Task)
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_pending(self, mock_repository, mock_task_orm):
        """Test marking a task as pending."""
        # Arrange
        task_id = uuid4()
        mock_repository.update.return_value = mock_task_orm
        service = TodoService(mock_repository)
        
        # Act
        result = await service.mark_pending(task_id)
        
        # Assert
        assert isinstance(result, Task)
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_categories(self, mock_repository):
        """Test getting all categories."""
        # Arrange
        expected_categories = ["Work", "Personal", "Urgent"]
        mock_repository.get_categories.return_value = expected_categories
        service = TodoService(mock_repository)
        
        # Act
        result = await service.get_categories()
        
        # Assert
        assert result == expected_categories
        mock_repository.get_categories.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_tasks(self, mock_repository, mock_task_orm):
        """Test searching tasks."""
        # Arrange
        mock_repository.get_with_filters.return_value = [mock_task_orm]
        service = TodoService(mock_repository)
        
        # Act
        result = await service.search_tasks("important", limit=50)
        
        # Assert
        assert len(result) == 1
        assert isinstance(result[0], Task)
        mock_repository.get_with_filters.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_tasks_empty_query(self, mock_repository, mock_task_orm):
        """Test searching with empty query returns all tasks."""
        # Arrange
        mock_repository.get_all.return_value = [mock_task_orm]
        service = TodoService(mock_repository)
        
        # Act
        result = await service.search_tasks("", limit=50)
        
        # Assert
        assert len(result) == 1
        mock_repository.get_all.assert_called_once_with(limit=50, offset=0)