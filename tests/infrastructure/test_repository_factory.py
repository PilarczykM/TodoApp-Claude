"""Tests for repository factory."""

from pathlib import Path
import tempfile
import pytest

from src.infrastructure.repository_factory import RepositoryFactory
from src.infrastructure.json_repository import JsonTodoRepository
from src.infrastructure.xml_repository import XmlTodoRepository


class TestRepositoryFactory:
    """Test cases for RepositoryFactory."""
    
    def test_create_json_repository(self):
        """Test creating JSON repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            repo = RepositoryFactory.create_repository("json", data_dir)
            assert isinstance(repo, JsonTodoRepository)
    
    def test_create_xml_repository(self):
        """Test creating XML repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            repo = RepositoryFactory.create_repository("xml", data_dir)
            assert isinstance(repo, XmlTodoRepository)
    
    def test_invalid_format(self):
        """Test creating repository with invalid format raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            with pytest.raises(ValueError, match="Unsupported storage format: invalid"):
                RepositoryFactory.create_repository("invalid", data_dir)
    
    def test_get_supported_formats(self):
        """Test getting supported storage formats."""
        formats = RepositoryFactory.get_supported_formats()
        assert "json" in formats
        assert "xml" in formats
        assert len(formats) == 2