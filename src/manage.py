#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def main():
    # Ensure project packages inside /src are on PYTHONPATH
    ROOT = Path(__file__).resolve().parent.parent
    sys.path.append(str(ROOT))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
