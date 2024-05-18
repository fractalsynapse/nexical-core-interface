import sys

from django_filters import rest_framework as filters

from app.utils import models as model_utils
from app.utils.python import create_class


class ModelFilter(filters.FilterSet):
    pass


def generate(_model, **fields):
    lookups = {
        "id": ["exact", "iexact", "istartswith", "in"],
        "token": ["exact", "iexact", "istartswith", "isnull", "in"],
        "short_text": ["exact", "iexact", "istartswith", "icontains", "iendswith", "iregex", "in"],
        "long_text": ["icontains", "iregex", "isnull"],
        "number": [
            "exact",
            "gt",
            "gte",
            "lt",
            "lte",
            "range",
            "in",
        ],
        "date": [
            "exact",
            "day",
            "gt",
            "gte",
            "lt",
            "lte",
            "month",
            "quarter",
            "week",
            "week_day",
            "year",
            "range",
            "in",
        ],
        "date_time": [
            "exact",
            "date",
            "day",
            "gt",
            "gte",
            "lt",
            "lte",
            "month",
            "quarter",
            "week",
            "week_day",
            "year",
            "hour",
            "minute",
            "second",
            "range",
            "in",
        ],
        "link": ["exact", "iexact", "istartswith", "icontains", "iendswith", "iregex", "in"],
    }
    for field, value in fields.items():
        if isinstance(value, str) and value in lookups:
            fields[field] = lookups[value]
        else:
            fields[field] = value

    return create_class(
        sys.modules[__name__],
        model_utils.get_class_name(_model, "Filter"),
        (ModelFilter,),
        {"Meta": type("Meta", (object,), {"model": _model, "fields": fields})},
    )
