
from src.application import CreateTodoDto, TodoService, UpdateTodoDto
from src.domain import Priority, RepositoryError, TodoNotFoundError, TodoValidationError

from src.interfaces.console_utils import ConsoleUtils


class ConsoleInterface:
    """Main console interface for the Todo application."""

    def __init__(self, todo_service: TodoService):
        self._service = todo_service
        self._running = True

    def run(self) -> None:
        """Main application loop."""
        ConsoleUtils.display_header("Todo List Application")
        ConsoleUtils.display_info("Welcome! Manage your tasks efficiently.")

        while self._running:
            try:
                self._display_main_menu()
                choice = ConsoleUtils.get_menu_choice(6)
                self._handle_menu_choice(choice)

            except KeyboardInterrupt:
                ConsoleUtils.display_info("Goodbye!")
                break
            except Exception as e:
                ConsoleUtils.display_error(f"Unexpected error: {e}")
                ConsoleUtils.pause()

    def _display_main_menu(self) -> None:
        """Display the main application menu."""
        ConsoleUtils.display_menu(
            "Main Menu",
            ["List all tasks", "Add new task", "Update task", "Delete task", "Mark task complete/incomplete", "Exit"],
        )

    def _handle_menu_choice(self, choice: int) -> None:
        """Handle user's menu selection."""
        actions = {
            1: self._list_todos,
            2: self._create_todo,
            3: self._update_todo,
            4: self._delete_todo,
            5: self._toggle_completion,
            6: self._exit_application,
        }

        action = actions.get(choice)
        if action:
            success = action()
            if success and choice != 6:  # Don't pause after exit
                ConsoleUtils.pause()

    def _list_todos(self) -> bool:
        """Display all todos."""
        try:
            todo_list = self._service.get_all_todos()

            if not todo_list.todos:
                ConsoleUtils.display_info("No todos found. Create your first task!")
                return True

            ConsoleUtils.display_todos(todo_list)

            # Show filtering options
            print("\nFiltering options:")
            print("1. Show all (current)")
            print("2. Show completed only")
            print("3. Show pending only")
            print("4. Show by priority")
            print("5. Back to main menu")

            filter_choice = ConsoleUtils.get_menu_choice(5)
            if filter_choice == 2:
                completed_todos = self._service.get_todos_by_status(True)
                ConsoleUtils.display_todos(completed_todos)
            elif filter_choice == 3:
                pending_todos = self._service.get_todos_by_status(False)
                ConsoleUtils.display_todos(pending_todos)
            elif filter_choice == 4:
                self._show_todos_by_priority()

            return True

        except RepositoryError as e:
            ConsoleUtils.display_error(f"Failed to load todos: {e}")
            return False

    def _create_todo(self) -> bool:
        """Create a new todo."""
        try:
            ConsoleUtils.display_header("Create New Task")

            title = ConsoleUtils.get_user_input("Enter task title")
            if not title:
                ConsoleUtils.display_error("Title is required")
                return False

            description_input = ConsoleUtils.get_user_input("Enter description (optional)")
            description: str | None = description_input if description_input else None

            priority = ConsoleUtils.get_user_choice("Enter priority (low/medium/high)", ["low", "medium", "high"])

            dto = CreateTodoDto(title=title, description=description, priority=priority)

            todo = self._service.create_todo(dto)
            ConsoleUtils.display_success(f"Task '{todo.title}' created successfully!")

            return True

        except TodoValidationError as e:
            ConsoleUtils.display_error(f"Validation error: {e}")
            return False
        except RepositoryError as e:
            ConsoleUtils.display_error(f"Failed to create todo: {e}")
            return False

    def _update_todo(self) -> bool:
        """Update an existing todo."""
        try:
            todo_id = self._select_todo("update")
            if not todo_id:
                return False

            # Show current todo
            current_todo = self._service.get_todo_by_id(todo_id)
            ConsoleUtils.display_todo_details(current_todo)

            ConsoleUtils.display_header("Update Task")
            print("Leave empty to keep current value")

            new_title = ConsoleUtils.get_user_input("New title", current_todo.title)
            new_description = ConsoleUtils.get_user_input("New description")
            new_priority = ConsoleUtils.get_user_input("New priority (low/medium/high)")

            dto = UpdateTodoDto()

            if new_title != current_todo.title:
                dto.title = new_title
            if new_description:
                dto.description = new_description
            if new_priority and new_priority != current_todo.priority:
                dto.priority = new_priority

            updated_todo = self._service.update_todo(todo_id, dto)
            ConsoleUtils.display_success(f"Task '{updated_todo.title}' updated successfully!")

            return True

        except TodoNotFoundError:
            ConsoleUtils.display_error("Todo not found")
            return False
        except TodoValidationError as e:
            ConsoleUtils.display_error(f"Validation error: {e}")
            return False
        except RepositoryError as e:
            ConsoleUtils.display_error(f"Failed to update todo: {e}")
            return False

    def _delete_todo(self) -> bool:
        """Delete a todo."""
        try:
            todo_id = self._select_todo("delete")
            if not todo_id:
                return False

            # Show todo before deletion
            todo = self._service.get_todo_by_id(todo_id)
            ConsoleUtils.display_todo_details(todo)

            if ConsoleUtils.confirm_action(f"Delete task '{todo.title}'?"):
                success = self._service.delete_todo(todo_id)

                if success:
                    ConsoleUtils.display_success("Task deleted successfully!")
                else:
                    ConsoleUtils.display_error("Failed to delete task")

                return success

            ConsoleUtils.display_info("Delete cancelled")
            return True

        except TodoNotFoundError:
            ConsoleUtils.display_error("Todo not found")
            return False
        except RepositoryError as e:
            ConsoleUtils.display_error(f"Failed to delete todo: {e}")
            return False

    def _toggle_completion(self) -> bool:
        """Toggle completion status of a todo."""
        try:
            todo_id = self._select_todo("toggle completion for")
            if not todo_id:
                return False

            updated_todo = self._service.toggle_completion(todo_id)
            status = "completed" if updated_todo.completed else "pending"

            ConsoleUtils.display_success(f"Task '{updated_todo.title}' marked as {status}!")
            return True

        except TodoNotFoundError:
            ConsoleUtils.display_error("Todo not found")
            return False
        except RepositoryError as e:
            ConsoleUtils.display_error(f"Failed to update todo: {e}")
            return False

    def _select_todo(self, action: str) -> str | None:
        """Allow user to select a todo by showing list and getting ID."""
        try:
            todo_list = self._service.get_all_todos()

            if not todo_list.todos:
                ConsoleUtils.display_info("No todos available")
                return None

            ConsoleUtils.display_header(f"Select Todo to {action.title()}")
            ConsoleUtils.display_todos(todo_list)

            todo_id = ConsoleUtils.get_user_input("Enter todo ID (first 8 characters are enough)")

            # Allow partial ID matching
            if len(todo_id) >= 8:
                for todo in todo_list.todos:
                    if todo.id.startswith(todo_id[:8]):
                        return todo.id

            ConsoleUtils.display_error("Todo not found with that ID")
            return None

        except RepositoryError as e:
            ConsoleUtils.display_error(f"Failed to load todos: {e}")
            return None

    def _show_todos_by_priority(self) -> None:
        """Show todos filtered by priority."""
        priority = ConsoleUtils.get_user_choice("Select priority filter (low/medium/high)", ["low", "medium", "high"])

        priority_enum = Priority(priority)
        filtered_todos = self._service.get_todos_by_priority(priority_enum)

        ConsoleUtils.display_header(f"Tasks with {priority.upper()} Priority")
        ConsoleUtils.display_todos(filtered_todos)

    def _exit_application(self) -> bool:
        """Exit the application."""
        if ConsoleUtils.confirm_action("Are you sure you want to exit?"):
            ConsoleUtils.display_info("Thank you for using Todo List Application!")
            self._running = False
        return True
