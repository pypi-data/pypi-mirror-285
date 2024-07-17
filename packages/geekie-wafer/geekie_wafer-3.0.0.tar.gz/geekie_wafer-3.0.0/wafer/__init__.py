import collections
import operator
import re
import six

from wafer import validators as wafer_validators


class ValidationError(Exception):
    def __init__(self, errors):
        super(ValidationError, self).__init__(
            "The model has validation errors on "
            + ", ".join(set(field for field, message in errors))
        )
        self.__errors = errors

    @property
    def errors(self):
        return self.__errors

    @property
    def errors_dict(self):
        result = collections.defaultdict(lambda: [])
        for field, error in self.errors:
            result[field].append(error)
        return result


class NotDeserializableError(Exception):
    pass


class Field(object):
    def __init__(
        self,
        model=None,
        default=None,
        json_name=None,
        validators=None,
        required=False,
        choices=None,
        eq=operator.eq,
    ):
        self._model = model
        self.json_name = json_name
        self._default = default
        self._validators = validators or []
        self._eq = eq

        if required:
            self._validators.append(wafer_validators.required())
        if choices is not None:
            self._validators.append(wafer_validators.choices(choices))

    @property
    def default(self):
        if callable(self._default):
            return self._default()
        return self._default

    def serialize(self, obj, **kwargs):
        if self._model is not None and obj is not None:
            return self._model.serialize(obj, **kwargs)
        else:
            return obj

    def deserialize(self, obj):
        if self._model is not None and obj is not None:
            return self._model.load(obj)
        else:
            return obj

    def validate(self, obj):
        for validator in self._validators:
            for error in validator(obj):
                yield error

    def accept(self, visitor, field_value):
        for value in visitor(self, field_value):
            yield "", value

        if self._model and issubclass(self._model, Model) and field_value:
            # Note: field_value is a wafer model
            for key, value in field_value.accept(visitor):
                yield key, value


class Computed(Field):
    def __init__(self, json_name=None, validators=None, setter=None, getter=None):
        if callable(json_name):  # Decorator was called without parameters
            getter = json_name
            json_name = None
        super(Computed, self).__init__(json_name=json_name, validators=validators)
        self.__getter = getter
        self.__setter = setter

    def __get__(self, instance, instance_type):
        if instance is None:  # pragma: no cover
            return self
        if self.__getter is None:
            raise AttributeError("Computed has no getter")
        return self.__getter(instance)

    def __set__(self, instance, value):
        if self.__setter is None:
            raise AttributeError("Can't set computed field")
        return self.__setter(instance, value)

    def __call__(self, decorated):
        return type(self)(
            self.json_name, self._validators, getter=decorated, setter=self.__setter
        )

    def setter(self, decorated):
        return type(self)(
            self.json_name, self._validators, getter=self.__getter, setter=decorated
        )

    def deserialize(self, value):
        raise NotDeserializableError


class EmbeddedCollection(Field):
    def __init__(self, *args, **kwargs):
        super(EmbeddedCollection, self).__init__(*args, **dict(kwargs, required=False))
        self.__required = kwargs.get("required", False)

    def serialize(self, items, **kwargs):
        if not items:
            return None
        else:
            return [
                super(EmbeddedCollection, self).serialize(item, **kwargs)
                for item in items
            ]

    def deserialize(self, items):
        if not items:
            return []
        else:
            return [super(EmbeddedCollection, self).deserialize(item) for item in items]

    def validate(self, items):
        if not items:
            if self.__required:
                yield "Mandatory field"
            else:
                return
        else:
            for index, item in enumerate(items):
                for error in super(EmbeddedCollection, self).validate(item):
                    yield "Element at {index}: {error}".format(index=index, error=error)

    def accept(self, visitor, field_value):
        for value in visitor(self, field_value):
            yield "", value

        if self._model and issubclass(self._model, Model) and field_value:
            # Note: field_value is a list of wafer models
            for inner_holder_model in field_value:
                for key, value in inner_holder_model.accept(visitor):
                    yield key, value

    @property
    def default(self):
        return super(EmbeddedCollection, self).default or []


class DictField(Field, dict):
    # We can't have objectid keys in a dict so we serialize them as strings

    def __init__(self, value_field=None, **kwargs):
        self._value_field = value_field or Field()
        kwargs.setdefault("default", dict)
        super(DictField, self).__init__(**kwargs)

    def serialize(self, value, **kwargs):
        return {k: self._value_field.serialize(v, **kwargs) for k, v in value.items()}

    def deserialize(self, value):
        return {k: self._value_field.deserialize(v) for k, v in value.items()}

    def accept(self, visitor, field_value):
        for value in visitor(self, field_value):  # pragma: no cover
            yield "", value

        if field_value and self._value_field and isinstance(self._value_field, Field):
            for value in field_value.values():
                for k, v in self._value_field.accept(visitor, value):
                    yield k, v


class ModelMetaclass(type):
    def __new__(metacls, name, parents, attributes):
        if parents == (object,):
            return super(ModelMetaclass, metacls).__new__(
                metacls, name, parents, attributes
            )
        else:
            mangled_prefix = "_" + name + "__"
            attributes["_Model__fields"] = fields = {}

            for key, value in dict(attributes).items():
                if isinstance(value, Field):
                    if not isinstance(value, Computed):
                        del attributes[key]
                    if key.startswith(mangled_prefix) and key.endswith("_field"):
                        key = key[len(mangled_prefix) : -len("_field")]
                    fields[key] = value

            for base in parents:
                if issubclass(base, Model) and base is not Model:
                    for key, value in base.fields().items():
                        fields.setdefault(key, value)

            return super(ModelMetaclass, metacls).__new__(
                metacls, name, parents, attributes
            )


class LoadModelError(Exception):
    pass


@six.add_metaclass(ModelMetaclass)
class Model(object):
    __polymorphism_field__ = None

    @classmethod
    def fields(cls):
        return cls.__fields

    @classmethod
    def sorted_fields(cls):
        return sorted(cls.__fields.keys())

    @classmethod
    def load(cls, serialized):
        poly_field = cls.__polymorphism_field__
        idt = serialized.get(poly_field)

        if idt and cls.fields().get(poly_field, Field()).default != idt:
            for sub in cls.__subclasses__():
                try:
                    return sub.load(serialized)
                except LoadModelError:
                    pass
            raise LoadModelError("Unknown type '{}' under {}".format(idt, cls.__name__))

        return cls.from_dict(serialized)

    @classmethod
    def from_dict(cls, serialized):
        loaded = cls()
        loaded.__start_values = serialized
        loaded.pre_load()
        for key, value in list(serialized.items()):
            try:
                field = cls.fields()[key]
            except KeyError:
                continue
            try:
                setattr(loaded, key, field.deserialize(value))
            except NotDeserializableError:
                continue
        loaded.post_load()
        return loaded

    def __init__(self, **kwargs):
        self.__start_values = {}

        for key, value in list(kwargs.items()):
            field = self.__class__.fields().get(key)
            if isinstance(field, Computed):
                raise ValueError(
                    "Can't set computed field {} in model constructor".format(key)
                )
            if not (field or hasattr(self, key)):
                raise KeyError(self.__class__.__name__ + "." + key)
            setattr(self, key, value)

    def __getattr__(self, key):
        try:
            default_value = self.__class__.fields()[key].default
            setattr(self, key, default_value)
            return default_value
        except KeyError:
            raise AttributeError(key)

    def serialize(self, json=False, validate=None):
        if validate is None:
            validate = not json
        if validate:
            self.validate()

        dictionary = {}

        def camelcase(key):
            prefix = re.split("[^_]", key)[0]
            camel_case_key = re.sub(
                r"_+(.)", lambda pattern: pattern.group(1).upper(), key
            )
            camel_case_key = camel_case_key[0].lower() + camel_case_key[1:]
            return prefix + camel_case_key

        for key, field in list(self.__class__.fields().items()):
            value = field.serialize(getattr(self, key), json=json, validate=validate)
            if value is not None:
                if json:
                    dictionary[field.json_name or camelcase(key)] = value
                else:
                    dictionary[key] = value

        if not json:
            # Add extra fields to serialized model
            dictionary.update(
                {
                    k: v
                    for k, v in list(self.__start_values.items())
                    if k not in self.__class__.fields()
                }
            )

        return dictionary

    def unset_legacy_field(self, field_name):
        if field_name in self.__class__.fields():
            raise ValueError("{} is not a legacy field".format(field_name))
        self.__start_values.pop(field_name, None)

    @property
    def dirty_fields(self):  # pragma: no cover
        return {
            key: value
            for key, value in list(self.serialize().items())
            if key not in self.__start_values or value != self.__start_values[key]
        }

    def clear_dirty_fields(self):  # pragma: no cover
        self.__start_values = self.serialize()

    def pre_load(self):
        pass

    def post_load(self):
        pass

    def validate(self, context=None):
        errors = []
        for field, error in self.enumerate_errors(context):
            errors.append((field, error))
        if errors:
            raise ValidationError(errors)

    def enumerate_errors(self, context=None):
        def visitor(field, field_value):
            for error in field.validate(field_value):
                yield error

        for key, error in self.accept(visitor):
            yield key, error

    def to_json(self):
        return self.serialize(json=True)

    def __repr__(self):
        def add_indent(text):
            return "\n    ".join(text.split("\n"))

        return "{type}(\n    {values}\n)".format(
            type=self.__class__.__name__,
            values=add_indent(
                ",\n".join(
                    "{key}={value}".format(key=field, value=repr(getattr(self, field)))
                    for field in self.__class__.sorted_fields()
                )
            ),
        )

    def clone(self):
        return self.__class__.load(self.serialize(validate=False))

    def accept(self, visitor):
        for key, field in list(self.__class__.fields().items()):
            for inner_key, processed in field.accept(visitor, getattr(self, key)):
                yield "{}{}".format(
                    key, "." + inner_key if inner_key else ""
                ), processed

    def populate(self, **kwargs):
        for key, value in list(kwargs.items()):
            setattr(self, key, value)

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and all(
            field._eq(getattr(self, key), getattr(other, key))
            for key, field in self.__class__.fields().items()
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    # This marks this object as unhashable. It is up to subclasses to provide
    # a implementation:
    #
    # See http://docs.python.org/reference/datamodel.html#object.__hash__
    __hash__ = None
