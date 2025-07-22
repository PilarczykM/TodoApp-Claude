from typing import Literal

from src.interfaces.console_utils import ConsoleUtils

StorageFormat = Literal["json", "xml"]


class FormatSelector:
    """Handles storage format selection at application startup."""

    @staticmethod
    def select_storage_format() -> StorageFormat:
        """Allow user to select storage format."""
        ConsoleUtils.display_header("Todo App - Storage Format Selection")

        print("Welcome to the Todo List Application!")
        print("Please choose your preferred data storage format:\n")

        ConsoleUtils.display_menu("Storage Format Options", ["JSON format (.json file)", "XML format (.xml file)"])

        while True:
            try:
                choice = ConsoleUtils.get_menu_choice(2)

                if choice == 1:
                    ConsoleUtils.display_success("JSON format selected")
                    return "json"
                elif choice == 2:
                    ConsoleUtils.display_success("XML format selected")
                    return "xml"

            except Exception as e:
                ConsoleUtils.display_error(f"Invalid selection: {e}")

    @staticmethod
    def display_format_info() -> None:
        """Display information about storage formats."""
        print("Storage Format Information:")
        print("- JSON: Lightweight, human-readable, commonly used")
        print("- XML: Structured, self-documenting, widely supported")
        print()
