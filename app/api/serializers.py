import sys

from drf_writable_nested.mixins import UniqueFieldsMixin
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from app.utils import models as model_utils
from app.utils.python import create_class


def validate_team_membership(serializer, validated_data, field="team", team=None):
    user = serializer.context["request"].user

    if not team:
        if field in validated_data:
            team = validated_data[field]
        elif serializer.instance:
            team = serializer.instance
            for inner_field in field.split("__"):
                team = getattr(team, inner_field)
        else:
            raise serializers.ValidationError("Team required")

    if not user.check_member("engine") and not user.membership.filter(team=team).exists():
        raise serializers.ValidationError("Team membership required")

    return validated_data


class ViewSerializer(serializers.Serializer):
    pass


class BaseModelViewSerializer(serializers.ModelSerializer):
    pass


class ObjectSerializer(BaseModelViewSerializer):
    pass


class ListSerializer(BaseModelViewSerializer):
    @classmethod
    def get_meta_fields(cls, field_list):
        return field_list

    @classmethod
    def get_meta_kwargs(cls, model):
        return {"url": {"view_name": f"{model._meta.model_name}-detail", "lookup_field": model._meta.pk.name}}


class CreateSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    pass


class UpdateSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    pass


def generate(
    model,
    class_prefix="",
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
    extra=None,
    **attributes,
):
    action_serializers = {}

    if fields is None:
        fields = []
    if view_fields is None:
        view_fields = []
    if list_fields is None:
        list_fields = []
    if object_fields is None:
        object_fields = []
    if save_fields is None:
        save_fields = []
    if create_fields is None:
        create_fields = []
    if update_fields is None:
        update_fields = []

    if relation_fields is None:
        relation_fields = []
    if view_relation_fields is None:
        view_relation_fields = []
    if list_relation_fields is None:
        list_relation_fields = []
    if object_relation_fields is None:
        object_relation_fields = []
    if save_relation_fields is None:
        save_relation_fields = []
    if create_relation_fields is None:
        create_relation_fields = []
    if update_relation_fields is None:
        update_relation_fields = []

    if reverse_fields is None:
        reverse_fields = []
    if view_reverse_fields is None:
        view_reverse_fields = []
    if list_reverse_fields is None:
        list_reverse_fields = []
    if object_reverse_fields is None:
        object_reverse_fields = []
    if save_reverse_fields is None:
        save_reverse_fields = []
    if create_reverse_fields is None:
        create_reverse_fields = []
    if update_reverse_fields is None:
        update_reverse_fields = []

    if method_fields is None:
        method_fields = {}
    if view_method_fields is None:
        view_method_fields = {}
    if list_method_fields is None:
        list_method_fields = {}
    if object_method_fields is None:
        object_method_fields = {}

    if extra_fields is None:
        extra_fields = {}
    if view_extra_fields is None:
        view_extra_fields = {}
    if list_extra_fields is None:
        list_extra_fields = {}
    if object_extra_fields is None:
        object_extra_fields = {}
    if save_extra_fields is None:
        save_extra_fields = {}
    if create_extra_fields is None:
        create_extra_fields = {}
    if update_extra_fields is None:
        update_extra_fields = {}

    if extra is None:
        extra = {}

    object_fields = fields + view_fields + object_fields
    if object_fields:
        retrieve_class = ObjectSerializerGenerator(model).generate(
            class_prefix=class_prefix,
            fields=object_fields,
            relation_prefix=relation_prefix,
            relation_fields=(relation_fields + view_relation_fields + object_relation_fields),
            reverse_prefix=reverse_prefix,
            reverse_fields=(reverse_fields + view_reverse_fields + object_reverse_fields),
            method_field_map={**method_fields, **view_method_fields, **object_method_fields},
            extra_field_map={**extra_fields, **view_extra_fields, **object_extra_fields},
            **attributes,
        )
        action_serializers["default"] = retrieve_class
        action_serializers["retrieve"] = retrieve_class

    list_fields = fields + view_fields + list_fields
    if list_fields:
        list_class = ListSerializerGenerator(model).generate(
            class_prefix=class_prefix,
            fields=list_fields,
            relation_prefix=relation_prefix,
            relation_fields=(relation_fields + view_relation_fields + list_relation_fields),
            reverse_prefix=reverse_prefix,
            reverse_fields=(reverse_fields + view_reverse_fields + list_reverse_fields),
            method_field_map={**method_fields, **view_method_fields, **list_method_fields},
            extra_field_map={**extra_fields, **view_extra_fields, **list_extra_fields},
            **attributes,
        )
        action_serializers["list"] = list_class

    create_fields = fields + save_fields + create_fields
    if create_fields:
        create_class = CreateSerializerGenerator(model).generate(
            class_prefix=class_prefix,
            fields=create_fields,
            relation_prefix=relation_prefix,
            relation_fields=(relation_fields + save_relation_fields + create_relation_fields),
            reverse_prefix=reverse_prefix,
            reverse_fields=(reverse_fields + save_reverse_fields + create_reverse_fields),
            extra_field_map={**extra_fields, **save_extra_fields, **create_extra_fields},
            validator=(create_validator or validator),
            handler=(create_handler or handler),
            **attributes,
        )
        action_serializers["create"] = create_class

    update_fields = fields + save_fields + update_fields
    if update_fields:
        update_class = UpdateSerializerGenerator(model).generate(
            class_prefix=class_prefix,
            fields=update_fields,
            relation_prefix=relation_prefix,
            relation_fields=(relation_fields + save_relation_fields + update_relation_fields),
            reverse_prefix=reverse_prefix,
            reverse_fields=(reverse_fields + save_reverse_fields + update_reverse_fields),
            extra_field_map={**extra_fields, **save_extra_fields, **update_extra_fields},
            validator=(update_validator or validator),
            handler=(update_handler or handler),
            **attributes,
        )
        action_serializers["update"] = update_class
        action_serializers["partial_update"] = update_class
        action_serializers["destroy"] = update_class

    for method, klass in extra.items():
        if isinstance(klass, str) and klass in action_serializers:
            action_serializers[method] = action_serializers[klass]
        else:
            action_serializers[method] = klass
    return action_serializers


class BaseSerializerGenerator:
    def __init__(self, model):
        self.model = model
        self.module = sys.modules[__name__]
        self.relations = model_utils.get_relations(self.model)
        self.reverse_relations = model_utils.get_reverse_relations(self.model)

    def _get_method_fields(self, method_field_map):
        field_names = []
        field_methods = {}

        for field, method in method_field_map.items():
            field_names.append(field)
            field_methods[method.__name__] = method
            field_methods[field] = serializers.SerializerMethodField(method.__name__)

        return field_names, field_methods

    def _get_extra_fields(self, extra_field_map):
        field_names = []
        field_methods = {}

        for field, serializer_method in extra_field_map.items():
            field_names.append(field)
            field_methods[field] = serializer_method(self.model, field)

        return field_names, field_methods

    def _add_relations(self, klass, class_name, relation_fields, prefix=None):
        for field_info in self.relations:
            field = field_info["field"]
            if relation_fields and field.name in relation_fields:
                for relation_prefix in [prefix, ""] if prefix else [""]:
                    serializer = getattr(
                        self.module,
                        model_utils.get_class_name(field.related_model, f"{relation_prefix}{class_name}"),
                        None,
                    )
                    if serializer:
                        klass._declared_fields[field.name] = serializer(many=field_info["multiple"])
                        break

    def _add_reverse_relations(self, klass, class_name, reverse_fields, prefix=None):
        for field_info in self.reverse_relations:
            field = field_info["field"]
            if reverse_fields and field.name in reverse_fields:
                for relation_prefix in [prefix, ""] if prefix else [""]:
                    serializer = getattr(
                        self.module,
                        model_utils.get_class_name(field.related_model, f"{relation_prefix}{class_name}"),
                        None,
                    )
                    if serializer:
                        klass._declared_fields[field.name] = serializer(many=True)
                        break

    def generate(self):
        raise NotImplementedError("Method generate() must be defined in all subclasses")


def generate_list(model, **kwargs):
    return ListSerializerGenerator(model).generate(**kwargs)


class ListSerializerGenerator(BaseSerializerGenerator):
    def generate(
        self,
        class_prefix="",
        fields=None,
        relation_prefix="",
        relation_fields=None,
        reverse_prefix="",
        reverse_fields=None,
        method_field_map=None,
        extra_field_map=None,
        **attributes,
    ):
        if not fields:
            fields = []
        if not relation_fields:
            relation_fields = []
        if not reverse_fields:
            reverse_fields = []
        if not method_field_map:
            method_field_map = {}
        if not extra_field_map:
            extra_field_map = {}

        method_names, method_attrs = self._get_method_fields(method_field_map)
        extra_names, extra_attrs = self._get_extra_fields(extra_field_map)

        field_names = []
        extra_kwargs = {}

        for field in fields:
            if isinstance(field, (list, tuple)):
                field_names.append(field[0])
                extra_kwargs[field[0]] = field[1]
            else:
                field_names.append(field)

        klass = create_class(
            self.module,
            model_utils.get_class_name(self.model, f"{class_prefix}ListSerializer"),
            (ListSerializer,),
            {
                "Meta": type(
                    "Meta",
                    (object,),
                    {
                        "model": self.model,
                        "fields": (field_names + relation_fields + reverse_fields + method_names + extra_names),
                        "extra_kwargs": extra_kwargs,
                    },
                ),
                **method_attrs,
                **extra_attrs,
                **attributes,
            },
        )
        self._add_relations(klass, "ListSerializer", relation_fields, prefix=relation_prefix)
        self._add_reverse_relations(klass, "ListSerializer", reverse_fields, prefix=reverse_prefix)
        return klass


def generate_object(model, **kwargs):
    return ObjectSerializerGenerator(model).generate(**kwargs)


class ObjectSerializerGenerator(BaseSerializerGenerator):
    def generate(
        self,
        class_prefix="",
        fields=None,
        relation_prefix="",
        relation_fields=None,
        reverse_prefix="",
        reverse_fields=None,
        method_field_map=None,
        extra_field_map=None,
        **attributes,
    ):
        if not fields:
            fields = []
        if not relation_fields:
            relation_fields = []
        if not reverse_fields:
            reverse_fields = []
        if not method_field_map:
            method_field_map = {}
        if not extra_field_map:
            extra_field_map = {}

        method_names, method_attrs = self._get_method_fields(method_field_map)
        extra_names, extra_attrs = self._get_extra_fields(extra_field_map)

        field_names = []
        extra_kwargs = {}

        for field in fields:
            if isinstance(field, (list, tuple)):
                field_names.append(field[0])
                extra_kwargs[field[0]] = field[1]
            else:
                field_names.append(field)

        klass = create_class(
            self.module,
            model_utils.get_class_name(self.model, f"{class_prefix}ObjectSerializer"),
            (ObjectSerializer,),
            {
                "Meta": type(
                    "Meta",
                    (object,),
                    {
                        "model": self.model,
                        "fields": (field_names + relation_fields + reverse_fields + method_names + extra_names),
                        "extra_kwargs": extra_kwargs,
                    },
                ),
                **method_attrs,
                **extra_attrs,
                **attributes,
            },
        )
        self._add_relations(klass, "ListSerializer", relation_fields, prefix=relation_prefix)
        self._add_reverse_relations(klass, "ListSerializer", reverse_fields, prefix=reverse_prefix)
        return klass


class BaseUpdateSerializerGenerator(BaseSerializerGenerator):
    def _add_update_methods(self, klass, validator, handler):
        def validate(self, attrs):
            validated_data = super(klass, self).validate(attrs)
            if validator and callable(validator):
                return validator(self, validated_data)
            return validated_data

        def create(self, validated_data):
            instance = super(klass, self).create(validated_data)
            if handler and callable(handler):
                handler(self, instance)
            return instance

        def update(self, instance, validated_data):
            instance = super(klass, self).update(instance, validated_data)
            if handler and callable(handler):
                handler(self, instance)
            return instance

        klass.validate = validate
        klass.create = create
        klass.update = update


def generate_create(model, **kwargs):
    return CreateSerializerGenerator(model).generate(**kwargs)


class CreateSerializerGenerator(BaseUpdateSerializerGenerator):
    def generate(
        self,
        class_prefix="",
        fields=None,
        relation_prefix="",
        relation_fields=None,
        reverse_prefix="",
        reverse_fields=None,
        extra_field_map=None,
        validator=None,
        handler=None,
        **attributes,
    ):
        if not fields:
            fields = []
        if not relation_fields:
            relation_fields = []
        if not reverse_fields:
            reverse_fields = []
        if not extra_field_map:
            extra_field_map = {}

        extra_names, extra_attrs = self._get_extra_fields(extra_field_map)

        field_names = []
        extra_kwargs = {}

        for field in fields:
            if isinstance(field, (list, tuple)):
                field_names.append(field[0])
                extra_kwargs[field[0]] = field[1]
            else:
                field_names.append(field)

        klass = create_class(
            self.module,
            model_utils.get_class_name(self.model, f"{class_prefix}CreateSerializer"),
            (CreateSerializer,),
            {
                "Meta": type(
                    "Meta",
                    (object,),
                    {
                        "model": self.model,
                        "fields": (field_names + relation_fields + reverse_fields + extra_names),
                        "extra_kwargs": extra_kwargs,
                    },
                ),
                **extra_attrs,
                **attributes,
            },
        )
        self._add_update_methods(klass, validator, handler)
        self._add_relations(klass, "CreateSerializer", relation_fields, prefix=relation_prefix)
        self._add_reverse_relations(klass, "CreateSerializer", reverse_fields, prefix=reverse_prefix)
        return klass


def generate_update(model, **kwargs):
    return UpdateSerializerGenerator(model).generate(**kwargs)


class UpdateSerializerGenerator(BaseUpdateSerializerGenerator):
    def generate(
        self,
        class_prefix="",
        fields=None,
        relation_prefix="",
        relation_fields=None,
        reverse_prefix="",
        reverse_fields=None,
        extra_field_map=None,
        validator=None,
        handler=None,
        **attributes,
    ):
        if not fields:
            fields = []
        if not relation_fields:
            relation_fields = []
        if not reverse_fields:
            reverse_fields = []
        if not extra_field_map:
            extra_field_map = {}

        extra_names, extra_attrs = self._get_extra_fields(extra_field_map)

        field_names = []
        extra_kwargs = {}

        for field in fields:
            if isinstance(field, (list, tuple)):
                field_names.append(field[0])
                extra_kwargs[field[0]] = field[1]
            else:
                field_names.append(field)

        klass = create_class(
            self.module,
            model_utils.get_class_name(self.model, f"{class_prefix}UpdateSerializer"),
            (UpdateSerializer,),
            {
                "Meta": type(
                    "Meta",
                    (object,),
                    {
                        "model": self.model,
                        "fields": (field_names + relation_fields + reverse_fields + extra_names),
                        "extra_kwargs": extra_kwargs,
                    },
                ),
                **extra_attrs,
                **attributes,
            },
        )
        self._add_update_methods(klass, validator, handler)
        self._add_relations(klass, "CreateSerializer", relation_fields, prefix=relation_prefix)
        self._add_reverse_relations(klass, "CreateSerializer", reverse_fields, prefix=reverse_prefix)
        return klass
