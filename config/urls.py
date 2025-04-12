"""URL Configuration for AgentSphere project.

This module contains the URL patterns for the AgentSphere project.
"""

# Third-party imports
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

# Third-party imports
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Admin and static URLs
urlpatterns = [
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# Static files for development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

# API documentation URLs
urlpatterns += [
    # OpenAPI schema
    path("api/v1/swagger/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    # Swagger UI
    path(
        "api/v1/swagger/ui/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="swagger-ui",
    ),
    # ReDoc UI
    path(
        "api/v1/swagger/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="redoc",
    ),
]

# API application URLs
urlpatterns += [
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/organizations/", include("apps.organization.urls")),
    path("api/v1/agents/", include("apps.agents.urls")),
    path("api/v1/tools/", include("apps.tools.urls")),
]

# Health check URLs
urlpatterns += [
    path("health/", include("health_check.urls")),
]

# Django silk URL
if settings.DEBUG:
    # Add django silk URL
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
