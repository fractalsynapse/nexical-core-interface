from django.urls import path

from . import ajax_views, views

app_name = "research"
urlpatterns = [
    # Project AJAX requests
    path("~timeline/<str:pk>/", ajax_views.TimelineListView.as_view(), name="timeline"),
    path("~summary/save/", ajax_views.SummarySaveView.as_view(), name="save_summary"),
    path("~summary/remove/<str:pk>/", ajax_views.SummaryRemoveView.as_view(), name="remove_summary"),
    path("~summary/<str:pk>/", ajax_views.SummaryView.as_view(), name="summary"),
    path("~note/save/", ajax_views.NoteSaveView.as_view(), name="save_note"),
    path("~note/remove/<str:pk>/", ajax_views.NoteRemoveView.as_view(), name="remove_note"),
    path("~note/<str:pk>/", ajax_views.NoteView.as_view(), name="note"),
    # Project research displays
    path("~modal/<str:pk>/", views.ModalPanelView.as_view(), name="panel_modal"),
    path("", views.PanelView.as_view(), name="panel"),
]
