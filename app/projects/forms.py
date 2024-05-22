from django import forms
from django.core.exceptions import ValidationError

from . import models


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.TeamProject
        fields = ["name", "summary_model", "summary_persona", "format_prompt", "documents"]
        widgets = {
            "summary_persona": forms.Textarea(attrs={"rows": 5}),
            "format_prompt": forms.Textarea(attrs={"rows": 5}),
            "documents": forms.CheckboxSelectMultiple,
        }

    def __init__(self, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["documents"].queryset = self.fields["documents"].queryset.filter(team=team)

    def clean_documents(self):
        queryset = self.cleaned_data["documents"]
        if len(queryset) > 10:
            raise ValidationError("Only 10 document collections may be selected per project")
        return queryset
