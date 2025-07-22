import sys
from pathlib import Path

from src.application import AppConfig, TodoService
from src.domain import RepositoryError
from src.infrastructure import RepositoryFactory

from src.interfaces.console_interface import ConsoleInterface
from src.interfaces.console_utils import ConsoleUtils
from src.interfaces.format_selector import FormatSelector


def create_app_components(data_dir: Path) -> tuple[TodoService, AppConfig]:
    """Create and configure application components."""
    try:
        # Get storage format from user
        storage_format = FormatSelector.select_storage_format()

        # Create configuration
        config = AppConfig(storage_format=storage_format, data_directory=data_dir)

        # Create repository
        repository = RepositoryFactory.create_repository(storage_format, data_dir)

        # Create service
        service = TodoService(repository)

        return service, config

    except Exception as e:
        ConsoleUtils.display_error(f"Failed to initialize application: {e}")
        sys.exit(1)


def main() -> None:
    """Main application entry point."""
    try:
        # Set up data directory
        data_dir = Path.home() / ".todoapp"

        # Create application components
        service, config = create_app_components(data_dir)

        # Create and run console interface
        console = ConsoleInterface(service)
        console.run()

    except KeyboardInterrupt:
        ConsoleUtils.display_info("\nApplication interrupted by user")
    except RepositoryError as e:
        ConsoleUtils.display_error(f"Data access error: {e}")
        sys.exit(1)
    except Exception as e:
        ConsoleUtils.display_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
