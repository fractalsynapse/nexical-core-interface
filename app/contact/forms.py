from django import forms

from . import models


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.ContactMessage
        fields = ["name", "email", "subject", "message"]

    def set_user(self, user):
        if user.is_authenticated:
            self.user = user
        else:
            self.user = None

    def save(self, commit=True):
        self.instance.user = self.user
        super().save(commit=commit)
        return self.instance
