import pytest


class TestTodoAPI:
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, test_client):
        """Test successful task creation via API."""
        task_data = {
            "title": "API Test Task",
            "description": "Created via API test",
            "category": "Testing"
        }
        
        response = await test_client.post("/api/v1/todos/", json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["category"] == task_data["category"]
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, test_client):
        """Test task creation with validation error."""
        task_data = {
            "title": "",  # Empty title should fail
            "description": "This should fail"
        }
        
        response = await test_client.post("/api/v1/todos/", json=task_data)
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_all_tasks_empty(self, test_client):
        """Test getting all tasks when none exist."""
        response = await test_client.get("/api/v1/todos/")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_all_tasks_with_data(self, test_client):
        """Test getting all tasks when some exist."""
        # First create a task
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "category": "Test"
        }
        
        create_response = await test_client.post("/api/v1/todos/", json=task_data)
        assert create_response.status_code == 201
        
        # Then get all tasks
        response = await test_client.get("/api/v1/todos/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == task_data["title"]

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, test_client):
        """Test getting a specific task by ID."""
        # First create a task
        task_data = {
            "title": "Specific Task",
            "description": "For ID test",
            "category": "Test"
        }
        
        create_response = await test_client.post("/api/v1/todos/", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        
        # Then get it by ID
        response = await test_client.get(f"/api/v1/todos/{created_task['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_task["id"]
        assert data["title"] == task_data["title"]

    @pytest.mark.asyncio
    async def test_get_task_by_id_not_found(self, test_client):
        """Test getting a non-existent task."""
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = await test_client.get(f"/api/v1/todos/{fake_id}")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task(self, test_client):
        """Test updating a task."""
        # First create a task
        task_data = {
            "title": "Original Title",
            "description": "Original Description",
            "category": "Original"
        }
        
        create_response = await test_client.post("/api/v1/todos/", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        
        # Then update it
        update_data = {
            "title": "Updated Title",
            "completed": True
        }
        
        response = await test_client.put(
            f"/api/v1/todos/{created_task['id']}", 
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["completed"] is True
        assert data["description"] == task_data["description"]  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_task(self, test_client):
        """Test deleting a task."""
        # First create a task
        task_data = {
            "title": "To be deleted",
            "description": "This task will be deleted",
            "category": "Test"
        }
        
        create_response = await test_client.post("/api/v1/todos/", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        
        # Then delete it
        response = await test_client.delete(f"/api/v1/todos/{created_task['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]
        
        # Verify it's gone
        get_response = await test_client.get(f"/api/v1/todos/{created_task['id']}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_task(self, test_client):
        """Test marking a task as completed."""
        # First create a task
        task_data = {
            "title": "To be completed",
            "description": "This task will be marked complete",
            "category": "Test"
        }
        
        create_response = await test_client.post("/api/v1/todos/", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        assert created_task["completed"] is False
        
        # Then mark it complete
        response = await test_client.patch(f"/api/v1/todos/{created_task['id']}/complete")
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    @pytest.mark.asyncio
    async def test_uncomplete_task(self, test_client):
        """Test marking a completed task as pending."""
        # First create and complete a task
        task_data = {
            "title": "To be uncompleted",
            "description": "This task will be marked pending",
            "category": "Test"
        }
        
        create_response = await test_client.post("/api/v1/todos/", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        
        # Mark it complete first
        await test_client.patch(f"/api/v1/todos/{created_task['id']}/complete")
        
        # Then mark it pending
        response = await test_client.patch(f"/api/v1/todos/{created_task['id']}/uncomplete")
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is False

    @pytest.mark.asyncio
    async def test_get_categories(self, test_client):
        """Test getting all categories."""
        # Create tasks with different categories
        categories = ["Work", "Personal", "Shopping"]
        
        for category in categories:
            task_data = {
                "title": f"Task in {category}",
                "category": category
            }
            await test_client.post("/api/v1/todos/", json=task_data)
        
        # Get categories
        response = await test_client.get("/api/v1/todos/categories/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for category in categories:
            assert category in data

    @pytest.mark.asyncio
    async def test_filter_tasks_by_category(self, test_client):
        """Test filtering tasks by category."""
        # Create tasks with different categories
        work_task = {"title": "Work Task", "category": "Work"}
        personal_task = {"title": "Personal Task", "category": "Personal"}
        
        await test_client.post("/api/v1/todos/", json=work_task)
        await test_client.post("/api/v1/todos/", json=personal_task)
        
        # Filter by Work category
        response = await test_client.get("/api/v1/todos/?category=Work")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Work"

    @pytest.mark.asyncio
    async def test_filter_tasks_by_completed_status(self, test_client):
        """Test filtering tasks by completion status."""
        # Create tasks
        task1_data = {"title": "Pending Task", "category": "Test"}
        task2_data = {"title": "Completed Task", "category": "Test"}
        
        task1_response = await test_client.post("/api/v1/todos/", json=task1_data)
        task2_response = await test_client.post("/api/v1/todos/", json=task2_data)
        
        # Complete one task
        task2 = task2_response.json()
        await test_client.patch(f"/api/v1/todos/{task2['id']}/complete")
        
        # Filter by completed status
        response = await test_client.get("/api/v1/todos/?completed=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["completed"] is True

    @pytest.mark.asyncio
    async def test_search_tasks(self, test_client):
        """Test searching tasks."""
        # Create tasks with searchable content
        task1 = {"title": "Important Meeting", "description": "Discuss project"}
        task2 = {"title": "Buy Groceries", "description": "Important shopping list"}
        task3 = {"title": "Regular Task", "description": "Nothing special"}
        
        await test_client.post("/api/v1/todos/", json=task1)
        await test_client.post("/api/v1/todos/", json=task2)
        await test_client.post("/api/v1/todos/", json=task3)
        
        # Search for "important"
        response = await test_client.get("/api/v1/todos/?search=important")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Should match both tasks containing "important"