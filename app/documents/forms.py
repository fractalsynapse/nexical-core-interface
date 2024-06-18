from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from . import models


class DocumentCollectionForm(forms.ModelForm):
    class Meta:
        model = models.TeamDocumentCollection
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


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
