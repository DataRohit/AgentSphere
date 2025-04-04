"""OpenAPI schema preprocessing hooks.

This module contains the preprocessing hooks for the OpenAPI schema.
"""

# Standard library imports
from typing import Any


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
