from typing import List, Optional
from datetime import datetime

from src.application.dto import TodoResponseDto, TodoListDto


class ConsoleUtils:
    """Utility class for console display and input."""
    
    @staticmethod
    def display_header(title: str, width: int = 60) -> None:
        """Display a formatted header."""
        print("=" * width)
        print(f"{title:^{width}}")
        print("=" * width)
    
    @staticmethod
    def display_menu(title: str, options: List[str]) -> None:
        """Display a menu with numbered options."""
        print(f"\n{title}")
        print("-" * len(title))
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print()
    
    @staticmethod
    def display_todos(todo_list: TodoListDto) -> None:
        """Display a formatted list of todos."""
        if not todo_list.todos:
            print("No todos found.")
            return
        
        print(f"\nTodos ({todo_list.total_count} total, "
              f"{todo_list.pending_count} pending, "
              f"{todo_list.completed_count} completed):")
        print("-" * 80)
        
        for todo in todo_list.todos:
            print(ConsoleUtils.format_todo_display(todo))
        print("-" * 80)
    
    @staticmethod
    def format_todo_display(todo: TodoResponseDto) -> str:
        """Format a single todo for display."""
        status_symbol = "[✓]" if todo.completed else "[ ]"
        priority_symbol = {
            "low": "▼",
            "medium": "●", 
            "high": "▲"
        }.get(todo.priority, "●")
        
        # Truncate title if too long
        title = todo.title[:50] + "..." if len(todo.title) > 50 else todo.title
        
        # Format creation date
        created = todo.created_at.strftime("%Y-%m-%d %H:%M")
        
        return (f"{status_symbol} {priority_symbol} {title:<55} "
               f"(ID: {todo.id[:8]}...) [{created}]")
    
    @staticmethod
    def display_todo_details(todo: TodoResponseDto) -> None:
        """Display detailed information about a todo."""
        print("\nTodo Details:")
        print("-" * 40)
        print(f"ID: {todo.id}")
        print(f"Title: {todo.title}")
        print(f"Description: {todo.description or 'No description'}")
        print(f"Status: {'Completed' if todo.completed else 'Pending'}")
        print(f"Priority: {todo.priority.upper()}")
        print(f"Created: {todo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if todo.updated_at:
            print(f"Updated: {todo.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 40)
    
    @staticmethod
    def get_user_input(prompt: str, default: Optional[str] = None) -> str:
        """Get user input with optional default value."""
        if default:
            prompt = f"{prompt} (default: {default}): "
        else:
            prompt = f"{prompt}: "
        
        user_input = input(prompt).strip()
        return user_input if user_input else (default or "")
    
    @staticmethod
    def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
        """Get user choice from a list of valid options."""
        while True:
            choice = ConsoleUtils.get_user_input(prompt).lower()
            if choice in [c.lower() for c in valid_choices]:
                return choice
            
            print(f"Invalid choice. Please select from: {', '.join(valid_choices)}")
    
    @staticmethod
    def get_menu_choice(max_option: int) -> int:
        """Get a menu choice as an integer."""
        while True:
            try:
                choice = int(ConsoleUtils.get_user_input("Enter your choice"))
                if 1 <= choice <= max_option:
                    return choice
                else:
                    print(f"Please enter a number between 1 and {max_option}")
            except ValueError:
                print("Please enter a valid number")
    
    @staticmethod
    def confirm_action(message: str) -> bool:
        """Get confirmation from user."""
        choice = ConsoleUtils.get_user_choice(f"{message} (y/n)", ["y", "yes", "n", "no"])
        return choice in ["y", "yes"]
    
    @staticmethod
    def display_error(message: str) -> None:
        """Display an error message."""
        print(f"\n❌ Error: {message}\n")
    
    @staticmethod
    def display_success(message: str) -> None:
        """Display a success message."""
        print(f"\n✅ {message}\n")
    
    @staticmethod
    def display_info(message: str) -> None:
        """Display an info message."""
        print(f"\nℹ️  {message}\n")
    
    @staticmethod
    def clear_screen() -> None:
        """Clear the console screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def pause() -> None:
        """Pause and wait for user to press Enter."""
        input("\nPress Enter to continue...")