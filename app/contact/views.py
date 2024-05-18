from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from app.utils.views import ParamFormView

from . import forms


class ContactFormView(SuccessMessageMixin, ParamFormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_message = _("Thanks for contacting us!  We'll get back with you shortly.")

    def form_valid(self, form):
        form.set_user(self.request.user)
        self.object = form.save()
        self.object.send(self.request)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("home")
