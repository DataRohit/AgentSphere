"""Django configuration package initialization.

This module initializes the Celery application for task processing
and ensures it's imported when Django starts.
"""

# Third-party imports
from config.celery_app import app as celery_app

# Define public API
__all__ = ("celery_app",)
