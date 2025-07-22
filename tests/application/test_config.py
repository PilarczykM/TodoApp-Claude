import tempfile
from pathlib import Path

import pytest

from src.application import AppConfig


def test_app_config_creation():
    with tempfile.TemporaryDirectory() as temp_dir:
        config = AppConfig(
            storage_format="json",
            data_directory=Path(temp_dir)
        )
        assert config.storage_format == "json"
        assert config.data_directory == Path(temp_dir)
        assert config.backup_enabled is True


def test_app_config_validation():
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(ValueError):
            AppConfig(
                storage_format="invalid",
                data_directory=Path(temp_dir)
            )
