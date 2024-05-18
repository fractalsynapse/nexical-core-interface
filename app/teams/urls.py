from django.urls import path

from . import ajax_views, views

app_name = "teams"
urlpatterns = [
    path("", view=views.ListView.as_view(), name="list"),
    path("create/", view=views.CreateFormView.as_view(), name="form_create"),
    path("update/<uuid:pk>/", view=views.UpdateFormView.as_view(), name="form_update"),
    path("remove/<uuid:pk>/", view=views.RemoveView.as_view(), name="remove"),
    path("<uuid:pk>/", view=views.MemberListView.as_view(), name="members"),
    path("members/remove/<uuid:pk>/", view=views.MemberRemoveView.as_view(), name="member_remove"),
    path("invites/remove/<uuid:pk>/", view=views.InviteRemoveView.as_view(), name="invite_remove"),
    path("invites/confirm/<uuid:pk>/", view=views.InviteConfirmView.as_view(), name="invite_confirm"),
    path("~invites/send/<uuid:team>/", view=ajax_views.InviteSendView.as_view(), name="invite_send"),
    path("~set/<uuid:pk>/", view=ajax_views.SetActiveView.as_view(), name="set_active_team"),
]
