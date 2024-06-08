from django import forms
from django.forms.models import inlineformset_factory

from . import models


class ContactGroupForm(forms.ModelForm):
    class Meta:
        model = models.ContactGroup
        fields = [
            "name",
            "description",
            "csv_file",
            "organization_name_column",
            "organization_link_column",
            "organization_employees_column",
            "organization_industry_column",
            "organization_keywords_column",
            "organization_linkedin_column",
            "organization_description_column",
            "organization_technologies_column",
            "organization_revenue_column",
            "organization_total_funding_column",
            "organization_last_funding_stage_column",
            "organization_last_funding_column",
            "organization_last_raised_at_column",
            "contact_first_name_column",
            "contact_last_name_column",
            "contact_title_column",
            "contact_departments_column",
            "contact_seniority_column",
            "contact_email_column",
            "contact_phone_column",
            "contact_city_column",
            "contact_province_column",
            "contact_country_column",
            "contact_linkedin_column",
        ]


class CampaignForm(forms.ModelForm):
    class Meta:
        model = models.Campaign
        fields = ["name", "description", "contact_groups"]
        widgets = {
            "contact_groups": forms.CheckboxSelectMultiple,
        }

    def set_owner(self, user):
        if not self.instance.owner:
            self.instance.owner = user


class CampaignEmailForm(forms.ModelForm):
    class Meta:
        model = models.CampaignEmail
        exclude = ()


CampaignEmailFormSet = inlineformset_factory(
    models.Campaign,
    models.CampaignEmail,
    form=CampaignEmailForm,
    fields=["subject_template", "body_template", "wait_days"],
    min_num=1,
    extra=0,
    can_delete=True,
)


class MessageForm(forms.ModelForm):
    class Meta:
        model = models.Message
        fields = ["sequence"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def process(self, request):
        pass
