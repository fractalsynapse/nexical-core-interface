from django.views.generic import FormView


class ParamFormView(FormView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(self.kwargs)
        return kwargs
