"""OpenAPI schema preprocessing hooks.

This module contains the preprocessing hooks for the OpenAPI schema.
"""

# Standard library imports
from typing import Any

# Third party imports
from rest_framework_simplejwt.authentication import JWTAuthentication


def preprocess_exclude_schema_endpoint(
    result: dict[str, Any],
    *,
    generator: Any,
    request: Any,
    public: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    """Postprocess hook to exclude the schema endpoint from the OpenAPI schema.

    Args:
        result: The OpenAPI schema dictionary
        generator: The schema generator instance
        request: The request object
        public: Whether the schema is public
        **kwargs: Additional arguments

    Returns:
        The modified OpenAPI schema dictionary
    """

    # Remove the schema endpoint from the OpenAPI schema
    if "paths" in result:
        result["paths"].pop("/api/v1/swagger/schema/", None)

    # Return the modified OpenAPI schema
    return result


def filter_authentication(request: Any, view: Any) -> list[Any]:
    """Filter authentication classes to only include JWT for swagger docs.

    This function filters out SessionAuthentication to prevent the
    sessionid cookie auth from appearing in the Swagger UI.

    Args:
        request: The request object
        view: The view being processed

    Returns:
        List of authentication classes to use in the schema
    """

    # Return only JWTAuthentication classes
    return [
        auth for auth in view.authentication_classes if isinstance(auth, type) and issubclass(auth, JWTAuthentication)
    ]
