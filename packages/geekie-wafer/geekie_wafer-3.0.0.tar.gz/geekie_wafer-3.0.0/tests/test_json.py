import unittest

import wafer


class Mayor(wafer.Model):
    full_name = wafer.Field()


class Tree(wafer.Model):
    x_position = wafer.Field(json_name="X")
    y_position = wafer.Field(json_name="Y")


class City(wafer.Model):
    _id = wafer.Field()
    city_name = wafer.Field()
    mayor = wafer.Field(Mayor)
    trees = wafer.EmbeddedCollection(Tree)


class WaferJsonSerializationTest(unittest.TestCase):
    def test_json_serialization_of_complex_document(self):
        document = City(
            _id="id",
            city_name="Town",
            mayor=Mayor(full_name="*Le mayor"),
            trees=[Tree(x_position=1, y_position=2)],
        )
        self.assertEqual(
            {
                "_id": "id",
                "cityName": "Town",
                "mayor": {"fullName": "*Le mayor"},
                "trees": [{"X": 1, "Y": 2}],
            },
            document.to_json(),
        )
