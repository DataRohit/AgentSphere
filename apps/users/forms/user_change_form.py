# Third-party imports
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

# Get the user model
User = get_user_model()


# Form for changing user information
class UserChangeForm(BaseUserChangeForm):
    """
    Form for modifying existing user information.

    Extends Django's base user change form to customize fields
    and validation for user profile updates.

    Attributes:
        Meta: Inner class defining model and form fields
    """

    # Class for configuration
    class Meta(BaseUserChangeForm.Meta):
        """
        Configuration class for UserChangeForm.

        Attributes:
            model: The user model to use for the form
            fields: List of fields to include in the form
        """

        # Attributes
        model = User
        fields = ["first_name", "last_name", "username", "email"]
