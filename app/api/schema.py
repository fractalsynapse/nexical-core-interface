from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.openapi import AutoSchema as SpectacularAutoSchema


class AutoSchema(SpectacularAutoSchema):
    def _get_filter_parameters(self):
        if not (self._is_a_general_list_view() or self._is_list_view()):
            return []
        if getattr(self.view, "filter_backends", None) is None:
            return []

        parameters = []
        for filter_backend in self.view.filter_backends:
            filter_extension = OpenApiFilterExtension.get_match(filter_backend())
            if filter_extension:
                parameters += filter_extension.get_schema_operation_parameters(self)
            else:
                parameters += filter_backend().get_schema_operation_parameters(self.view)
        return parameters

    def _is_a_general_list_view(self):
        return hasattr(self.view, "detail") and self.method.lower() == "get" and not self.view.detail
