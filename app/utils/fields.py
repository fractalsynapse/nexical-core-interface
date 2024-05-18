import json

from django.db import models


class BaseJSONField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json.loads(super().from_db_value(value, expression, connection))

    def get_prep_value(self, value):
        if value is None:
            return value
        return super().get_prep_value(json.dumps(value))


class ListField(BaseJSONField):
    def __init__(self, *args, **kwargs):
        kwargs["default"] = list
        kwargs["null"] = False
        super().__init__(*args, **kwargs)


class DictionaryField(BaseJSONField):
    def __init__(self, *args, **kwargs):
        kwargs["default"] = dict
        kwargs["null"] = False
        super().__init__(*args, **kwargs)
