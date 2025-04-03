# Standard library imports
from typing import TYPE_CHECKING
from typing import Any

# Third-party imports
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager

# Type checking imports
if TYPE_CHECKING:
    # Type checking imports
    from .models import User


# Custom user manager for handling user creation and management
class UserManager(DjangoUserManager["User"]):
    """
    Custom manager for User model that extends Django's UserManager.

    Handles user creation and management with email-based authentication
    instead of username-based authentication.

    Attributes:
        model: The User model class this manager is attached to
        _db: The database alias to use for queries
    """

    def _create_user(
        self,
        email: str,
        password: str | None,
        **extra_fields: dict[str, Any],
    ) -> "User":
        """
        Create and save a user with the given email and password.

        Args:
            email: The user's email address
            password: The user's password (optional)
            **extra_fields: Additional fields to be set on the user model

        Returns:
            User: The created user instance

        Raises:
            ValueError: If the email is not provided
        """
        # Validate email is provided
        if not email:
            msg = "The given email must be set"
            raise ValueError(msg)

        # Normalize the email address
        email = self.normalize_email(email)

        # Create new user instance
        user = self.model(email=email, **extra_fields)

        # Set the user's password
        user.password = make_password(password)

        # Save the user to database
        user.save(using=self._db)

        return user

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: dict[str, Any],
    ) -> "User":  # type: ignore[override]
        """
        Create and save a regular user with the given email and password.

        Args:
            email: The user's email address
            password: The user's password (optional)
            **extra_fields: Additional fields to be set on the user model

        Returns:
            User: The created regular user instance
        """
        # Set default permissions for regular user
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        # Create the user using base method
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: dict[str, Any],
    ) -> "User":  # type: ignore[override]
        """
        Create and save a superuser with the given email and password.

        Args:
            email: The user's email address
            password: The user's password (optional)
            **extra_fields: Additional fields to be set on the user model

        Returns:
            User: The created superuser instance

        Raises:
            ValueError: If is_staff or is_superuser is not True
        """
        # Set default permissions for superuser
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Validate superuser has required permissions
        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)

        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        # Create the superuser using base method
        return self._create_user(email, password, **extra_fields)
