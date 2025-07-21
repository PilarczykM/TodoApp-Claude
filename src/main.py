import sys

import click
import uvicorn

from todo_app.config import get_settings


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """TODO Application - Manage your tasks efficiently.

    Run with --help to see available commands.
    """
    if version:
        click.echo("TODO Application v1.0.0")
        return

    if ctx.invoked_subcommand is None:
        # Default behavior: show help
        click.echo(ctx.get_help())


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=8000, help="Port to bind the server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def api(host: str, port: int, reload: bool) -> None:
    """Start the FastAPI server for the TODO application."""
    settings = get_settings()

    click.echo(f"🚀 Starting TODO API server on {host}:{port}")
    click.echo(f"📚 API Documentation: http://{host}:{port}/api/docs")
    click.echo(f"🔄 Debug mode: {settings.debug}")

    uvicorn.run(
        "todo_app.api.main:app",
        host=host,
        port=port,
        reload=reload or settings.debug,
        log_level=settings.log_level.lower(),
    )


@cli.command()
def console() -> None:
    """Start the interactive console interface for the TODO application."""
    from todo_app.console.main import console_main

    click.echo("🖥️  Starting TODO Console Application...")
    console_main()


@cli.command()
@click.option(
    "--mode", type=click.Choice(["console", "api"]), prompt="Choose mode", help="Application mode"
)
@click.option("--host", default="0.0.0.0", help="Host for API mode")
@click.option("--port", default=8000, help="Port for API mode")
def run(mode: str, host: str, port: int) -> None:
    """Interactive mode selector for the TODO application."""
    if mode == "console":
        from todo_app.console.main import console_main

        console_main()
    elif mode == "api":
        settings = get_settings()
        uvicorn.run(
            "todo_app.api.main:app",
            host=host,
            port=port,
            reload=settings.debug,
            log_level=settings.log_level.lower(),
        )


def main() -> None:
    """Main entry point for the application."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Fatal error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
