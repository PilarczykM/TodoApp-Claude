"""File handler utilities for safe file operations."""

import os
import shutil
from datetime import datetime
from pathlib import Path


class FileHandler:
    """Utility class for safe file operations."""

    @staticmethod
    def ensure_data_directory(path: Path) -> None:
        """Create directory if it doesn't exist."""
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def create_backup(file_path: Path) -> Path:
        """Create a backup of existing file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return backup_path

    @staticmethod
    def safe_write(file_path: Path, content: str) -> None:
        """Safely write content to file with atomic operation."""
        temp_path = file_path.with_suffix(file_path.suffix + ".tmp")

        try:
            # Write to temporary file first
            temp_path.write_text(content, encoding="utf-8")

            # Atomic move to final location
            if os.name == "nt":  # Windows
                if file_path.exists():
                    file_path.unlink()
            temp_path.replace(file_path)

        except Exception:
            # Clean up temporary file if something goes wrong
            if temp_path.exists():
                temp_path.unlink()
            raise

    @staticmethod
    def file_exists_and_readable(file_path: Path) -> bool:
        """Check if file exists and is readable."""
        return file_path.exists() and os.access(file_path, os.R_OK)
