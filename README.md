# TODO Application

A comprehensive TODO application with both console and REST API interfaces, built with modern Python technologies.

## Features

- **Console Interface**: Rich-powered interactive terminal experience
- **REST API**: FastAPI-powered web interface with automatic documentation
- **Clean Architecture**: Extensible design following SOLID principles
- **PostgreSQL Backend**: Async database operations with proper session management
- **Comprehensive Testing**: Unit and integration tests with high coverage
- **Type Safety**: Full type annotations with mypy validation

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL database
- UV package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PRP_TodoApp
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env with your database URL
```

4. Run database migrations:
```bash
uv run alembic upgrade head
```

### Usage

#### Console Interface

Start the interactive console application:

```bash
uv run python src/main.py console
```

Features:
- Create, read, update, delete tasks
- Search and filter tasks by category/status
- Rich formatted tables and interactive prompts
- Task statistics and analytics

#### REST API

Start the FastAPI server:

```bash
uv run python src/main.py api
```

- API Documentation: http://localhost:8000/api/docs
- Interactive API explorer: http://localhost:8000/api/redoc

#### Interactive Mode Selector

```bash
uv run python src/main.py run
```

## API Endpoints

- `GET /api/v1/todos` - List all tasks with filtering
- `POST /api/v1/todos` - Create a new task
- `GET /api/v1/todos/{id}` - Get specific task
- `PUT /api/v1/todos/{id}` - Update task
- `DELETE /api/v1/todos/{id}` - Delete task
- `PATCH /api/v1/todos/{id}/complete` - Mark as completed
- `PATCH /api/v1/todos/{id}/uncomplete` - Mark as pending
- `GET /api/v1/todos/categories/` - Get all categories

## Development

### Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# With coverage
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
uv run ruff format src/

# Lint code
uv run ruff check src/ --fix

# Type checking
uv run mypy src/
```

### Database Operations

```bash
# Create migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## Architecture

The application follows clean architecture principles:

```
src/todo_app/
├── domain/          # Business logic and models
├── database/        # Data persistence layer
├── services/        # Application services
├── api/            # REST API layer
├── console/        # Console interface layer
└── config.py       # Configuration management
```

## Technology Stack

- **FastAPI**: Modern async web framework
- **SQLAlchemy**: Async ORM with PostgreSQL
- **Pydantic**: Data validation and serialization
- **Rich**: Enhanced console interface
- **Alembic**: Database migrations
- **Pytest**: Testing framework
- **Ruff**: Code formatting and linting
- **MyPy**: Static type checking

## License

MIT License