from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from ..domain.models import Task

console = Console()


class TaskUI:
    def __init__(self) -> None:
        self.console = console

    def show_welcome(self) -> None:
        title = Text("🚀 TODO Application", style="bold blue")
        subtitle = Text("Manage your tasks efficiently", style="italic")

        welcome_panel = Panel(f"{title}\n{subtitle}", title="Welcome", border_style="blue")
        self.console.print(welcome_panel)

    def show_main_menu(self) -> None:
        menu_options = """
[bold cyan]Main Menu[/bold cyan]

[1] 📝 Create new task
[2] 📋 List all tasks  
[3] 🔍 Search tasks
[4] ✅ Mark task complete
[5] ❌ Mark task pending
[6] ✏️  Edit task
[7] 🗑️  Delete task
[8] 📊 Show statistics
[9] 🚪 Exit

Choose an option (1-9):"""

        self.console.print(Panel(menu_options, border_style="green"))

    def display_tasks(self, tasks: list[Task], title: str = "Tasks") -> None:
        if not tasks:
            self.console.print("[yellow]No tasks found.[/yellow]")
            return

        table = Table(title=title, show_header=True, header_style="bold magenta")

        table.add_column("ID", style="dim", min_width=8)
        table.add_column("Title", style="cyan", min_width=20)
        table.add_column("Category", style="green", min_width=12)
        table.add_column("Status", justify="center", min_width=10)
        table.add_column("Created", style="dim", min_width=12)
        table.add_column("Description", style="dim", overflow="fold")

        for task in tasks:
            status = "✅ Done" if task.completed else "⏳ Pending"
            status_style = "green" if task.completed else "yellow"

            created_date = task.created_at.strftime("%Y-%m-%d") if task.created_at else "N/A"
            description = (
                task.description[:50] + "..."
                if task.description and len(task.description) > 50
                else task.description or ""
            )

            table.add_row(
                str(task.id)[:8] if task.id else "",
                task.title,
                task.category,
                f"[{status_style}]{status}[/{status_style}]",
                created_date,
                description,
            )

        self.console.print(table)

    def display_task_details(self, task: Task) -> None:
        status = "✅ Completed" if task.completed else "⏳ Pending"
        status_style = "green" if task.completed else "yellow"

        details = f"""
[bold cyan]Title:[/bold cyan] {task.title}
[bold cyan]Category:[/bold cyan] {task.category}
[bold cyan]Status:[/bold cyan] [{status_style}]{status}[/{status_style}]
[bold cyan]Created:[/bold cyan] {task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else "N/A"}
[bold cyan]Updated:[/bold cyan] {task.updated_at.strftime("%Y-%m-%d %H:%M:%S") if task.updated_at else "N/A"}
[bold cyan]Description:[/bold cyan] {task.description or "No description"}
"""

        panel = Panel(details, title=f"Task Details - {task.id}", border_style="blue", expand=False)
        self.console.print(panel)

    def get_task_input(self) -> tuple[str, str | None, str]:
        self.console.print("\n[bold green]Create New Task[/bold green]")

        title = Prompt.ask("📝 Task title", default="")
        while not title.strip():
            self.console.print("[red]Title cannot be empty![/red]")
            title = Prompt.ask("📝 Task title", default="")

        description = Prompt.ask("📄 Task description (optional)", default="")
        description = description if description.strip() else None

        category = Prompt.ask("🏷️  Category", default="General")
        category = category if category.strip() else "General"

        return title.strip(), description, category.strip()

    def get_task_update_input(self, task: Task) -> dict[str, any]:
        self.console.print(f"\n[bold green]Edit Task: {task.title}[/bold green]")

        updates = {}

        new_title = Prompt.ask("📝 New title (press Enter to keep current)", default="")
        if new_title.strip():
            updates["title"] = new_title.strip()

        new_description = Prompt.ask("📄 New description (press Enter to keep current)", default="")
        if new_description.strip():
            updates["description"] = new_description.strip()

        new_category = Prompt.ask("🏷️  New category (press Enter to keep current)", default="")
        if new_category.strip():
            updates["category"] = new_category.strip()

        return updates

    def get_search_query(self) -> str:
        return Prompt.ask("🔍 Enter search term")

    def get_task_id_input(self, prompt_message: str = "Enter task ID") -> str:
        return Prompt.ask(f"🔢 {prompt_message}")

    def get_user_choice(self) -> str:
        return Prompt.ask("Your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])

    def confirm_action(self, message: str) -> bool:
        return Confirm.ask(f"⚠️  {message}")

    def show_success(self, message: str) -> None:
        self.console.print(f"[green]✅ {message}[/green]")

    def show_error(self, message: str) -> None:
        self.console.print(f"[red]❌ {message}[/red]")

    def show_warning(self, message: str) -> None:
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")

    def show_info(self, message: str) -> None:
        self.console.print(f"[blue]ℹ️  {message}[/blue]")

    def show_statistics(
        self, total: int, completed: int, pending: int, categories: list[str]
    ) -> None:
        completion_rate = (completed / total * 100) if total > 0 else 0

        stats = f"""
[bold cyan]Total Tasks:[/bold cyan] {total}
[bold green]Completed:[/bold green] {completed}
[bold yellow]Pending:[/bold yellow] {pending}
[bold blue]Completion Rate:[/bold blue] {completion_rate:.1f}%
[bold magenta]Categories:[/bold magenta] {len(categories)}
"""

        if categories:
            category_list = ", ".join(categories[:5])
            if len(categories) > 5:
                category_list += f" and {len(categories) - 5} more..."
            stats += f"[dim]({category_list})[/dim]"

        panel = Panel(stats, title="📊 Task Statistics", border_style="cyan", expand=False)
        self.console.print(panel)

    def pause(self) -> None:
        Prompt.ask("\nPress Enter to continue", default="")
