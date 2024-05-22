from django import forms

from . import models


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.TeamProject
        fields = ["name", "summary_model", "summary_persona", "format_prompt"]
        widgets = {
            "summary_persona": forms.Textarea(attrs={"rows": 5}),
            "format_prompt": forms.Textarea(attrs={"rows": 5}),
        }
