import uuid
from functools import lru_cache

from django.db import models
from django.template.loader import render_to_string
from django.utils.timezone import now


def get_class_name(model, suffix):
    return f"{model._meta.object_name}{suffix}"


@lru_cache(maxsize=None)
def get_fields(model):
    return model._meta.get_fields()


@lru_cache(maxsize=None)
def get_direct_fields(model):
    fields = []
    for field in get_fields(model):
        if isinstance(field, models.Field):
            fields.append(field)
    return fields


@lru_cache(maxsize=None)
def get_scalars(model):
    fields = []
    for field in get_fields(model):
        if not isinstance(
            field,
            (
                models.ForeignKey,
                models.OneToOneField,
                models.ManyToManyField,
                models.OneToOneRel,
                models.ManyToOneRel,
                models.ManyToManyRel,
            ),
        ):
            fields.append(field)
    return fields


def get_boolean_fields(model):
    fields = []
    for field in get_fields(model):
        if isinstance(field, (models.BooleanField,)):
            fields.append(field)
    return fields


def get_numeric_fields(model):
    fields = []
    for field in get_fields(model):
        if isinstance(
            field,
            (
                models.SmallIntegerField,
                models.PositiveSmallIntegerField,
                models.IntegerField,
                models.PositiveIntegerField,
                models.BigIntegerField,
                models.PositiveBigIntegerField,
                models.DecimalField,
                models.FloatField,
            ),
        ):
            fields.append(field)
    return fields


def get_text_fields(model, include_long_text=True):
    fields = []
    field_classes = [
        models.SlugField,
        models.CharField,
    ]
    if include_long_text:
        field_classes.append(models.TextField)

    for field in get_fields(model):
        if isinstance(field, tuple(field_classes)):
            fields.append(field)
    return fields


def get_time_fields(model, include_time=True):
    fields = []
    field_classes = [
        models.DateField,
        models.DurationField,
    ]
    if include_time:
        field_classes.extend(
            [
                models.DateTimeField,
                models.TimeField,
            ]
        )
    for field in get_fields(model):
        if isinstance(field, tuple(field_classes)):
            fields.append(field)
    return fields


def get_data_fields(model):
    fields = []
    for field in get_fields(model):
        if isinstance(field, (models.JSONField,)):
            fields.append(field)
    return fields


def get_web_fields(model):
    fields = []
    for field in get_fields(model):
        if isinstance(
            field,
            (
                models.EmailField,
                models.GenericIPAddressField,
                models.URLField,
            ),
        ):
            fields.append(field)
    return fields


def get_sortable_fields(model):
    return get_numeric_fields(model) + get_text_fields(model, False) + get_time_fields(model)


@lru_cache(maxsize=None)
def get_relations(model):
    fields = []
    for field in get_fields(model):
        if isinstance(field, models.ManyToManyField):
            fields.append({"multiple": True, "field": field})
        elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
            fields.append({"multiple": False, "field": field})
    return fields


@lru_cache(maxsize=None)
def get_reverse_relations(model):
    fields = []
    for field in get_fields(model):
        if isinstance(field, (models.OneToOneRel, models.ManyToOneRel)):
            fields.append({"multiple": False, "field": field})
        elif isinstance(field, models.ManyToManyRel):
            fields.append({"multiple": True, "field": field})
    return fields


def render_field_table(instance, *field_names, id=None, classes=None):
    field_map = {field.name: field for field in get_direct_fields(instance.__class__)}
    data = []

    if not field_names:
        field_names = list(field_map.keys())

    for name in field_names:
        value = getattr(instance, name)
        if isinstance(field_map[name], models.ManyToManyField):
            element = []
            for item in value.all():
                element.append(str(item))
            value = "\n".join(element)

        if value is not None:
            data.append([field_map[name].verbose_name, value])

    return render_to_string(
        "components/field_table.html",
        {
            "id": id,
            "classes": classes,
            "data": data,
        },
    )


class BaseModelMixin(models.Model):
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = now()
        self.updated = now()
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls, id, _id_field=None):
        if not _id_field:
            _id_field = cls._meta.pk.name
        try:
            instance = cls.objects.get(**{_id_field: id})
        except cls.DoesNotExist:
            instance = None
        return instance

    @classmethod
    def save_instance(cls, id, _id_field=None, **values):
        if not _id_field:
            _id_field = cls._meta.pk.name
        try:
            instance = cls.objects.get(**{_id_field: id})
            for field, value in values.items():
                setattr(instance, field, value)
            instance.save()

        except cls.DoesNotExist:
            instance = cls.objects.create(**{**values, _id_field: id})
        return instance

    @classmethod
    def remove_instance(cls, id, _id_field=None):
        if not _id_field:
            _id_field = cls._meta.pk.name
        return cls.objects.filter(**{_id_field: id}).delete()


class BaseHashedModelMixin(BaseModelMixin):
    id = models.CharField(primary_key=True, unique=True, max_length=65)

    class Meta:
        abstract = True


class BaseUUIDModelMixin(BaseModelMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid1, editable=False)

    class Meta:
        abstract = True


class BaseModel(BaseModelMixin):
    class Meta:
        abstract = True
        ordering = ["-created"]


class BaseHashedModel(BaseHashedModelMixin):
    class Meta:
        abstract = True
        ordering = ["-created"]


class BaseUUIDModel(BaseUUIDModelMixin):
    class Meta:
        abstract = True
        ordering = ["-created"]
