"""WSGI configuration for AgentSphere project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
from django.core.handlers.wsgi import WSGIHandler
from django.core.wsgi import get_wsgi_application

# Set the base directory for the project
BASE_DIR: Path = Path(__file__).resolve(strict=True).parent.parent

# Add the apps directory to the Python path
sys.path.append(str(BASE_DIR / "apps"))

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Get the WSGI application
application: WSGIHandler = get_wsgi_application()
