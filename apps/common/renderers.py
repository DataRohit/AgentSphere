# Standard library imports
import json
from typing import Any

# Third-party imports
from django.utils.translation import gettext_lazy as _
from rest_framework.renderers import JSONRenderer


# Custom JSON renderer for API responses
class GenericJSONRenderer(JSONRenderer):
    """Custom JSON renderer for standardizing API responses.

    This renderer extends DRF's JSONRenderer to provide a consistent response structure
    for all API endpoints. It wraps the response data in a standardized format
    with status code and object label.

    Attributes:
        charset (str): Character encoding for the rendered content.
        object_label (str): Default label for the object in the response.
    """

    # Character encoding for output
    charset = "utf-8"

    # Default object label for response
    object_label = "object"

    # Override render method to customize response format
    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict[str, Any] | None = None,
    ) -> bytes:
        """Render the data into JSON with standardized format.

        This method overrides the parent's render method to wrap the response data
        in a consistent format with status code and appropriate object labeling.

        Args:
            data (Any): The data to be rendered, typically from the serializer.
            accepted_media_type (str | None): The media type accepted by the request.
            renderer_context (dict | None): Context dictionary from the renderer.

        Returns:
            bytes: JSON encoded response with standardized structure.

        Raises:
            ValueError: If renderer context doesn't contain a response object.
        """

        # Default to empty dict if context is None
        if renderer_context is None:
            renderer_context = {}

        # Get view from renderer context
        view = renderer_context.get("view")

        # Get object label from view or use default
        object_label = getattr(view, "object_label", self.object_label)

        # Get response object from renderer context
        response = renderer_context.get("response")

        # Validate response object exists
        if not response:
            raise ValueError(_("Renderer context does not contain a response object"))

        # Get status code from response
        status_code = response.status_code

        # Check for errors in data
        errors = data.get("errors", None)

        # Return error response without wrapping if errors exist
        if errors is not None:
            return super().render(data)

        # Return standardized response format
        return json.dumps({"status_code": status_code, object_label: data}).encode(
            self.charset,
        )
