from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django_select2 import forms as s2forms

from . import models


class AccessTeamWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ["name__icontains", "owner__email"]


class DocumentCollectionForm(forms.ModelForm):
    class Meta:
        model = models.TeamDocumentCollection
        fields = ["name", "description", "access_teams"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "access_teams": AccessTeamWidget,
        }

    def __init__(self, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["access_teams"].queryset = self.fields["access_teams"].queryset.exclude(id=team.id)


class DocumentCollectionFileForm(forms.ModelForm):
    class Meta:
        model = models.TeamDocument
        fields = ["file", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class BaseDocumentCollectionFileFormSet(BaseInlineFormSet):
    def full_clean(self):
        super().full_clean()

        for error in self._non_form_errors.as_data():
            if error.code == "too_many_forms":
                error.message = f"Only {self.max_num} files may be specified per document collection"


DocumentCollectionFileFormSet = inlineformset_factory(
    models.TeamDocumentCollection,
    models.TeamDocument,
    formset=BaseDocumentCollectionFileFormSet,
    form=DocumentCollectionFileForm,
    min_num=0,
    max_num=10,
    extra=0,
    can_delete=True,
    validate_max=True,
)


class DocumentCollectionBookmarkForm(forms.ModelForm):
    class Meta:
        model = models.TeamBookmark
        fields = ["url", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class BaseDocumentCollectionBookmarkFormSet(BaseInlineFormSet):
    def full_clean(self):
        super().full_clean()

        for error in self._non_form_errors.as_data():
            if error.code == "too_many_forms":
                error.message = f"Only {self.max_num} webpages may be specified per document collection"


DocumentCollectionBookmarkFormSet = inlineformset_factory(
    models.TeamDocumentCollection,
    models.TeamBookmark,
    formset=BaseDocumentCollectionBookmarkFormSet,
    form=DocumentCollectionBookmarkForm,
    min_num=0,
    max_num=10,
    extra=0,
    can_delete=True,
    validate_max=True,
)
