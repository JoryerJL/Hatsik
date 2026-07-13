"""
Root URL configuration for Hatsik.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("internal/", include("apps.internal.urls")),
    path("events/", include("apps.events.urls")),
    path("", include("apps.accounts.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    from apps.internal.dev_views import component_gallery_view, htmx_test_view

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        path("dev/components/", component_gallery_view, name="dev_components"),
        path("dev/htmx-test/", htmx_test_view, name="dev_htmx_test"),
    ] + urlpatterns
