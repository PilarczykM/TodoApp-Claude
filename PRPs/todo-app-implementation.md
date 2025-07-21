# TODO Application Implementation PRP

## Goal

Build a complete TODO application with TDD approach featuring:
- **Console Interface**: Rich-powered terminal experience with tables, menus, and interactive prompts
- **REST API**: FastAPI-powered web interface with full CRUD operations
- **Clean Architecture**: Extensible design ready for future GUI implementations
- **PostgreSQL Backend**: Async database operations with proper session management
- **Comprehensive Testing**: 90%+ test coverage following TDD principles

## Why

- **User Value**: Provides flexible access to task management (console + API)
- **Technical Excellence**: Demonstrates modern Python patterns and clean architecture  
- **Extensibility**: Foundation for future web/desktop/mobile interfaces
- **Learning Platform**: Comprehensive example of TDD, async patterns, and clean code

## What

Multi-interface TODO application with:
- Core CRUD operations (create, read, update, delete tasks)
- Task categorization and filtering
- Status management (pending/completed)
- Rich console interface with beautiful formatting
- RESTful API with automatic documentation
- Async PostgreSQL backend with migrations
- Comprehensive test suite

### Success Criteria

- [ ] Console interface allows full task management with Rich formatting
- [ ] REST API provides complete CRUD operations with validation
- [ ] 90%+ test coverage with comprehensive test suite
- [ ] Clean architecture with clear layer separation
- [ ] Database migrations work correctly
- [ ] All validation gates pass (ruff, mypy, pytest)
- [ ] Application handles errors gracefully with user feedback

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Critical for implementation success

- url: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
  why: Async SQLAlchemy patterns, session management, eager loading
  critical: Never share AsyncSession across concurrent tasks

- url: https://fastapi.tiangolo.com/tutorial/bigger-applications/
  why: Project structure patterns, dependency injection, router organization
  
- url: https://rich.readthedocs.io/en/stable/tables.html
  why: Rich table formatting for task display
  
- url: https://docs.pydantic.dev/latest/
  why: Pydantic v2 validation patterns and configuration
  
- url: https://alembic.sqlalchemy.org/en/latest/tutorial.html
  why: Database migration patterns and async configuration

- url: https://docs.pytest.org/en/stable/how-to/fixtures.html
  why: Async test fixtures and database test isolation

- docfile: PRPs/ai_docs/async-sqlalchemy-patterns.md
  why: Critical SQLAlchemy async patterns and gotchas specific to this project

- docfile: PRPs/ai_docs/fastapi-best-practices.md
  why: FastAPI project structure and patterns aligned with our needs

- file: CLAUDE.md
  why: Project development guidelines, conventions, and standards to follow
```

### Current Codebase Structure

```bash
PRP_TodoApp/
├── CLAUDE.md                          # Development guidelines
├── README.md
├── pyproject.toml                     # Basic deps: pytest, ruff
├── uv.lock
├── src/
│   ├── __init__.py
│   └── main.py                        # Just prints "Hello"
└── PRPs/
    ├── ai_docs/                       # Critical implementation docs
    ├── prp_base.md                    # PRP template
    └── todo-app-prd.md                # Requirements document
```

### Desired Codebase Structure with Responsibilities

```bash
PRP_TodoApp/
├── pyproject.toml                     # All dependencies configured
├── alembic.ini                        # Migration configuration
├── alembic/                          # Database migrations
│   ├── env.py                        # Async migration setup
│   └── versions/                     # Migration files
├── src/
│   └── todo_app/
│       ├── __init__.py
│       ├── main.py                   # Application entry points
│       ├── config.py                 # Settings management
│       │
│       ├── domain/                   # Core business logic
│       │   ├── __init__.py
│       │   ├── models.py             # Pydantic domain models
│       │   └── exceptions.py         # Custom exceptions
│       │
│       ├── database/                 # Data persistence
│       │   ├── __init__.py
│       │   ├── connection.py         # Async session management
│       │   ├── models.py             # SQLAlchemy ORM models
│       │   └── repository.py         # Repository pattern
│       │
│       ├── services/                 # Business logic services
│       │   ├── __init__.py
│       │   └── todo_service.py       # Task business operations
│       │
│       ├── api/                      # FastAPI REST interface
│       │   ├── __init__.py
│       │   ├── main.py               # FastAPI app
│       │   ├── dependencies.py       # DI containers
│       │   ├── schemas.py            # Request/Response models
│       │   └── routes/
│       │       ├── __init__.py
│       │       └── todos.py          # Task endpoints
│       │
│       ├── console/                  # Rich console interface
│       │   ├── __init__.py
│       │   ├── main.py               # Console entry point
│       │   ├── ui.py                 # Rich UI components
│       │   └── commands.py           # CLI command handlers
│       │
│       └── tests/                    # Test suite
│           ├── conftest.py           # Shared fixtures
│           ├── unit/                 # Unit tests
│           ├── integration/          # Integration tests
│           └── e2e/                  # End-to-end tests
└── tests/                            # Additional test files if needed
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: SQLAlchemy Async Session Management
# - NEVER share AsyncSession across concurrent tasks
# - ALWAYS use expire_on_commit=False for post-commit attribute access
# - Use selectinload() for relationship eager loading

# CRITICAL: FastAPI + Pydantic v2
# - Use model_config = ConfigDict(from_attributes=True) for ORM integration
# - Pydantic v2 uses different field validation syntax
# - Always handle ValidationError in endpoints

# CRITICAL: Rich Console Performance
# - Rich has 1.6s startup penalty - create Console instance once
# - Use force_terminal=False for testing
# - Disable record=True in production

# CRITICAL: UV Package Management
# - NEVER edit pyproject.toml dependencies directly
# - ALWAYS use 'uv add package' for new dependencies
# - Use 'uv sync' instead of pip install

# CRITICAL: Testing with Async
# - Use pytest-asyncio for async tests
# - Create new session for each test (isolation)
# - Mock async functions with AsyncMock, not Mock
```

## Implementation Blueprint

### Data Models and Structure

Create the core data models ensuring type safety and consistency:

```python
# Domain Models (Pydantic)
class Task(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: str = Field(default="General", max_length=50)
    completed: bool = False
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

# ORM Models (SQLAlchemy)
class TaskORM(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    # ... other fields

# API Schemas (Request/Response)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = "General"

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    category: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

### List of Tasks to Complete (Implementation Order)

```yaml
Task 1: Project Setup and Dependencies
MODIFY pyproject.toml:
  - ADD fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic, rich, click
  - ADD dev dependencies: pytest-asyncio, httpx, pytest-cov, mypy
  - CONFIGURE tool sections for ruff, mypy, coverage

CREATE .env file:
  - DATABASE_URL for local PostgreSQL
  - Environment configuration

Task 2: Database Foundation  
CREATE src/todo_app/database/connection.py:
  - IMPLEMENT async engine setup with connection pooling
  - CREATE async session factory with expire_on_commit=False
  - PROVIDE get_async_session dependency function

CREATE src/todo_app/database/models.py:
  - DEFINE Base declarative base
  - CREATE TaskORM model with proper constraints
  - INCLUDE created_at, updated_at with auto-timestamps

CREATE alembic configuration:
  - INITIALIZE alembic for async migrations
  - CONFIGURE env.py for async engine
  - CREATE initial migration for tasks table

Task 3: Core Domain Layer
CREATE src/todo_app/domain/models.py:
  - IMPLEMENT Task Pydantic model with validation
  - CREATE TaskStatus enum
  - ADD field validators for title, category

CREATE src/todo_app/domain/exceptions.py:
  - DEFINE custom exception hierarchy
  - CREATE TaskNotFoundError, ValidationError classes

Task 4: Repository Pattern
CREATE src/todo_app/database/repository.py:
  - IMPLEMENT BaseRepository with generic CRUD operations
  - CREATE TaskRepository with domain-specific queries
  - INCLUDE filtering by category, status, search

Task 5: Service Layer
CREATE src/todo_app/services/todo_service.py:
  - IMPLEMENT TodoService with business logic
  - CREATE methods: create_task, get_tasks, update_task, delete_task
  - ADD validation and error handling

Task 6: Configuration Management
CREATE src/todo_app/config.py:
  - USE pydantic-settings for configuration
  - LOAD database URL, debug settings from environment
  - PROVIDE get_settings cached function

Task 7: API Layer Foundation
CREATE src/todo_app/api/schemas.py:
  - DEFINE TaskCreate, TaskUpdate, TaskResponse models
  - IMPLEMENT proper validation and serialization

CREATE src/todo_app/api/dependencies.py:
  - PROVIDE get_db_session dependency
  - CREATE get_todo_service dependency injection

Task 8: FastAPI Routes
CREATE src/todo_app/api/routes/todos.py:
  - IMPLEMENT full CRUD endpoints with proper HTTP methods
  - ADD filtering, pagination, search functionality
  - INCLUDE comprehensive error handling

CREATE src/todo_app/api/main.py:
  - SETUP FastAPI app with middleware
  - INCLUDE routers and exception handlers
  - CONFIGURE CORS for frontend integration

Task 9: Console Interface Foundation
CREATE src/todo_app/console/ui.py:
  - IMPLEMENT Rich table for task display
  - CREATE interactive prompts for task input
  - DESIGN menu system with navigation

CREATE src/todo_app/console/commands.py:
  - IMPLEMENT command handlers for CRUD operations
  - ADD filtering and search capabilities
  - INCLUDE error display and user feedback

CREATE src/todo_app/console/main.py:
  - CREATE console application entry point
  - IMPLEMENT main menu loop
  - INTEGRATE with service layer

Task 10: Application Entry Points
MODIFY src/todo_app/main.py:
  - PROVIDE command-line interface to choose mode
  - IMPLEMENT console and API server startup
  - ADD proper argument parsing

Task 11: Comprehensive Test Suite
CREATE tests/conftest.py:
  - SETUP test database fixtures
  - IMPLEMENT async session fixtures
  - CREATE sample data factories

CREATE tests/unit/ structure:
  - TEST domain models validation
  - TEST service layer business logic
  - TEST repository operations

CREATE tests/integration/ structure:
  - TEST API endpoints with test client
  - TEST database operations end-to-end
  - TEST console interface components

CREATE tests/e2e/ structure:
  - TEST complete user workflows
  - TEST error scenarios and edge cases

Task 12: Database Migrations and Seeding
CREATE migration scripts:
  - GENERATE initial schema migration
  - ADD seed data for categories
  - IMPLEMENT rollback procedures

Task 13: Error Handling and Logging
ENHANCE exception handling:
  - ADD structured logging configuration
  - IMPLEMENT global error handlers
  - CREATE user-friendly error messages

Task 14: Documentation and Polish
CREATE README with setup instructions:
  - DOCUMENT installation and usage
  - PROVIDE API examples
  - INCLUDE development setup

FINALIZE validation and testing:
  - ENSURE 90%+ test coverage
  - VERIFY all linting passes
  - TEST complete user workflows
```

### Task Implementation Details

#### Task 1: Project Setup (Critical Foundation)
```python
# pyproject.toml additions
[dependencies]
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.0"}
asyncpg = "^0.29.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
alembic = "^1.13.0"
rich = "^13.7.0"
click = "^8.1.0"

[dependency-groups.dev]
pytest-asyncio = "^0.21.0"
httpx = "^0.25.0"
pytest-cov = "^4.1.0"
mypy = "^1.7.0"
```

#### Task 2: Database Connection (Session Management Critical)
```python
# src/todo_app/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# CRITICAL: Connection pool configuration for production
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    echo=False  # Set True for SQL debugging
)

# CRITICAL: expire_on_commit=False required for post-commit access
async_session_maker = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### Task 5: Service Layer (Business Logic Hub)
```python
# src/todo_app/services/todo_service.py
class TodoService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def create_task(self, task_data: TaskCreate) -> Task:
        # PATTERN: Validate business rules first
        if not task_data.title.strip():
            raise ValueError("Title cannot be empty")
        
        # PATTERN: Use repository for persistence
        task_dict = task_data.model_dump()
        db_task = await self.repository.create(task_dict)
        return Task.model_validate(db_task)

    async def get_filtered_tasks(self, filters: TaskFilters) -> List[Task]:
        # PATTERN: Repository handles data access, service handles logic
        db_tasks = await self.repository.get_with_filters(filters)
        return [Task.model_validate(task) for task in db_tasks]
```

#### Task 8: API Routes (Error Handling Critical)
```python
# src/todo_app/api/routes/todos.py
@router.post("/", response_model=TaskResponse, status_code=201)
async def create_todo(
    task_data: TaskCreate,
    service: TodoService = Depends(get_todo_service)
) -> TaskResponse:
    try:
        task = await service.create_task(task_data)
        return TaskResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error creating task")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Integration Points

```yaml
DATABASE:
  - migration: "alembic upgrade head"
  - connection: "postgresql+asyncpg://user:pass@localhost/todo_db"
  - pooling: "Configure connection pool with max 20 connections"

CONFIG:
  - add to: src/todo_app/config.py
  - pattern: "DATABASE_URL = Field(..., env='DATABASE_URL')"
  - validation: "Use pydantic-settings for type-safe config"

ROUTES:
  - add to: src/todo_app/api/main.py
  - pattern: "app.include_router(todo_router, prefix='/api/v1')"
  - middleware: "Add CORS middleware for frontend integration"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
uv run ruff check src/ --fix
uv run ruff format src/
uv run mypy src/

# Expected: No errors. If errors, READ the error and fix.
# Common issues: import ordering, unused imports, type annotations
```

### Level 2: Unit Tests (Follow TDD - Write Tests First)
```python
# CREATE tests/unit/test_todo_service.py
@pytest.mark.asyncio
async def test_create_task_with_valid_data():
    """Test basic task creation works"""
    mock_repo = AsyncMock()
    mock_repo.create.return_value = TaskORM(id=uuid4(), title="Test")
    
    service = TodoService(mock_repo)
    result = await service.create_task(TaskCreate(title="Test"))
    
    assert result.title == "Test"
    mock_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_task_empty_title_raises_error():
    """Test validation prevents empty titles"""
    service = TodoService(AsyncMock())
    
    with pytest.raises(ValueError, match="Title cannot be empty"):
        await service.create_task(TaskCreate(title=""))

# CREATE tests/integration/test_api.py
@pytest.mark.asyncio
async def test_create_todo_endpoint_success(test_client):
    """Test API endpoint creates task successfully"""
    payload = {"title": "Test task", "description": "Test desc"}
    response = await test_client.post("/api/v1/todos", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert "id" in data
```

```bash
# Run and iterate until passing:
uv run pytest tests/unit/ -v
uv run pytest tests/integration/ -v
uv run pytest --cov=src --cov-report=term-missing

# If failing: Read error, understand root cause, fix code (never mock to pass)
# Target: 90%+ coverage, all tests passing
```

### Level 3: Integration Testing
```bash
# Start PostgreSQL database
docker run -d --name test-postgres \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=test_todo \
  -p 5432:5432 postgres:15

# Run migrations
export DATABASE_URL="postgresql+asyncpg://postgres:test@localhost/test_todo"
uv run alembic upgrade head

# Test the API server
uv run uvicorn src.todo_app.api.main:app --host 0.0.0.0 --port 8000 &

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Integration test"}'

# Expected: {"id": "...", "title": "Test task", ...}

# Test console interface
uv run python -m src.todo_app.console.main

# Expected: Rich-formatted menu system, task CRUD operations work
```

### Level 4: End-to-End Validation
```bash
# Complete workflow testing
uv run pytest tests/e2e/ -v

# Performance testing
uv run python scripts/load_test.py  # Create if needed

# Coverage validation
uv run pytest --cov=src --cov-report=html --cov-fail-under=90

# Memory leak testing (for long-running processes)
uv run python -m memory_profiler scripts/memory_test.py
```

## Final Validation Checklist

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] No type errors: `uv run mypy src/`
- [ ] Database migrations work: `uv run alembic upgrade head`
- [ ] API responds correctly: `curl -X GET http://localhost:8000/api/v1/todos`
- [ ] Console interface functional: Interactive menu and CRUD operations
- [ ] Coverage above 90%: `uv run pytest --cov=src --cov-fail-under=90`
- [ ] Error cases handled gracefully: Invalid input shows user-friendly messages
- [ ] Documentation complete: README with setup and usage instructions

---

## Anti-Patterns to Avoid

- ❌ Don't share AsyncSession across async tasks - creates race conditions
- ❌ Don't skip writing tests first - breaks TDD discipline  
- ❌ Don't use sync database operations - breaks FastAPI async benefits
- ❌ Don't ignore validation errors - leads to data inconsistency
- ❌ Don't hardcode database URLs - use environment configuration
- ❌ Don't create circular imports between layers - maintain clean architecture
- ❌ Don't forget to close database sessions - causes connection leaks
- ❌ Don't mock everything in tests - reduces test value and confidence

---

**Success Confidence Score: 9/10**

This PRP provides comprehensive context, clear implementation path, specific validation gates, and addresses all critical gotchas identified during research. The layered approach with TDD ensures steady progress while maintaining quality. Rich documentation and examples enable one-pass implementation success.