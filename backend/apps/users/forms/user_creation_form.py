# Standard library imports
from typing import ClassVar

# Third-party imports
from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model

# Get the user model
User = get_user_model()


# Form for creating new users
class UserCreationForm(admin_forms.UserCreationForm):
    """
    Form for creating new user accounts.

    Extends Django's admin user creation form to add custom
    validation for username and email uniqueness.

    Attributes:
        error_messages: Dictionary of custom error messages
        Meta: Inner class defining model and form fields
    """

    # Class for configuration
    class Meta(admin_forms.UserCreationForm.Meta):
        """
        Configuration class for UserCreationForm.

        Attributes:
            model: The user model to use for the form
            fields: List of fields to include in the form
        """

        # Attributes
        model = User
        fields = ["first_name", "last_name", "username", "email"]

    # Custom error messages for form validation
    error_messages: ClassVar[dict[str, str]] = {
        "duplicate_username": "A user with that username already exists.",
        "duplicate_email": "A user with that email already exists.",
    }

    # Clean the email
    def clean_email(self) -> str:
        """
        Validate that the email address is unique.

        Returns:
            str: The cleaned email address if valid

        Raises:
            forms.ValidationError: If email is already in use
        """

        # Get the email from cleaned data
        email = self.cleaned_data["email"]

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            # Raise a validation error
            raise forms.ValidationError(
                self.error_messages["duplicate_email"],
            ) from None

        # Return the email
        return email

    # Clean the username
    def clean_username(self) -> str:
        """
        Validate that the username is unique.

        Returns:
            str: The cleaned username if valid

        Raises:
            forms.ValidationError: If username is already in use
        """

        # Get the username from cleaned data
        username = self.cleaned_data["username"]

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            # Raise a validation error
            raise forms.ValidationError(
                self.error_messages["duplicate_username"],
            ) from None

        # Return the username
        return username
