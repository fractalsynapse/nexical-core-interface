import private_storage.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from app.api import views as api_views
from app.contact.views import ContactFormView
from app.landing.views import HomeRedirectView

admin.site.site_title = "Nexical Core"
admin.site.site_header = "Nexical Core Administration"
admin.site.index_title = "Administration"


urlpatterns = [
    path("status/", api_views.Status.as_view(), name="status"),
    path("", HomeRedirectView.as_view(), name="home"),
    path("contact/", ContactFormView.as_view(), name="contact"),
    path("privacy/", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),
    path("tos/", TemplateView.as_view(template_name="pages/tos.html"), name="tos"),
    path("api/", include("app.api.urls", namespace="api")),
    path("accounts/", include("allauth.urls")),
    path("landing/", include("app.landing.urls", namespace="landing")),
    path("users/", include("app.users.urls", namespace="users")),
    path("teams/", include("app.teams.urls", namespace="teams")),
    path("projects/", include("app.projects.urls", namespace="projects")),
    path("documents/", include("app.documents.urls", namespace="documents")),
    path("research/", include("app.research.urls", namespace="research")),
    path("feedback/", include("app.feedback.urls", namespace="feedback")),
    path("private-media/", include(private_storage.urls)),
    path(settings.ADMIN_PATH, admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
