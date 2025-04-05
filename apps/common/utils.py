# Third-party imports
# Standard library imports
import logging
from typing import Any

from django.conf import settings
from django.contrib.sites.models import Site

# Third-party imports
from django.core.mail import send_mail
from django.http import HttpRequest
from django.template.loader import render_to_string

# Setup logger
logger = logging.getLogger(__name__)


# Get the activation base URL
def get_activation_base_url(request: HttpRequest) -> tuple[str, str]:
    """Determines the scheme and domain part for activation links.

    Uses HTTPS with the current site's domain if the request is secure
    or behind a trusted proxy. Otherwise, defaults to HTTP with localhost:8080
    for development environments.

    Args:
        request: The HttpRequest object.

    Returns:
        A tuple containing the scheme ('http' or 'https') and the domain part
        (e.g., 'example.com' or 'localhost:8080').
    """

    # Default to HTTP
    scheme = "http"

    # Default to localhost:8080 for HTTP
    domain_part = "localhost:8080"

    # Check if proxy header is configured and indicates HTTPS
    if settings.SECURE_PROXY_SSL_HEADER:
        # Get the header and value
        header, value = settings.SECURE_PROXY_SSL_HEADER

        # Check if the header is set to the value
        if request.META.get(header, "").lower() == value.lower():
            # Set the scheme to HTTPS
            scheme = "https"

    # Check if direct HTTPS is used
    elif request.is_secure():
        # Set the scheme to HTTPS
        scheme = "https"

    # Get the current site domain if scheme is HTTPS
    if scheme == "https":
        # Get the current site
        current_site = Site.objects.get_current(request)

        # Set the domain part to the current site domain
        domain_part = current_site.domain

    # Return the scheme and domain part
    return scheme, domain_part


# Send templated email
def send_templated_mail(
    template_name: str,
    subject: str,
    context: dict[str, Any],
    recipient_list: list[str],
    from_email: str | None = None,
) -> None:
    """Renders an HTML template and sends it as an email.

    Args:
        template_name: The path to the email template.
        subject: The email subject.
        context: The context dictionary for rendering the template.
        recipient_list: A list of email addresses to send to.
        from_email: The sender's email address. Defaults to settings.DEFAULT_FROM_EMAIL.
    """

    # Set default from_email if not provided
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    # Render HTML email content
    html_message = render_to_string(template_name, context)

    # Send the email
    send_mail(
        subject,
        "",
        from_email,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )
