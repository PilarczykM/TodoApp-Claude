# TodoApp

A console-based Todo List application built with Python 3.12+ following Domain-Driven Design (DDD) principles and clean architecture patterns.

## Overview

PRP TodoApp is a command-line task management application that demonstrates modern software architecture practices. It provides full CRUD operations for managing todo items with support for multiple data persistence formats (JSON and XML).

### Key Features

- **Complete Task Management**: Create, read, update, and delete todo items
- **Flexible Storage**: Choose between JSON or XML data persistence at startup
- **Priority System**: Organize tasks with LOW, MEDIUM, and HIGH priorities
- **Status Tracking**: Mark tasks as completed or pending
- **Filtering Options**: View tasks by status (completed/pending) or priority level
- **Clean Architecture**: Well-structured codebase following DDD principles
- **Comprehensive Testing**: High test coverage with pytest framework
- **Code Quality**: Enforced with ruff (linting/formatting) and mypy (type checking)

### Technology Stack

- **Language**: Python 3.12+
- **Architecture**: Domain-Driven Design (DDD) with Clean Architecture
- **Data Modeling**: Pydantic v2 for validation and serialization
- **Testing**: pytest with coverage reporting
- **Code Quality**: ruff for linting/formatting, mypy for type checking
- **Dependency Management**: uv package manager

## Architecture

The application follows a layered architecture with clear separation of concerns:

```
src/
   domain/          # Core business logic and entities
   application/     # Use cases and application services
   infrastructure/  # Data persistence and external concerns
   interfaces/      # User interface and application entry points
```

### Layer Responsibilities

- **Domain Layer**: Contains business entities (Todo, Priority), repository interfaces, and domain exceptions
- **Application Layer**: Implements use cases, DTOs, and coordinates business operations
- **Infrastructure Layer**: Provides concrete implementations for data persistence (JSON/XML repositories)
- **Interface Layer**: Handles user interaction through console interface and application startup

### Design Patterns

- **Repository Pattern**: Abstract data access with multiple storage implementations
- **Strategy Pattern**: Pluggable storage formats (JSON/XML)
- **DTO Pattern**: Data transfer objects for application layer boundaries
- **Factory Pattern**: Repository creation based on storage format selection

## Installation

### Prerequisites

- Python 3.12 or higher
- uv package manager (recommended) or pip

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd PRP_TodoApp
   ```

2. **Install dependencies**:
   ```bash
   make install
   # or manually with uv:
   uv sync
   ```

3. **Verify installation**:
   ```bash
   make test
   ```

## Usage

### Running the Application

**Option 1: Direct execution**
```bash
python -m src/todo_app.py
```

**Option 2: UV script**
```bash
uv run -m src.todo_app
```

### Application Workflow

1. **Format Selection**: Choose between JSON or XML storage format at startup
2. **Main Menu**: Navigate through the following options:
   - List all tasks (with filtering options)
   - Add new task
   - Update existing task
   - Delete task
   - Mark task complete/incomplete
   - Exit application

### Storage

The application stores data in your home directory:
- **Location**: `~/.todoapp/`
- **JSON Format**: `todos.json`
- **XML Format**: `todos.xml`

### Example Usage

```
Todo App - Storage Format Selection
====================================================
Welcome to the Todo List Application!
Please choose your preferred data storage format:

Storage Format Options
----------------------
1. JSON format (.json file)
2. XML format (.xml file)

Enter your choice: 1
 JSON format selected

====================================================
           Todo List Application
====================================================
9  Welcome! Manage your tasks efficiently.

Main Menu
---------
1. List all tasks
2. Add new task
3. Update task
4. Delete task
5. Mark task complete/incomplete
6. Exit

Enter your choice: 2
```

## Development

### Project Structure

```
PRP_TodoApp/
   src/
      domain/              # Business entities and rules
         todo.py         # Todo entity with business methods
         priority.py     # Priority enumeration
         repository.py   # Repository interface
         exceptions.py   # Domain-specific exceptions
      application/         # Use cases and services
         dto/            # Data transfer objects
         use_cases/      # Individual use case implementations
         todo_service.py # Main application service
         config.py       # Application configuration
      infrastructure/      # External concerns
         json_repository.py    # JSON persistence
         xml_repository.py     # XML persistence
         file_handler.py       # File operations
         repository_factory.py # Repository creation
      interfaces/          # User interface layer
         console_interface.py  # Main console UI
         console_utils.py      # Display utilities
         format_selector.py    # Storage format selection
         main.py               # Application entry point
      todo_app.py         # CLI script entry point
   tests/                  # Comprehensive test suite
   docs/                   # Documentation
   pyproject.toml         # Project configuration
   Makefile              # Development commands
   CLAUDE.md            # Project guidelines
```

### Available Commands

Use the Makefile for common development tasks:

```bash
make install    # Install dependencies
make test       # Run all tests
make cov        # Run tests with coverage (must be >90%)
make lint       # Check code quality
make typecheck  # Run static type analysis
make format     # Auto-fix code formatting
make all        # Run format, lint, and test
```

### Code Quality Standards

- **Test Coverage**: Minimum 90% coverage required
- **Linting**: No ruff violations allowed
- **Type Checking**: All mypy checks must pass
- **Formatting**: Consistent code style with ruff
- **Architecture**: Follow SOLID principles and clean architecture

### Testing

The project uses pytest with comprehensive test coverage:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end application flow testing
- **Test Organization**: Class-based organization mirroring source structure
- **Coverage Reporting**: Detailed coverage analysis with exclusions for non-testable code

### Development Workflow

1. **Test-Driven Development**: Write tests before implementation
2. **Code Quality**: Run `make format lint typecheck` before committing
3. **Testing**: Ensure `make test cov` passes with >90% coverage
4. **Atomic Commits**: Keep changes small and focused
5. **No Direct Commits**: Use feature branches for main branch

## Configuration

### Environment Variables

The application uses the following configuration:

- **Data Directory**: `~/.todoapp/` (automatically created)
- **Storage Format**: Selected at runtime (JSON or XML)
- **Logging**: Console output with colored status messages

### Customization

- **File Locations**: Modify `data_directory` in application configuration
- **Storage Formats**: Extend `RepositoryFactory` for additional formats
- **UI Themes**: Customize `ConsoleUtils` for different display styles

## Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch
3. Follow the TDD approach (write tests first)
4. Ensure all quality checks pass
5. Submit a pull request

### Code Style

- **Imports**: Use absolute imports only (no relative imports)
- **Type Hints**: Required for all public methods
- **Docstrings**: Document classes and complex methods
- **Error Handling**: Use domain-specific exceptions
- **Architecture**: Maintain layer separation and dependency direction

### Quality Gates

Before submitting code:

```bash
make format     # Fix formatting issues
make lint       # Check for violations
make typecheck  # Verify type annotations
make test       # Run all tests
make cov        # Verify coverage >90%
```

## License

This project is part of a programming practice exercise demonstrating clean architecture and modern Python development practices.

---

For detailed technical specifications, see [docs/PRD.md](docs/PRD.md).
For implementation phases, see the task documentation in [docs/tasks/](docs/tasks/).