# Third-party imports
from django.core import validators
from django.utils.translation import gettext_lazy as _


# Custom validator for username field validation
class UsernameValidator(validators.RegexValidator):
    """
    Custom validator for enforcing username format rules.

    Extends Django's RegexValidator to provide specific validation rules for usernames.
    Ensures usernames only contain alphanumeric characters, dots, @, +, and hyphens.

    Attributes:
        regex (str): Regular expression pattern for valid username characters
        message (str): Error message displayed when validation fails
        flags (int): Regex compilation flags, defaults to 0 for no special flags
    """

    # Regular expression pattern for username validation
    regex = r"^[\w.@+-]+\Z"

    # Error message for invalid username format
    message = _(
        "Your username is not valid. A username can only contain letters, numbers, "
        "a dot, @ symbol, + symbol and a hyphen",
    )

    # Regex compilation flags
    flags: int = 0
