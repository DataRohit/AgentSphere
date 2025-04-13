#!/usr/bin/env python

# -----------------------------------------
# Django management script
# -----------------------------------------

# Standard library imports
import os
import sys
from pathlib import Path
from typing import NoReturn


# Main function for Django administrative tasks
def main() -> NoReturn:
    """
    Run Django administrative tasks.

    Sets up the Django environment and runs management commands.
    Configures Python path to include the agentsphere directory.

    Raises:
        ImportError: If Django is not installed or not in PYTHONPATH.
    """

    # Set default Django settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        # Import Django management module
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Raise a more descriptive error message
        raise ImportError(  # noqa: TRY003
            "Couldn't import Django. Are you sure it's installed and "  # noqa: EM101
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?",
        ) from exc

    # Get the current directory path
    current_path = Path(__file__).parent.resolve()

    # Add apps directory to Python path
    sys.path.append(str(current_path / "apps"))

    # Execute Django management command
    execute_from_command_line(sys.argv)


# Execute main function when script is run directly
if __name__ == "__main__":
    # Call the main function
    main()
