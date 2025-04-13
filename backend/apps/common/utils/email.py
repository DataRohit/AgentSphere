# Standard library imports
from typing import Any

# Third-party imports
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


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
