from datetime import datetime


def _get_value(request, key):
    value = None
    try:
        if request.POST.get(key) is not None:
            value = request.POST.get(key)
    except (ValueError, AttributeError, TypeError):
        pass
    return value


def get_integer(request, key):
    value = _get_value(request, key)
    return int(value) if value is not None else None


def get_number(request, key):
    value = _get_value(request, key)
    return float(value) if value is not None else None


def get_text(request, key):
    value = _get_value(request, key)
    return str(value) if value is not None else None


def get_boolean(request, key):
    value = _get_value(request, key)
    return bool(value) if value is not None else None


def get_date(request, key):
    value = _get_value(request, key)
    if value:
        value = datetime.strptime(value, "%Y-%m-%d").date()
    return value if value else None


def get_datetime(request, key):
    value = _get_value(request, key)
    if value:
        value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    return value if value else None
