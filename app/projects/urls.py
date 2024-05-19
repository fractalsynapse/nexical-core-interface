from django.urls import path

from . import views

app_name = "projects"
urlpatterns = [
    path("", view=views.ListView.as_view(), name="list"),
    path("create/", view=views.CreateFormView.as_view(), name="form_create"),
    path("<uuid:pk>/", view=views.UpdateFormView.as_view(), name="form_update"),
    path("remove/<uuid:pk>/", view=views.RemoveView.as_view(), name="remove"),
]
