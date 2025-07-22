"""Tests for file handler utilities."""

import os
import tempfile
import unittest.mock
from pathlib import Path

import pytest

from src.infrastructure.file_handler import FileHandler


class TestFileHandler:
    """Test cases for FileHandler utility class."""

    def test_ensure_data_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "data"
            FileHandler.ensure_data_directory(data_path)
            assert data_path.exists()
            assert data_path.is_dir()

    def test_backup_file(self):
        """Test file backup creation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = Path(f.name)

        try:
            backup_path = FileHandler.create_backup(temp_file)
            assert backup_path.exists()
            assert backup_path.read_text() == "test content"
        finally:
            temp_file.unlink(missing_ok=True)
            backup_path.unlink(missing_ok=True)

    def test_backup_nonexistent_file(self):
        """Test backup of non-existent file raises error."""
        non_existent = Path("/tmp/does_not_exist.txt")
        with pytest.raises(FileNotFoundError):
            FileHandler.create_backup(non_existent)

    def test_safe_write(self):
        """Test safe file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            FileHandler.safe_write(file_path, "test content")
            assert file_path.read_text() == "test content"

    def test_safe_write_overwrites_existing(self):
        """Test safe write overwrites existing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            # Write initial content
            file_path.write_text("initial content")

            # Safe write should overwrite
            FileHandler.safe_write(file_path, "new content")
            assert file_path.read_text() == "new content"

    def test_file_exists_and_readable(self):
        """Test file existence and readability check."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = Path(f.name)

        try:
            assert FileHandler.file_exists_and_readable(temp_file) is True

            # Test with non-existent file
            non_existent = Path("/tmp/does_not_exist.txt")
            assert FileHandler.file_exists_and_readable(non_existent) is False
        finally:
            temp_file.unlink(missing_ok=True)

    def test_safe_write_exception_cleanup(self):
        """Test that temporary file is cleaned up on exception."""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            temp_path = file_path.with_suffix(file_path.suffix + '.tmp')

            # Mock temp_path.replace to raise exception
            with unittest.mock.patch.object(Path, 'replace', side_effect=OSError("Test error")):
                with pytest.raises(OSError):
                    FileHandler.safe_write(file_path, "test content")

                # Verify temp file was cleaned up
                assert not temp_path.exists()

    def test_safe_write_windows_path(self):
        """Test Windows-specific file handling."""

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "existing.txt"
            # Create existing file
            file_path.write_text("existing content")

            # Mock os.name to simulate Windows
            with unittest.mock.patch.object(os, 'name', 'nt'):
                FileHandler.safe_write(file_path, "new content")
                assert file_path.read_text() == "new content"
