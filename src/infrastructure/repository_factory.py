"""Factory class for creating repository instances."""

from pathlib import Path
from typing import Literal, List

from src.domain.repository import TodoRepository
from src.infrastructure.json_repository import JsonTodoRepository
from src.infrastructure.xml_repository import XmlTodoRepository

StorageFormat = Literal["json", "xml"]


class RepositoryFactory:
    """Factory class for creating repository instances."""
    
    @staticmethod
    def create_repository(format_type: StorageFormat, data_dir: Path) -> TodoRepository:
        """Create a repository instance based on format type."""
        if format_type == "json":
            file_path = data_dir / "todos.json"
            return JsonTodoRepository(file_path)
        elif format_type == "xml":
            file_path = data_dir / "todos.xml"
            return XmlTodoRepository(file_path)
        else:
            raise ValueError(f"Unsupported storage format: {format_type}")
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported storage formats."""
        return ["json", "xml"]