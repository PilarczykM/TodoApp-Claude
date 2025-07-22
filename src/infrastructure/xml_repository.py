"""XML file-based implementation of TodoRepository."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from src.domain.todo import Todo
from src.domain.repository import TodoRepository
from src.domain.exceptions import RepositoryError, TodoNotFoundError
from src.domain.priority import Priority
from src.infrastructure.file_handler import FileHandler


class XmlTodoRepository(TodoRepository):
    """XML file-based implementation of TodoRepository."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def save(self, todo: Todo) -> None:
        """Save a todo item to XML storage."""
        try:
            root = self._load_xml_root()
            
            # Remove existing todo with same ID if it exists
            for existing in root.findall(f".//todo[@id='{todo.id}']"):
                root.remove(existing)
            
            # Add updated todo
            todo_element = self._todo_to_xml_element(todo)
            root.append(todo_element)
            
            self._save_xml_root(root)
        except Exception as e:
            raise RepositoryError(f"Failed to save todo: {e}")
    
    def find_by_id(self, todo_id: str) -> Optional[Todo]:
        """Find a todo item by its ID."""
        try:
            root = self._load_xml_root()
            todo_element = root.find(f".//todo[@id='{todo_id}']")
            
            if todo_element is not None:
                return self._xml_element_to_todo(todo_element)
            return None
        except Exception as e:
            raise RepositoryError(f"Failed to find todo: {e}")
    
    def find_all(self) -> List[Todo]:
        """Retrieve all todo items."""
        try:
            root = self._load_xml_root()
            todos = []
            
            for todo_element in root.findall(".//todo"):
                todos.append(self._xml_element_to_todo(todo_element))
            
            return todos
        except Exception as e:
            raise RepositoryError(f"Failed to load todos: {e}")
    
    def delete(self, todo_id: str) -> bool:
        """Delete a todo item by ID."""
        try:
            root = self._load_xml_root()
            todo_element = root.find(f".//todo[@id='{todo_id}']")
            
            if todo_element is not None:
                root.remove(todo_element)
                self._save_xml_root(root)
                return True
            return False
        except Exception as e:
            raise RepositoryError(f"Failed to delete todo: {e}")
    
    def exists(self, todo_id: str) -> bool:
        """Check if a todo item exists."""
        return self.find_by_id(todo_id) is not None
    
    def update(self, todo: Todo) -> None:
        """Update an existing todo item."""
        if not self.exists(todo.id):
            raise TodoNotFoundError(todo.id)
        self.save(todo)
    
    def count(self) -> int:
        """Return the total number of todo items."""
        root = self._load_xml_root()
        return len(root.findall(".//todo"))
    
    def _load_xml_root(self) -> ET.Element:
        """Load XML root element from file."""
        if not self.file_path.exists():
            return ET.Element("todos")
        
        try:
            tree = ET.parse(self.file_path)
            return tree.getroot()
        except ET.ParseError as e:
            raise RepositoryError(f"Invalid XML format: {e}")
    
    def _save_xml_root(self, root: ET.Element) -> None:
        """Save XML root element to file."""
        try:
            # Create backup if file exists
            if self.file_path.exists():
                FileHandler.create_backup(self.file_path)
            
            # Format XML with proper indentation
            self._indent_xml(root)
            tree = ET.ElementTree(root)
            
            # Write to temporary file then move atomically
            xml_content = ET.tostring(root, encoding='unicode', xml_declaration=True)
            FileHandler.safe_write(self.file_path, xml_content)
            
        except Exception as e:
            raise RepositoryError(f"Failed to write XML file: {e}")
    
    def _todo_to_xml_element(self, todo: Todo) -> ET.Element:
        """Convert Todo object to XML element."""
        todo_elem = ET.Element("todo", id=todo.id)
        
        title_elem = ET.SubElement(todo_elem, "title")
        title_elem.text = todo.title
        
        if todo.description:
            desc_elem = ET.SubElement(todo_elem, "description")
            desc_elem.text = todo.description
        
        completed_elem = ET.SubElement(todo_elem, "completed")
        completed_elem.text = str(todo.completed).lower()
        
        priority_elem = ET.SubElement(todo_elem, "priority")
        priority_elem.text = todo.priority.value
        
        created_elem = ET.SubElement(todo_elem, "created_at")
        created_elem.text = todo.created_at.isoformat()
        
        if todo.updated_at:
            updated_elem = ET.SubElement(todo_elem, "updated_at")
            updated_elem.text = todo.updated_at.isoformat()
        
        return todo_elem
    
    def _xml_element_to_todo(self, element: ET.Element) -> Todo:
        """Convert XML element to Todo object."""
        todo_id = element.get("id")
        title = element.find("title").text
        description_elem = element.find("description")
        description = description_elem.text if description_elem is not None else None
        completed = element.find("completed").text.lower() == "true"
        priority = Priority(element.find("priority").text)
        created_at = datetime.fromisoformat(element.find("created_at").text)
        
        updated_elem = element.find("updated_at")
        updated_at = datetime.fromisoformat(updated_elem.text) if updated_elem is not None else None
        
        return Todo(
            id=todo_id,
            title=title,
            description=description,
            completed=completed,
            priority=priority,
            created_at=created_at,
            updated_at=updated_at,
        )
    
    def _indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Add proper indentation to XML elements."""
        indent = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
    
    def _ensure_file_exists(self) -> None:
        """Ensure the data directory and file exist."""
        FileHandler.ensure_data_directory(self.file_path.parent)
        if not self.file_path.exists():
            root = ET.Element("todos")
            self._save_xml_root(root)