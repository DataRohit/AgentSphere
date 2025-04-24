"""Celery configuration for AgentSphere project.

This module contains the Celery application used for task processing
and asynchronous job execution.
"""

# Standard library imports
import os
from logging.config import dictConfig

# Third-party imports
from celery import Celery
from celery.signals import setup_logging
from django.conf import settings

# Set the default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create Celery application instance
app: Celery = Celery("agentsphere")

# Load configuration from Django settings with CELERY namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Discover tasks from all registered Django apps
app.autodiscover_tasks()


# Logging configuration
@setup_logging.connect
def config_loggers(*args, **kwargs) -> None:
    """Configure Celery logging using Django settings.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        None
    """

    # Configure Celery logging
    dictConfig(settings.LOGGING)
