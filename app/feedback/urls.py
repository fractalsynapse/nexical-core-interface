from django.urls import path

from . import ajax_views

app_name = "feedback"
urlpatterns = [
    path("~send/", view=ajax_views.SendView.as_view(), name="send"),
]
