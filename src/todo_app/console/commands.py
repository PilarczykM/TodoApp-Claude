from uuid import UUID

from ..database.connection import async_session_maker
from ..database.repository import TaskRepository
from ..domain.exceptions import TaskNotFoundError, ValidationError
from ..services.todo_service import TodoService
from .ui import TaskUI


class TaskCommands:
    def __init__(self) -> None:
        self.ui = TaskUI()

    async def _get_service(self) -> TodoService:
        session = async_session_maker()
        repository = TaskRepository(session)
        return TodoService(repository)

    async def create_task(self) -> None:
        try:
            title, description, category = self.ui.get_task_input()

            async with async_session_maker() as session:
                async with session.begin():
                    repository = TaskRepository(session)
                    service = TodoService(repository)

                    task = await service.create_task(
                        title=title, description=description, category=category
                    )

                    self.ui.show_success(f"Task '{task.title}' created successfully!")
                    self.ui.display_task_details(task)

        except ValidationError as e:
            self.ui.show_error(f"Validation error: {e}")
        except Exception as e:
            self.ui.show_error(f"Failed to create task: {e}")

    async def list_tasks(self) -> None:
        try:
            async with async_session_maker() as session:
                repository = TaskRepository(session)
                service = TodoService(repository)

                tasks = await service.get_all_tasks(limit=50)
                self.ui.display_tasks(tasks, "All Tasks")

        except Exception as e:
            self.ui.show_error(f"Failed to retrieve tasks: {e}")

    async def search_tasks(self) -> None:
        try:
            query = self.ui.get_search_query()
            if not query.strip():
                self.ui.show_warning("Search query cannot be empty")
                return

            async with async_session_maker() as session:
                repository = TaskRepository(session)
                service = TodoService(repository)

                tasks = await service.search_tasks(query)
                self.ui.display_tasks(tasks, f"Search Results for '{query}'")

        except Exception as e:
            self.ui.show_error(f"Search failed: {e}")

    async def mark_task_completed(self) -> None:
        try:
            task_id_str = self.ui.get_task_id_input("Enter task ID to mark as completed")
            task_id = UUID(task_id_str)

            async with async_session_maker() as session:
                async with session.begin():
                    repository = TaskRepository(session)
                    service = TodoService(repository)

                    task = await service.mark_completed(task_id)
                    self.ui.show_success(f"Task '{task.title}' marked as completed!")

        except ValueError:
            self.ui.show_error("Invalid task ID format")
        except TaskNotFoundError as e:
            self.ui.show_error(str(e))
        except Exception as e:
            self.ui.show_error(f"Failed to mark task as completed: {e}")

    async def mark_task_pending(self) -> None:
        try:
            task_id_str = self.ui.get_task_id_input("Enter task ID to mark as pending")
            task_id = UUID(task_id_str)

            async with async_session_maker() as session:
                async with session.begin():
                    repository = TaskRepository(session)
                    service = TodoService(repository)

                    task = await service.mark_pending(task_id)
                    self.ui.show_success(f"Task '{task.title}' marked as pending!")

        except ValueError:
            self.ui.show_error("Invalid task ID format")
        except TaskNotFoundError as e:
            self.ui.show_error(str(e))
        except Exception as e:
            self.ui.show_error(f"Failed to mark task as pending: {e}")

    async def edit_task(self) -> None:
        try:
            task_id_str = self.ui.get_task_id_input("Enter task ID to edit")
            task_id = UUID(task_id_str)

            async with async_session_maker() as session:
                async with session.begin():
                    repository = TaskRepository(session)
                    service = TodoService(repository)

                    # First, get the current task
                    current_task = await service.get_task(task_id)
                    self.ui.display_task_details(current_task)

                    # Get updates from user
                    updates = self.ui.get_task_update_input(current_task)

                    if not updates:
                        self.ui.show_info("No changes made")
                        return

                    # Update the task
                    updated_task = await service.update_task(task_id, **updates)
                    self.ui.show_success(f"Task '{updated_task.title}' updated successfully!")
                    self.ui.display_task_details(updated_task)

        except ValueError:
            self.ui.show_error("Invalid task ID format")
        except TaskNotFoundError as e:
            self.ui.show_error(str(e))
        except ValidationError as e:
            self.ui.show_error(f"Validation error: {e}")
        except Exception as e:
            self.ui.show_error(f"Failed to edit task: {e}")

    async def delete_task(self) -> None:
        try:
            task_id_str = self.ui.get_task_id_input("Enter task ID to delete")
            task_id = UUID(task_id_str)

            async with async_session_maker() as session:
                async with session.begin():
                    repository = TaskRepository(session)
                    service = TodoService(repository)

                    # First, show the task details
                    try:
                        task = await service.get_task(task_id)
                        self.ui.display_task_details(task)

                        if not self.ui.confirm_action(f"Delete task '{task.title}'?"):
                            self.ui.show_info("Task deletion cancelled")
                            return

                        # Delete the task
                        success = await service.delete_task(task_id)
                        if success:
                            self.ui.show_success(f"Task '{task.title}' deleted successfully!")
                        else:
                            self.ui.show_error("Failed to delete task")

                    except TaskNotFoundError as e:
                        self.ui.show_error(str(e))

        except ValueError:
            self.ui.show_error("Invalid task ID format")
        except Exception as e:
            self.ui.show_error(f"Failed to delete task: {e}")

    async def show_statistics(self) -> None:
        try:
            async with async_session_maker() as session:
                repository = TaskRepository(session)
                service = TodoService(repository)

                # Get all tasks and categories
                all_tasks = await service.get_all_tasks(limit=1000)
                categories = await service.get_categories()

                # Calculate statistics
                total = len(all_tasks)
                completed = sum(1 for task in all_tasks if task.completed)
                pending = total - completed

                self.ui.show_statistics(total, completed, pending, categories)

        except Exception as e:
            self.ui.show_error(f"Failed to retrieve statistics: {e}")

    async def run_menu_loop(self) -> None:
        self.ui.show_welcome()

        while True:
            try:
                self.ui.show_main_menu()
                choice = self.ui.get_user_choice()

                if choice == "1":
                    await self.create_task()
                elif choice == "2":
                    await self.list_tasks()
                elif choice == "3":
                    await self.search_tasks()
                elif choice == "4":
                    await self.mark_task_completed()
                elif choice == "5":
                    await self.mark_task_pending()
                elif choice == "6":
                    await self.edit_task()
                elif choice == "7":
                    await self.delete_task()
                elif choice == "8":
                    await self.show_statistics()
                elif choice == "9":
                    self.ui.show_info("Thank you for using TODO App! 👋")
                    break

                if choice != "9":
                    self.ui.pause()

            except KeyboardInterrupt:
                self.ui.show_info("\nExiting TODO App. Goodbye! 👋")
                break
            except Exception as e:
                self.ui.show_error(f"Unexpected error: {e}")
                self.ui.pause()
