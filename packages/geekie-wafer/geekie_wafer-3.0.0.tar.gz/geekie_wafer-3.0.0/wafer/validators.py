# coding: utf-8
import datetime as _datetime
import re
import six

REQUIRED = "Obrigatório"
INTEGER = "Deve ser um inteiro"
NUMBER = "Deve ser um número"
GREATER_THAN = "Deve ser maior que {}"
GREATER_OR_EQUAL_THAN = "Deve ser maior ou igual à {}"
LESS_THAN = "Deve ser menor que {}"
LESS_OR_EQUAL_THAN = "Deve ser menor ou igual à {}"
BOOL = "Deve ser verdadeiro ou falso"
INVALID = "Valor inválido"
INSTANCEOF = "Deve ser um objeto {}"
OBJECTID = "Deve ser um ObjectId"
DATETIME = "Deve ser uma data"
CHOICES = "Deve ser um dentre {}"


def required(msg=REQUIRED):
    def validator(obj):
        if obj is None:
            yield msg

    return validator


def instanceof(type, msg=INSTANCEOF):
    def validator(obj):
        if obj is not None and not isinstance(obj, type):
            yield msg.format(type)

    return validator


def integer(msg=INTEGER):
    return instanceof(int, msg=msg)


def greater_than(number, msg=GREATER_THAN):
    def validator(obj):
        if obj is not None and obj <= number:
            yield msg.format(number)

    return validator


def less_than(number, msg=LESS_THAN):
    def validator(obj):
        if obj is not None and obj >= number:
            yield msg.format(number)

    return validator


def non_empty_string(msg=REQUIRED):
    def validator(obj):
        if obj is not None and not (
            isinstance(obj, str if six.PY3 else basestring)  # noqa: F821
            and len(obj) > 0
        ):
            yield msg

    return validator


def unicode_string(msg="String must be unicode"):
    return instanceof(six.text_type, msg=msg)


def bool(msg=BOOL):
    def validator(obj):
        if obj is not None and not (obj is True or obj is False):
            yield msg

    return validator


def matches_regex(regex, msg=INVALID):
    def validator(obj):
        compiled_regex = re.compile(regex.rstrip("$") + "$")

        if obj is not None and not compiled_regex.match(obj):
            yield msg

    return validator


def number(
    min_range_inclusive=None,
    min_range_exclusive=None,
    max_range_inclusive=None,
    max_range_exclusive=None,
):
    def validator(obj):
        if obj is None:
            return

        try:
            float(obj)
        except ValueError:
            yield NUMBER

        if min_range_inclusive is not None:
            if obj < min_range_inclusive:
                yield GREATER_OR_EQUAL_THAN.format(min_range_inclusive)
        elif min_range_exclusive is not None:
            if obj <= min_range_exclusive:
                yield GREATER_THAN.format(min_range_exclusive)

        if max_range_inclusive is not None:
            if obj > max_range_inclusive:
                yield LESS_OR_EQUAL_THAN.format(max_range_inclusive)
        elif max_range_exclusive is not None:
            if obj >= max_range_exclusive:
                yield LESS_THAN.format(max_range_exclusive)

    return validator


def number_str(
    min_range_inclusive=None,
    min_range_exclusive=None,
    max_range_inclusive=None,
    max_range_exclusive=None,
):
    def validator(obj):
        if obj is None:
            return
        try:
            for error in number(
                min_range_inclusive,
                min_range_exclusive,
                max_range_inclusive,
                max_range_exclusive,
            )(float(obj)):
                yield error
        except ValueError:
            yield NUMBER

    return validator


# Convenience functions
def required_positive_integer():  # pragma: no cover
    return [required()] + positive_integer()


def required_non_negative_integer():  # pragma: no cover
    return [required()] + non_negative_integer()


def positive_integer():  # pragma: no cover
    return [integer(), greater_than(0)]


def non_negative_integer():  # pragma: no cover
    return [integer(), greater_than(-1)]


def in_list(valid_values, msg=INVALID):
    def validator(obj):
        if obj is not None and obj not in valid_values:
            yield msg

    return validator


def objectid(msg=OBJECTID):
    import bson

    return instanceof(bson.ObjectId, msg=msg)


def datetime(msg=DATETIME):
    return instanceof(_datetime.datetime, msg=msg)


def choices(choices, msg=CHOICES):
    choices = set(choices)

    def validator(obj):
        if obj is not None and obj not in choices:
            yield msg.format(choices)

    return validator
