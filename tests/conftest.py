import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.todo_app.api.main import app
from src.todo_app.database.connection import get_async_session
from src.todo_app.database.models import Base, TaskORM
from src.todo_app.database.repository import TaskRepository
from src.todo_app.domain.models import Task
from src.todo_app.services.todo_service import TodoService

# Test database URL for SQLite in-memory database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session_maker_test(async_engine):
    """Create async session maker for testing."""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    return async_session


@pytest_asyncio.fixture
async def async_session(async_session_maker_test):
    """Create async session for testing."""
    async with async_session_maker_test() as session:
        yield session


@pytest_asyncio.fixture
async def repository(async_session):
    """Create repository for testing."""
    return TaskRepository(async_session)


@pytest_asyncio.fixture
async def todo_service(repository):
    """Create todo service for testing."""
    return TodoService(repository)


@pytest_asyncio.fixture
async def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "category": "Testing",
        "completed": False
    }


@pytest_asyncio.fixture
async def sample_task(repository, sample_task_data):
    """Create a sample task in the database."""
    task = await repository.create(**sample_task_data)
    return task


@pytest_asyncio.fixture
async def multiple_tasks(repository):
    """Create multiple sample tasks in the database."""
    tasks_data = [
        {"title": "Task 1", "description": "First task", "category": "Work", "completed": False},
        {"title": "Task 2", "description": "Second task", "category": "Personal", "completed": True},
        {"title": "Task 3", "description": "Third task", "category": "Work", "completed": False},
        {"title": "Important Task", "description": "Very important", "category": "Urgent", "completed": False},
    ]
    
    tasks = []
    for task_data in tasks_data:
        task = await repository.create(**task_data)
        tasks.append(task)
    
    return tasks


# Override the database dependency for testing
async def get_test_async_session():
    """Override for testing - this will be set up by individual tests."""
    pass


@pytest_asyncio.fixture
async def test_client(async_session_maker_test):
    """Create test client with overridden dependencies."""
    
    async def override_get_async_session():
        async with async_session_maker_test() as session:
            yield session
    
    app.dependency_overrides[get_async_session] = override_get_async_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock fixtures for unit tests
@pytest.fixture
def mock_repository():
    """Mock repository for unit tests."""
    return AsyncMock(spec=TaskRepository)


@pytest.fixture
def mock_task_orm():
    """Mock TaskORM for unit tests."""
    mock = AsyncMock(spec=TaskORM)
    mock.id = "550e8400-e29b-41d4-a716-446655440000"
    mock.title = "Mock Task"
    mock.description = "Mock Description"
    mock.category = "Mock Category"
    mock.completed = False
    return mock


@pytest.fixture
def mock_task():
    """Mock Task domain object for unit tests."""
    return Task(
        title="Mock Task",
        description="Mock Description",
        category="Mock Category",
        completed=False
    )