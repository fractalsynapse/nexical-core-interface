from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import ajax_views, mailgun_views, views

app_name = "outreach"
urlpatterns = [
    # Campaign Management
    path("", view=views.CampaignListView.as_view(), name="campaign_list"),
    path("create/", view=views.CampaignCreateFormView.as_view(), name="form_campaign_create"),
    path("<uuid:pk>/", view=views.CampaignUpdateFormView.as_view(), name="form_campaign_update"),
    path("remove/<uuid:pk>/", view=views.CampaignRemoveView.as_view(), name="campaign_remove"),
    path("contacts/", view=views.ContactGroupListView.as_view(), name="contact_group_list"),
    path("contacts/create/", view=views.ContactGroupCreateFormView.as_view(), name="form_contact_group_create"),
    path("contacts/<uuid:pk>/", view=views.ContactGroupUpdateFormView.as_view(), name="form_contact_group_update"),
    path("contacts/remove/<uuid:pk>/", view=views.ContactGroupRemoveView.as_view(), name="contact_group_remove"),
    # Outreach Message Management
    path("process/<uuid:pk>/", views.ProcessView.as_view(), name="campaign_process"),
    # Email Send Callback
    path("~send/<uuid:pk>/", ajax_views.SendView.as_view(), name="send"),
    path("~skip/<uuid:pk>/", ajax_views.SkipView.as_view(), name="skip"),
    path("~block/<uuid:pk>/", ajax_views.BlockView.as_view(), name="block"),
    # Mailgun Callback
    path("~mailgun/callback/", view=csrf_exempt(mailgun_views.MailgunWebhookView.as_view()), name="mailgun_callback"),
]
