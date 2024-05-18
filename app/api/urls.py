from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("docs/", view=views.DocumentationView.as_view(), name="docs"),
]
