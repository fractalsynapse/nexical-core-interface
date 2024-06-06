import private_storage.urls
from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView
from rest_framework.routers import DefaultRouter, SimpleRouter

from app.api import views
from app.api.swagger import SwaggerView

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("event", views.EventViewSet)
router.register("user", views.UserViewSet)
router.register("team", views.TeamViewSet)
router.register("project", views.TeamProjectViewSet)
router.register("library", views.TeamDocumentCollectionViewSet)
router.register("document", views.TeamDocumentViewSet)
router.register("summary", views.ProjectSummaryViewSet)
router.register("note", views.ProjectNoteViewSet)
router.register("feedback", views.FeedbackViewSet)
# router.register("message", views.MessageViewSet)


# API URLS
app_name = "api"
urlpatterns = [
    path("status/", views.Status.as_view(), name="status"),
    path("", SwaggerView.as_view(url_name="api-schema"), name="api-docs"),
    path("schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("accounts/", include("allauth.urls")),
    path("users/", include("app.users.urls", namespace="users")),
    path("landing/", include("app.landing.urls", namespace="landing")),
    path("feedback/", include("app.feedback.urls", namespace="feedback")),
    path("private-media/", include(private_storage.urls)),
] + router.urls
