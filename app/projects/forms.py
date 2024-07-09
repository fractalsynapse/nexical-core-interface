from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_select2 import forms as s2forms

from . import models


class AccessTeamWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ["name__icontains", "owner__email"]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.TeamProject
        fields = ["name", "summary_model", "summary_persona", "format_prompt", "documents", "projects", "access_teams"]
        widgets = {
            "summary_persona": forms.Textarea(attrs={"rows": 5}),
            "format_prompt": forms.Textarea(attrs={"rows": 5}),
            "documents": forms.CheckboxSelectMultiple,
            "projects": forms.CheckboxSelectMultiple,
            "access_teams": AccessTeamWidget,
        }

    def __init__(self, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["documents"].queryset = (
            self.fields["documents"].queryset.filter(Q(access_teams__id=str(team.id)) | Q(team=team)).distinct()
        )
        self.fields["projects"].queryset = (
            self.fields["projects"].queryset.filter(access_teams__id=str(team.id)).distinct()
        )
        self.fields["access_teams"].queryset = self.fields["access_teams"].queryset.exclude(id=team.id)

    def clean_documents(self):
        queryset = self.cleaned_data["documents"]
        if len(queryset) > 10:
            raise ValidationError("Only 10 document collections may be selected per project")
        return queryset
