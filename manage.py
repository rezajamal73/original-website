
#!/usr/bin/env python
"""
Django management utility.

Project: Parsa Novin Kavosh
Website: https://nkavosh.com

Production environment:
    Django
    SQLite
    cPanel

The production settings module is the default.
An explicitly configured DJANGO_SETTINGS_MODULE
environment variable takes precedence.
"""

import os
import sys


def main():
    """
    Execute Django administrative commands.
    """

    # ==================================================
    # DJANGO SETTINGS
    # ==================================================

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "original_website.setting.dev",
    )

    # ==================================================
    # DJANGO MANAGEMENT
    # ==================================================

    try:
        from django.core.management import (
            execute_from_command_line,
        )

    except ImportError as exc:

        raise ImportError(
            "Django could not be imported. "
            "Check the Python virtual environment "
            "and installed dependencies in cPanel."
        ) from exc

    # ==================================================
    # EXECUTE COMMAND
    # ==================================================

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
