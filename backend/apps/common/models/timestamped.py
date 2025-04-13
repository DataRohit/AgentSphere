# Standard library imports
import uuid

# Third-party imports
from django.db import models
from django.utils.translation import gettext_lazy as _


# Base abstract model with timestamp fields
class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields.

    This model serves as a base for other models, providing common fields like
    a UUID primary key and timestamp fields for tracking creation and updates.

    Attributes:
        id (UUIDField): Primary key and unique identifier.
        created_at (DateTimeField): Timestamp when the instance was created.
        updated_at (DateTimeField): Timestamp when the instance was last updated.

    Meta:
        abstract (bool): Marks this as an abstract model that won't create a table.
    """

    # UUID field for unique identification and primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    # Timestamp when the instance was created
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
    )

    # Timestamp when the instance was last updated
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        auto_now=True,
    )

    class Meta:
        """Meta class for TimeStampedModel configuration.

        Attributes:
            abstract (bool): Marks this as an abstract model.
        """

        # Mark as abstract model
        abstract = True
