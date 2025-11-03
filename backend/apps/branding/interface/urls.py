from django.urls import path

from apps.branding.interface.views import (
    ActivateThemeView,
    ActiveThemeView,
    DeactivateThemeView,
    ThemeDetailView,
    ThemeListCreateView,
)

app_name = "branding"

urlpatterns = [
    # List all themes + Create new theme
    path("themes/", ThemeListCreateView.as_view(), name="theme-list-create"),
    # Get/Update/Delete specific theme
    path("themes/<uuid:theme_id>/", ThemeDetailView.as_view(), name="theme-detail"),
    # Get active theme
    path("themes/active/", ActiveThemeView.as_view(), name="theme-active"),
    # Activate a theme
    path("themes/<uuid:theme_id>/activate/", ActivateThemeView.as_view(), name="theme-activate"),
    # Deactivate a theme
    path("themes/<uuid:theme_id>/deactivate/", DeactivateThemeView.as_view(), name="theme-deactivate"),
]
