import importlib
import logging
import sys

from django.conf import settings
from django.core.management import call_command
from django.db.models.query import prefetch_related_objects
from django.http import JsonResponse

# from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView
from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from app.teams.models import TeamMembership
from app.utils import models as model_utils
from app.utils.python import create_class

from . import filters, serializers

logger = logging.getLogger(__name__)


def get_team_queryset(view, field="team"):
    if view.request.user.check_member("engine"):
        return view.queryset

    team_ids = list(TeamMembership.objects.filter(user__id=view.request.user.id).values_list("team__id", flat=True))
    return view.queryset.filter(**{f"{field}__id__in": team_ids}).distinct()


class Status(View):
    def get(self, request, *args, **kwargs):
        try:
            call_command("check")
            return JsonResponse({"message": "System check successful"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("API status error <{}>: {}".format(request.user.name if request.user else "anonymous", e))
            return JsonResponse(data={"detail": "System check error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentationView(TemplateView):
    template_name = "api_docs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["help_title"] = "API Help"
        # context["help_body"] = render_to_string("api_help.html")
        return context


#
# * Create
# * Retrieve
# * Update
# * Destroy
# * List
#
class ModelViewSet(viewsets.ModelViewSet):
    #
    # '^' Starts-with search
    # '=' Exact matches
    # '@' Full-text search
    # '$' Regex search
    #
    search_fields = []
    #
    # '-' Descending order
    #
    ordering_fields = []
    ordering = []

    action_serializers = {}

    def get_serializer_class(self):
        try:
            return self.action_serializers[self.action]
        except (KeyError, AttributeError):
            return self.action_serializers["default"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if self.lookup_field in request.data:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset.filter(**{self.lookup_field: request.data[self.lookup_field]}).exists():
                self.kwargs[self.lookup_field] = request.data[self.lookup_field]
                return self.update(request, partial=True)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        queryset = self.filter_queryset(self.get_queryset())
        if queryset._prefetch_related_lookups:
            instance._prefetched_objects_cache = {}
            prefetch_related_objects([instance], *queryset._prefetch_related_lookups)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


def generate(
    model,
    filter_fields=None,
    search_fields=None,
    ordering_fields=None,
    serializer_prefix="",
    relation_prefix="",
    reverse_prefix="",
    fields=None,
    view_fields=None,
    list_fields=None,
    object_fields=None,
    save_fields=None,
    create_fields=None,
    update_fields=None,
    relation_fields=None,
    view_relation_fields=None,
    list_relation_fields=None,
    object_relation_fields=None,
    save_relation_fields=None,
    create_relation_fields=None,
    update_relation_fields=None,
    reverse_fields=None,
    view_reverse_fields=None,
    list_reverse_fields=None,
    object_reverse_fields=None,
    save_reverse_fields=None,
    create_reverse_fields=None,
    update_reverse_fields=None,
    method_fields=None,
    view_method_fields=None,
    list_method_fields=None,
    object_method_fields=None,
    extra_fields=None,
    view_extra_fields=None,
    list_extra_fields=None,
    object_extra_fields=None,
    save_extra_fields=None,
    create_extra_fields=None,
    update_extra_fields=None,
    validator=None,
    create_validator=None,
    update_validator=None,
    handler=None,
    create_handler=None,
    update_handler=None,
    extra_serializers=None,
    **attributes,
):
    if filter_fields is None:
        filter_fields = {}
    if search_fields is None:
        search_fields = []
    if ordering_fields is None:
        ordering_fields = []

    if model._meta.pk.name.endswith("_ptr") and model._meta.parents:
        pk_name = list(model._meta.parents.keys())[0]._meta.pk.name
    else:
        pk_name = model._meta.pk.name

    return create_class(
        sys.modules[__name__],
        model_utils.get_class_name(model, "ViewSet"),
        (ModelViewSet,),
        {
            "permission_classes": [IsAdminUser],
            "filterset_class": filters.generate(model, **filter_fields),
            "action_serializers": serializers.generate(
                model,
                class_prefix=serializer_prefix,
                relation_prefix=relation_prefix,
                reverse_prefix=reverse_prefix,
                fields=fields,
                view_fields=view_fields,
                list_fields=list_fields,
                object_fields=object_fields,
                save_fields=save_fields,
                create_fields=create_fields,
                update_fields=update_fields,
                relation_fields=relation_fields,
                view_relation_fields=view_relation_fields,
                list_relation_fields=list_relation_fields,
                object_relation_fields=object_relation_fields,
                save_relation_fields=save_relation_fields,
                create_relation_fields=create_relation_fields,
                update_relation_fields=update_relation_fields,
                reverse_fields=reverse_fields,
                view_reverse_fields=view_reverse_fields,
                list_reverse_fields=list_reverse_fields,
                object_reverse_fields=object_reverse_fields,
                save_reverse_fields=save_reverse_fields,
                create_reverse_fields=create_reverse_fields,
                update_reverse_fields=update_reverse_fields,
                method_fields=method_fields,
                view_method_fields=view_method_fields,
                list_method_fields=list_method_fields,
                object_method_fields=object_method_fields,
                extra_fields=extra_fields,
                view_extra_fields=view_extra_fields,
                list_extra_fields=list_extra_fields,
                object_extra_fields=object_extra_fields,
                save_extra_fields=save_extra_fields,
                create_extra_fields=create_extra_fields,
                update_extra_fields=update_extra_fields,
                validator=validator,
                create_validator=create_validator,
                update_validator=update_validator,
                handler=handler,
                create_handler=create_handler,
                update_handler=update_handler,
                extra=extra_serializers,
            ),
            "queryset": model.objects.all(),
            "lookup_field": pk_name,
            "search_fields": search_fields,
            "ordering_fields": ordering_fields,
            "ordering": [pk_name],
            **attributes,
        },
    )


for base_module_path in settings.LOCAL_APPS:
    try:
        importlib.import_module(f"{base_module_path}.api")
    except ModuleNotFoundError:
        pass
