import hashlib
import uuid


def create_class(module, name, parents=None, attributes=None):
    if parents is None:
        parents = []
    if attributes is None:
        attributes = {}

    klass = type(name, tuple(parents), attributes)
    klass.__module__ = module.__name__
    setattr(module, name, klass)
    return klass


def get_identifier(values):
    if isinstance(values, (list, tuple)):
        values = [str(item) for item in values]
    elif isinstance(values, dict):
        values = [f"{key}:{values[key]}" for key in sorted(values.keys())]
    else:
        values = [str(values)]
    return hashlib.sha256("-".join(sorted(values)).encode()).hexdigest()


def get_uuid(values):
    if isinstance(values, (list, tuple)):
        values = [str(item) for item in values]
    elif isinstance(values, dict):
        values = [f"{key}:{values[key]}" for key in sorted(values.keys())]
    else:
        values = [str(values)]

    hex_string = hashlib.md5("-".join(sorted(values)).encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))


def ensure_list(data, preserve_null=False):
    if preserve_null and data is None:
        return None
    return list(data) if isinstance(data, (list, tuple)) else [data]


def chunk_list(data, chunk_size=10):
    data = list(data)
    return [data[index : index + chunk_size] for index in range(0, len(data), chunk_size)]
