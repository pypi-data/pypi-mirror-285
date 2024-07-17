import bson
import datetime
import datadriven
import unittest
from freezegun import freeze_time

import wafer
from wafer import fields


def test_date_field_serialization():
    class Model(wafer.Model):
        date = fields.DateField()

    model = Model(date=datetime.date(2020, 12, 1))
    assert model.serialize() == {"date": [2020, 12, 1]}
    assert Model.load(model.serialize()).date == model.date


@freeze_time()
def test_datetime_default():
    class Model(wafer.Model):
        created_at = fields.DateTimeField(auto_now_add=True)

    now = datetime.datetime.utcnow()
    assert Model().created_at == now


def test_datetime_serialization():
    class Model(wafer.Model):
        created_at = fields.DateTimeField()

    now = datetime.datetime.utcnow()
    model = Model(created_at=now)
    assert model.serialize() == {"created_at": now}
    assert Model.load(model.serialize()).created_at == now


def test_datetime_eq():
    class Model(wafer.Model):
        created_at = fields.DateTimeField()

    m1 = Model(created_at=datetime.datetime(2020, 1, 1, 0, 0, 0, 999999))
    m2 = Model(created_at=datetime.datetime(2020, 1, 1, 0, 0, 0, 999000))
    m3 = Model(created_at="foo")

    assert m1 == m2
    assert m1.created_at != m2.created_at
    assert m1 != m3

    assert Model(created_at=None) == Model(created_at=None)


def test_blob_serialization():
    class Model(wafer.Model):
        blob = fields.BlobField()

    model = Model(blob=b"blob value")
    assert isinstance(model.serialize()["blob"], bson.binary.Binary)
    assert Model.load(model.serialize()).blob == b"blob value"


def test_tuple_deserialization():
    class Model(wafer.Model):
        date = fields.TupleField()

    assert Model.load({"date": [2020, 12, 1]}).date == (2020, 12, 1)


def test_unicode_string_is_converted_when_serializing():
    class Model(wafer.Model):
        unistr = fields.UnicodeStringField()

    model = Model(unistr=b"bytes text")
    assert model.serialize() == {"unistr": "bytes text"}


class TypedFieldsTest(unittest.TestCase):
    @datadriven.datadriven(
        objectid=datadriven.Args(
            field=fields.ObjectIdField(),
            valid_value=bson.ObjectId(),
            invalid_value=str(bson.ObjectId()),
        ),
        datetime=datadriven.Args(
            field=fields.DateTimeField(),
            valid_value=datetime.datetime.utcnow(),
            invalid_value=datetime.datetime.utcnow().isoformat(),
        ),
        int=datadriven.Args(
            field=fields.IntField(),
            valid_value=1,
            invalid_value="1",
        ),
        string=datadriven.Args(
            field=fields.StringField(),
            valid_value="Foo",
            invalid_value=["foo"],
        ),
        unicode_string=datadriven.Args(
            field=fields.UnicodeStringField(),
            valid_value="Foo",
            invalid_value=["foo"],
        ),
        bool=datadriven.Args(
            field=fields.BooleanField(),
            valid_value=True,
            invalid_value="False",
        ),
    )
    def test_they_are_typed(self, field, valid_value, invalid_value):
        self.assertEqual(0, sum(1 for _ in field.validate(valid_value)))
        self.assertGreater(sum(1 for _ in field.validate(invalid_value)), 0)
