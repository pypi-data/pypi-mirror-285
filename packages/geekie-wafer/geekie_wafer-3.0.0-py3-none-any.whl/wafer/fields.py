import datetime
import six

import wafer
from wafer import validators as wafer_validators


class DateField(wafer.Field):
    def serialize(self, date, **kwargs):
        return [date.year, date.month, date.day] if date else None

    def deserialize(self, arr):
        return datetime.date(*[int(x) for x in arr[:3]]) if arr else None


def _eq_datetime(a, b):
    if isinstance(a, datetime.datetime) and isinstance(b, datetime.datetime):
        return a.replace(microsecond=a.microsecond // 1000 * 1000) == b.replace(
            microsecond=b.microsecond // 1000 * 1000
        )
    return a == b


class DateTimeField(wafer.Field):
    def __init__(self, *args, **kwargs):
        if "auto_now_add" in kwargs:
            kwargs["default"] = datetime.datetime.utcnow
            kwargs.pop("auto_now_add")

        kwargs.setdefault("eq", _eq_datetime)
        kwargs.setdefault("validators", []).append(wafer_validators.datetime())
        super(DateTimeField, self).__init__(*args, **kwargs)

    def deserialize(self, value, **kwargs):
        return value.replace(tzinfo=None) if value else None


class BlobField(wafer.Field):
    # Defer importing `bson` so that any import errors only happen when the field is actually used

    def __init__(self, *args, **kwargs):
        import bson  # noqa: F401

        super(BlobField, self).__init__(*args, **kwargs)

    def serialize(self, blob, **kwargs):
        import bson.binary

        return bson.binary.Binary(blob) if blob else None

    def deserialize(self, s):
        return six.binary_type(s) if s else None


class TupleField(wafer.Field):
    """A field whose value is a tuple.
    This is serialized as an array in the datastore, but converted back to a tuple when
    deserialized."""

    def deserialize(self, tuple_):
        return tuple(tuple_) if tuple_ else None


class ConstantField(wafer.Field):
    def __init__(self, value):
        super(ConstantField, self).__init__(default=value)
        self.value = value

    def serialize(self, *args, **kwargs):
        return self.value

    def deserialize(self, *args, **kwargs):
        return self.value


class UnicodeStringField(wafer.Field):
    def __init__(self, **kwargs):
        kwargs.setdefault("validators", []).append(wafer_validators.unicode_string())
        super(UnicodeStringField, self).__init__(**kwargs)

    # Wafer doesn't use descriptors =(
    def _convert(self, obj):
        if isinstance(obj, str if six.PY2 else bytes):
            return obj.decode("utf-8")
        return obj

    def validate(self, obj):
        obj = self._convert(obj)
        return super(UnicodeStringField, self).validate(obj)

    def serialize(self, obj, **kwargs):
        obj = self._convert(obj)
        return super(UnicodeStringField, self).serialize(obj, **kwargs)


class DeprecatedEnumField(wafer.Field):  # pragma: no cover
    def __init__(self, options, **kwargs):
        self.options = options or []
        super(DeprecatedEnumField, self).__init__(choices=options, **kwargs)

    def serialize(self, value, **kwargs):
        try:
            value = self.options.index(value)
        except ValueError:
            pass
        return value

    def deserialize(self, value):
        try:
            value = self.options[int(value)]
        except (ValueError, IndexError):
            pass
        return value


def typed_field(builtin_validators=()):
    class TypedField(wafer.Field):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("validators", []).extend(builtin_validators)
            super(TypedField, self).__init__(*args, **kwargs)

    return TypedField


BooleanField = typed_field([wafer_validators.bool()])
IntField = typed_field([wafer_validators.integer()])

try:
    basestring
except NameError:  # pragma: no cover
    basestring = str

StringField = typed_field([wafer_validators.instanceof(basestring)])


class ObjectIdField(wafer.Field):
    # Not using `typed_field` here so we can defer calling `validators.objectid()`.
    # That way we only throw an error for missing `bson` if this field is actually used.

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("validators", []).append(wafer_validators.objectid())
        super(ObjectIdField, self).__init__(*args, **kwargs)
