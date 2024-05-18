from django.utils.encoding import force_str
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.metadata import SimpleMetadata


class Metadata(SimpleMetadata):
    def get_serializer_info(self, serializer, depth=3):
        if hasattr(serializer, "child"):
            serializer = serializer.child
        return {
            field_name: self.get_field_info(field, depth)
            for field_name, field in serializer.fields.items()
            if not isinstance(field, serializers.HiddenField)
        }

    def get_field_info(self, field, depth):
        field_info = {
            "type": self.label_lookup[field],
            "required": getattr(field, "required", False),
        }

        attrs = [
            "read_only",
            "label",
            "help_text",
            "min_length",
            "max_length",
            "min_value",
            "max_value",
            "max_digits",
            "decimal_places",
        ]

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != "":
                field_info[attr] = force_str(value, strings_only=True)

        if depth:
            if getattr(field, "child", None):
                field_info["child"] = self.get_field_info(field.child, (depth - 1))
            elif getattr(field, "fields", None):
                field_info["children"] = self.get_serializer_info(field, (depth - 1))

        if (
            not field_info.get("read_only")
            and not isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField))
            and hasattr(field, "choices")
        ):
            field_info["choices"] = [
                {"value": choice_value, "display_name": force_str(choice_name, strings_only=True)}
                for choice_value, choice_name in field.choices.items()
            ]

        if getattr(field, "default", None) and field.default != empty and not callable(field.default):
            field_info["default"] = field.default

        return field_info
