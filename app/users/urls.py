from django.urls import path

from . import ajax_views, views

app_name = "users"
urlpatterns = [
    path("signup/", view=views.SignupFormView.as_view(), name="signup"),
    path("me/", view=views.DetailView.as_view(), name="me"),
    path("update/", view=views.UpdateFormView.as_view(), name="update"),
    path("token/", view=views.TokenFormView.as_view(), name="token"),
    path("token/embed", view=views.EmbeddedTokenFormView.as_view(), name="embed_token"),
    path("~token/generate", view=ajax_views.GenerateTokenView.as_view(), name="generate_token"),
    path("~token/revoke", view=ajax_views.RevokeTokenView.as_view(), name="revoke_token"),
    path("~redirect/", view=views.RedirectView.as_view(), name="redirect"),
    path("~settings/", view=ajax_views.SettingsView.as_view(), name="settings"),
    path("~settings/save", view=ajax_views.SaveSettingsView.as_view(), name="save_settings"),
]
