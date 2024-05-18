from drf_spectacular.views import SpectacularSwaggerView


class SwaggerView(SpectacularSwaggerView):
    template_name = "rest_framework/swagger_ui.html"
