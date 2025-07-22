from pathlib import Path

from pydantic import BaseModel, ConfigDict, field_validator

from src.infrastructure import StorageFormat


class AppConfig(BaseModel):
    """Application configuration."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    storage_format: StorageFormat = "json"
    data_directory: Path = Path.home() / ".todoapp"
    backup_enabled: bool = True
    max_backups: int = 5

    @field_validator('data_directory')
    def validate_data_directory(cls, v: Path) -> Path:
        """Ensure data directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v
