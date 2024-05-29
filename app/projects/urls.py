from django.urls import path

from . import ajax_views, views

app_name = "projects"
urlpatterns = [
    path("", view=views.ListView.as_view(), name="list"),
    path("create/", view=views.CreateFormView.as_view(), name="form_create"),
    path("~modal/create/", views.ModalCreateFormView.as_view(), name="modal_form_create"),
    path("<uuid:pk>/", view=views.UpdateFormView.as_view(), name="form_update"),
    path("~modal/<uuid:pk>/", views.ModalUpdateFormView.as_view(), name="modal_form_update"),
    path("remove/<uuid:pk>/", view=views.RemoveView.as_view(), name="remove"),
    path("~set/<uuid:pk>/", view=ajax_views.SetActiveView.as_view(), name="set_active_project"),
]
