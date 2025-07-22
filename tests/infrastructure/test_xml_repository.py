"""Tests for XML repository implementation."""

import tempfile
import unittest.mock
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from src.domain.exceptions import RepositoryError, TodoNotFoundError
from src.domain.priority import Priority
from src.domain.todo import Todo
from src.infrastructure.xml_repository import XmlTodoRepository


class TestXmlTodoRepository:
    """Test cases for XmlTodoRepository."""

    def test_xml_repository_save_and_find(self):
        """Test saving and finding a todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task", priority=Priority.HIGH)
            repo.save(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Test Task"
            assert found_todo.priority == Priority.HIGH

    def test_xml_repository_find_all(self):
        """Test finding all todo items."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo1 = Todo(title="Task 1")
            todo2 = Todo(title="Task 2")
            repo.save(todo1)
            repo.save(todo2)

            all_todos = repo.find_all()
            assert len(all_todos) == 2

    def test_xml_repository_delete(self):
        """Test deleting a todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task")
            repo.save(todo)

            deleted = repo.delete(todo.id)
            assert deleted is True
            assert repo.find_by_id(todo.id) is None

    def test_xml_repository_delete_nonexistent(self):
        """Test deleting a non-existent todo item."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            deleted = repo.delete("nonexistent-id")
            assert deleted is False

    def test_xml_repository_persistence(self):
        """Test data persistence between repository instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "todos.xml"

            # First repository instance
            repo1 = XmlTodoRepository(file_path)
            todo = Todo(title="Persistent Task")
            repo1.save(todo)

            # Second repository instance
            repo2 = XmlTodoRepository(file_path)
            found_todo = repo2.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Persistent Task"

    def test_xml_repository_exists(self):
        """Test checking if a todo exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task")
            repo.save(todo)

            assert repo.exists(todo.id) is True
            assert repo.exists("nonexistent-id") is False

    def test_xml_repository_update(self):
        """Test updating an existing todo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Original Task")
            repo.save(todo)

            # Update the todo
            todo.title = "Updated Task"
            todo.completed = True
            repo.update(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.title == "Updated Task"
            assert found_todo.completed is True

    def test_xml_repository_update_nonexistent(self):
        """Test updating a non-existent todo raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Nonexistent Task")
            with pytest.raises(TodoNotFoundError):
                repo.update(todo)

    def test_xml_repository_count(self):
        """Test counting todo items."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            assert repo.count() == 0

            todo1 = Todo(title="Task 1")
            todo2 = Todo(title="Task 2")
            repo.save(todo1)
            repo.save(todo2)

            assert repo.count() == 2

    def test_xml_repository_with_description(self):
        """Test XML repository with todo that has description."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task", description="Detailed description")
            repo.save(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.description == "Detailed description"

    def test_xml_repository_save_error_handling(self):
        """Test error handling in save method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")
            todo = Todo(title="Test Task")

            # Mock _save_xml_root to raise exception
            with unittest.mock.patch.object(repo, '_save_xml_root', side_effect=Exception("Save error")):
                with pytest.raises(RepositoryError, match="Failed to save todo"):
                    repo.save(todo)

    def test_xml_repository_find_by_id_error_handling(self):
        """Test error handling in find_by_id method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Mock _load_xml_root to raise exception
            with unittest.mock.patch.object(repo, '_load_xml_root', side_effect=Exception("Load error")):
                with pytest.raises(RepositoryError, match="Failed to find todo"):
                    repo.find_by_id("test-id")

    def test_xml_repository_find_all_error_handling(self):
        """Test error handling in find_all method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Mock _load_xml_root to raise exception
            with unittest.mock.patch.object(repo, '_load_xml_root', side_effect=Exception("Load error")):
                with pytest.raises(RepositoryError, match="Failed to load todos"):
                    repo.find_all()

    def test_xml_repository_find_all_empty(self):
        """Test find_all with no todos."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            all_todos = repo.find_all()
            assert all_todos == []

    def test_xml_repository_delete_error_handling(self):
        """Test error handling in delete method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Mock _load_xml_root to raise exception
            with unittest.mock.patch.object(repo, '_load_xml_root', side_effect=Exception("Load error")):
                with pytest.raises(RepositoryError, match="Failed to delete todo"):
                    repo.delete("test-id")

    def test_xml_repository_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "nonexistent.xml"
            repo = XmlTodoRepository(file_path)

            root = repo._load_xml_root()
            assert root.tag == "todos"

    def test_xml_repository_load_invalid_xml(self):
        """Test loading from file with invalid XML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.xml"
            file_path.write_text("not valid xml", encoding='utf-8')

            repo = XmlTodoRepository(file_path)
            with pytest.raises(RepositoryError, match="Invalid XML format"):
                repo._load_xml_root()

    def test_xml_repository_save_error_in_write(self):
        """Test error handling when XML write fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")
            root = ET.Element("todos")

            # Mock FileHandler.safe_write to raise exception
            with unittest.mock.patch('src.infrastructure.xml_repository.FileHandler.safe_write',
                                   side_effect=Exception("Write error")):
                with pytest.raises(RepositoryError, match="Failed to write XML file"):
                    repo._save_xml_root(root)

    def test_xml_repository_todo_with_updated_at(self):
        """Test todo with updated_at field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            todo = Todo(title="Test Task")
            todo.mark_completed()  # This sets updated_at
            repo.save(todo)

            found_todo = repo.find_by_id(todo.id)
            assert found_todo is not None
            assert found_todo.updated_at is not None

    def test_xml_element_to_todo_missing_id(self):
        """Test XML element missing required ID attribute."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Create element without ID
            element = ET.Element("todo")
            with pytest.raises(RepositoryError, match="Todo element missing required 'id' attribute"):
                repo._xml_element_to_todo(element)

    def test_xml_element_to_todo_missing_title(self):
        """Test XML element missing required title field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Create element with ID but no title
            element = ET.Element("todo", id="test-id")
            with pytest.raises(RepositoryError, match="Todo element missing required 'title' field"):
                repo._xml_element_to_todo(element)

    def test_xml_element_to_todo_missing_completed(self):
        """Test XML element missing required completed field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Create element with ID and title but no completed
            element = ET.Element("todo", id="test-id")
            title_elem = ET.SubElement(element, "title")
            title_elem.text = "Test"

            with pytest.raises(RepositoryError, match="Todo element missing required 'completed' field"):
                repo._xml_element_to_todo(element)

    def test_xml_element_to_todo_missing_priority(self):
        """Test XML element missing required priority field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Create element with ID, title, completed but no priority
            element = ET.Element("todo", id="test-id")
            title_elem = ET.SubElement(element, "title")
            title_elem.text = "Test"
            completed_elem = ET.SubElement(element, "completed")
            completed_elem.text = "false"

            with pytest.raises(RepositoryError, match="Todo element missing required 'priority' field"):
                repo._xml_element_to_todo(element)

    def test_xml_element_to_todo_missing_created_at(self):
        """Test XML element missing required created_at field."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = XmlTodoRepository(Path(temp_dir) / "todos.xml")

            # Create element with all fields except created_at
            element = ET.Element("todo", id="test-id")
            title_elem = ET.SubElement(element, "title")
            title_elem.text = "Test"
            completed_elem = ET.SubElement(element, "completed")
            completed_elem.text = "false"
            priority_elem = ET.SubElement(element, "priority")
            priority_elem.text = "medium"

            with pytest.raises(RepositoryError, match="Todo element missing required 'created_at' field"):
                repo._xml_element_to_todo(element)

    def test_xml_repository_load_xml_root_nonexistent_file_direct(self):
        """Test _load_xml_root directly with truly non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "truly_nonexistent.xml"
            repo = XmlTodoRepository.__new__(XmlTodoRepository)  # Create without calling __init__
            repo.file_path = file_path  # Set the file path directly

            # Now call _load_xml_root which should hit the non-existent file branch
            root = repo._load_xml_root()
            assert root.tag == "todos"
            assert len(list(root)) == 0  # Should be empty
