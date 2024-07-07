from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, TemplateView, UpdateView
from rest_framework.authtoken.models import Token

from app.utils.auth import PublicOnlyAccessMixin, TeamAccessMixin
from app.utils.models import render_field_table
from app.utils.views import ParamFormView

from . import forms, models


class SignupFormView(PublicOnlyAccessMixin, ParamFormView):
    template_name = "user_signup.html"
    form_class = forms.SignupForm

    def form_valid(self, form):
        self.object = form.signup(self.request)
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("landing:start")


class DetailView(LoginRequiredMixin, DetailView):
    template_name = "user_detail.html"
    model = models.User

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["field_table"] = render_field_table(
            self.request.user,
            "email",
            "first_name",
            "last_name",
            "timezone",
            id="user-fields",
            classes="field-table",
        )
        return context


class UpdateFormView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "user_form.html"
    model = models.User
    fields = ["first_name", "last_name", "timezone"]
    success_message = _("Information successfully updated")

    def get_object(self):
        return self.request.user

    def get_success_url(self, **kwargs):
        return reverse("users:me")


class BaseTokenFormView(TeamAccessMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["token"] = Token.objects.get(user=self.request.user).key
        except Token.DoesNotExist:
            context["token"] = ""
        return context


class TokenFormView(BaseTokenFormView):
    template_name = "user_token.html"


class EmbeddedTokenFormView(BaseTokenFormView):
    template_name = "user_token_embed.html"


class RedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:me")
