import asyncio
import sys

from .commands import TaskCommands


async def main() -> None:
    """Main entry point for the console application."""
    commands = TaskCommands()
    await commands.run_menu_loop()


def console_main() -> None:
    """Sync entry point that runs the async main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    console_main()
