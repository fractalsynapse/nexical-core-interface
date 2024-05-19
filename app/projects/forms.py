from django import forms

from . import models


class ProjectForm(forms.ModelForm):
    class Meta:
        model = models.TeamProject
        fields = ["name", "summary_prompt", "format_prompt"]
        widgets = {
            "summary_prompt": forms.Textarea(attrs={"rows": 5}),
            "format_prompt": forms.Textarea(attrs={"rows": 5}),
        }
