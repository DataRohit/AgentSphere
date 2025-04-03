"""ASGI configuration for AgentSphere project.

This module contains the ASGI application used by Django's development server
and any production ASGI deployments.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler

# Set the base directory for the project
BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent

# Add the apps directory to the Python path
sys.path.append(str(BASE_DIR / "apps"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Get the ASGI application
application: ASGIHandler = get_asgi_application()
