#!/usr/bin/env python3
"""
Console Todo List Application

A clean architecture implementation with CRUD operations
and support for both JSON and XML storage formats.
"""

from src.interfaces.main import main as _main


def main() -> None:
    """Entry point for the todo-app console script."""
    _main()


if __name__ == "__main__":
    main()