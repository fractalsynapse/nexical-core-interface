from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView


@method_decorator([never_cache], name="dispatch")
class HomeRedirectView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("research:panel")
        return redirect("users:signup")


class HomeView(TemplateView):
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("users:me")
        return super().dispatch(request, *args, **kwargs)


class StartView(LoginRequiredMixin, TemplateView):
    template_name = "getting_started.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def Site404(request, exception=None):
    return HttpResponseRedirect("/")
