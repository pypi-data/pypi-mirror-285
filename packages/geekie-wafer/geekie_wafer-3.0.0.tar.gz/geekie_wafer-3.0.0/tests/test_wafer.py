# coding: utf-8
import bson
import copy
import datadriven as data
import six
import textwrap
import unittest

import wafer
from wafer import fields, validators


# Some models
class Thing(wafer.Model):
    __polymorphism_field__ = "poly"

    poly = fields.ConstantField("parent")
    weight = wafer.Field()


class Eatable(Thing):
    poly = fields.ConstantField("son")
    calories = wafer.Field(validators=[validators.required()])


class SomeModel(wafer.Model):
    experience = wafer.Field()
    lucky = wafer.Field()


class Menu(wafer.Model):
    class LocationConverter(object):
        @staticmethod
        def serialize(item):
            if item is None:
                return None
            elif item == "Sao Jose dos Campos":
                return "SJK"
            else:
                return "???"

        @staticmethod
        def deserialize(item):
            if item is None:
                return None
            elif item == "SJK":
                return "Sao Jose dos Campos"
            else:
                return "Other"

    dish_of_the_day = wafer.Field(Eatable)
    main_courses = wafer.EmbeddedCollection(Eatable)


class MenuContainer(wafer.Model):
    menu = wafer.Field(Menu)


class Metal(wafer.Model):
    name = wafer.Field()

    def __init__(self, *args, **kwargs):
        self.__conductivity = None
        super(Metal, self).__init__(*args, **kwargs)

    @property
    def conductivity(self):
        return self.__conductivity

    @conductivity.setter
    def conductivity(self, value):
        if value < 0:
            raise ValueError("value must be 0 or more")
        self.__conductivity = value


class EngineTest(unittest.TestCase):
    def test_only_model_attributes_never_raise_AttributeError(self):
        model = Thing()
        self.assertIsNone(model.weight)  # should not raise AttributeError
        with self.assertRaises(AttributeError):
            model.bogus_attribute

    def test_load_simple_model(self):
        model = Thing.load({"weight": 0.453})
        self.assertEqual(0.453, model.weight)

    def test_serialize_simple_model(self):
        model = Thing()
        model.weight = 0.453
        self.assertEqual(0.453, model.serialize()["weight"])

    def test_load_simple_model_from_parent_class(self):
        model = Thing.load({"weight": 0.453, "calories": 100, "poly": "son"})

        self.assertIsInstance(model, Eatable)
        self.assertEqual(100, model.calories)
        self.assertEqual(0.453, model.weight)

    def test_poly_field_unfound(self):
        with six.assertRaisesRegex(
            self, wafer.LoadModelError, "Unknown type 'unexpected' under Thing"
        ):
            Thing.load({"poly": "unexpected"})

    def test_load_simple_model_with_inheritance(self):
        model = Eatable.load(dict(weight=0.453, calories=100))

        self.assertEqual(100, model.calories)
        self.assertEqual(0.453, model.weight)

    def test_serialize_simple_model_with_inheritance(self):
        model = Eatable(weight=0.453, calories=100)
        model_data = model.serialize()

        self.assertEqual(100, model_data["calories"])
        self.assertEqual(0.453, model_data["weight"])

    def test_load_accepts_legacy_attributes_not_in_model_but_is_not_an_attribute(self):
        model = Thing()
        model.load({"bogus": True})
        with self.assertRaises(AttributeError):
            model.bogus

    def test_constructor_raises_error_if_attribute_not_in_model(self):
        with self.assertRaises(KeyError):
            Thing(bogus=True)

    def test_constructor_does_not_raise_error_if_attribute_is_not_field_but_is_property(
        self,
    ):
        class AmericanEatable(Eatable):
            @property
            def weight_in_pounds(self):
                return self.weight / 0.453 if self.weight else None

            @weight_in_pounds.setter
            def weight_in_pounds(self, value):
                self.weight = value * 0.453 if value else None

        apple = AmericanEatable(calories=100, weight_in_pounds=1)
        self.assertEqual(0.453, apple.weight)

    def test_load_works_if_value_is_none(self):
        model = Thing()
        model.load({"weight": None})

        self.assertIsNone(model.weight)

    def test_serialize_works_if_value_is_none(self):
        model = SomeModel()
        model.experience = None
        model.lucky = 9

        self.assertEqual({"lucky": 9}, model.serialize())

    def test_load_model_with_embedded_document(self):
        model = Menu.load({"dish_of_the_day": {"weight": 0.453}})
        self.assertEqual(0.453, model.dish_of_the_day.weight)

    def test_serialize_model_with_embedded_document(self):
        model = Menu(dish_of_the_day=Eatable(weight=0.453, calories=100))

        self.assertEqual(
            {
                "dish_of_the_day": {"weight": 0.453, "poly": "son", "calories": 100},
            },
            model.serialize(),
        )

    def test_serialize_model_with_embedded_empty_collection(self):
        model = Menu(main_courses=[])
        self.assertEqual({}, model.serialize())

    def test_load_model_with_embedded_collection(self):
        model = Menu.load(
            {
                "main_courses": [
                    {"weight": 1.1, "calories": 1000},
                    {"weight": 2.2, "calories": 2000},
                ]
            }
        )

        self.assertEqual(2, len(model.main_courses))
        self.assertEqual(2.2, model.main_courses[1].weight)
        self.assertEqual(1000, model.main_courses[0].calories)

    def test_save_model_with_embedded_collection(self):
        model = Menu(
            main_courses=[
                Eatable(weight=1, calories=10),
                Eatable(weight=2, calories=15),
            ]
        )
        self.assertEqual(
            {
                "main_courses": [
                    {
                        "weight": 1,
                        "poly": "son",
                        "calories": 10,
                    },
                    {
                        "weight": 2,
                        "poly": "son",
                        "calories": 15,
                    },
                ]
            },
            model.serialize(),
        )

    def test_populate(self):
        model = Thing()
        self.assertIsNone(model.weight)
        model.populate(weight=10)
        self.assertEqual(model.weight, 10)

    def test_clone(self):
        model = Menu(
            main_courses=[
                Eatable(weight=1, calories=10),
                Eatable(weight=2, calories=15),
            ]
        )
        clone = model.clone()
        self.assertEqual(model, clone)
        clone.main_courses[0].calories = 9
        self.assertEqual(10, model.main_courses[0].calories)

    def test_deepcopy_model_with_embedded_collection(self):
        model = Menu(
            main_courses=[
                Eatable(weight=1, calories=10),
                Eatable(weight=2, calories=15),
            ]
        )
        clone = copy.deepcopy(model)
        clone.main_courses[0].calories = 9
        self.assertEqual(10, model.main_courses[0].calories)

    def test_default_value_of_embedded_collection(self):
        model1 = Menu()
        model2 = Menu()
        self.assertIsNot(
            model1.main_courses,
            model2.main_courses,
            msg="Empty list created on the fly must not be the shared "
            "between instances",
        )
        self.assertIs(
            model1.main_courses,
            model1.main_courses,
            msg="Empty list created on the fly must be stored as the attribute "
            "value on the first access",
        )

    def test_allows_usage_of_properties(self):
        model = Metal(conductivity=2)
        self.assertEqual(2, model.conductivity)

        with self.assertRaises(ValueError):
            model = Metal(conductivity=-2)

    def test_repr(self):
        eatable = SomeModel()
        self.assertEqual(
            textwrap.dedent(
                """\
                SomeModel(
                    experience=None,
                    lucky=None
                )"""
            ),
            repr(eatable),
        )
        eatable = Eatable(calories=124.5, weight="70 kg")
        self.assertMultiLineEqual(
            textwrap.dedent(
                """\
            Eatable(
                calories=124.5,
                poly='son',
                weight='70 kg'
            )"""
            ),
            repr(eatable),
        )

    def test_repr_with_nested_models(self):
        self.maxDiff = None

        menu = MenuContainer(
            menu=Menu(
                main_courses=[
                    Eatable(calories=100, weight=1),
                    Eatable(calories=200, weight=2),
                ],
            ),
        )

        self.assertMultiLineEqual(
            textwrap.dedent(
                """\
            MenuContainer(
                menu=Menu(
                    dish_of_the_day=None,
                    main_courses=[Eatable(
                        calories=100,
                        poly='son',
                        weight=1
                    ), Eatable(
                        calories=200,
                        poly='son',
                        weight=2
                    )]
                )
            )"""
            ),
            repr(menu),
        )

    def test_str_defaults_to_repr(self):
        eatable = SomeModel()
        self.assertMultiLineEqual(
            textwrap.dedent(
                """\
            SomeModel(
                experience=None,
                lucky=None
            )"""
            ),
            str(eatable),
        )

    def test_str_can_be_overriden_without_altering_repr(self):
        class Sherman(SomeModel):
            def __str__(self):
                return "Sherminator"

        self.assertMultiLineEqual("Sherminator", str(Sherman()))
        self.assertMultiLineEqual(
            textwrap.dedent(
                """\
            Sherman(
                experience=100,
                lucky=7
            )"""
            ),
            repr(Sherman(experience=100, lucky=7)),
        )

    def test_equality_operator(self):
        apple = Eatable(calories=100, weight=0.5)
        same_apple = Eatable(calories=100, weight=0.5)
        another_apple = Eatable(calories=100, weight=0.6)
        bad_apple = Eatable()

        self.assertEqual(apple, same_apple)
        self.assertNotEqual(apple, another_apple)
        self.assertNotEqual(apple, bad_apple)

    def test_validates_model_in_depth(self):
        main_menu = Menu(dish_of_the_day=Eatable(weight=0.453))
        with self.assertRaises(wafer.ValidationError):
            main_menu.serialize()
        main_menu.dish_of_the_day.calories = 10
        main_menu.serialize()


class FieldTests(unittest.TestCase):
    def test_default_default_value(self):
        field = wafer.Field()
        self.assertIsNone(field.default)

    def test_simple_default_value(self):
        field = wafer.Field(default="hello world")
        self.assertEqual("hello world", field.default)

    def test_lambda_default_value(self):
        field = wafer.Field(default=lambda: [])
        self.assertEqual([], field.default)
        self.assertIsNot(field.default, field.default)

    def test_function_default_value(self):
        def value_generator():
            return []

        field = wafer.Field(default=value_generator)
        self.assertEqual([], field.default)
        self.assertIsNot(field.default, field.default)

    def test_constructor_default_value(self):
        class Clazz(object):
            pass

        field = wafer.Field(default=Clazz)
        self.assertIsInstance(field.default, Clazz)
        self.assertIsNot(field.default, field.default)

    def test_required_is_true(self):
        field = wafer.Field(required=True)
        self.assertEqual([], list(field.validate(False)))
        self.assertNotEqual([], list(field.validate(None)))

    def test_choices(self):
        field = wafer.Field(choices=["red", "blue"])
        self.assertEqual([], list(field.validate(None)))
        self.assertEqual([], list(field.validate("red")))
        self.assertNotEqual([], list(field.validate("green")))


class EmbeddedCollectionTests(unittest.TestCase):
    def test_deserialize_none(self):
        class Example(wafer.Model):
            collection = wafer.EmbeddedCollection()

        example = Example.load({"collection": None})
        self.assertEqual(example.collection, [])

    def test_default_default_value(self):
        field = wafer.EmbeddedCollection()
        self.assertEqual([], field.default)
        self.assertIsNot(field.default, field.default)

    def test_simple_default_value(self):
        field = wafer.EmbeddedCollection(default=[1, 2])
        self.assertEqual([1, 2], field.default)

    def test_lambda_default_value(self):
        field = wafer.EmbeddedCollection(default=lambda: [1, 2])
        self.assertEqual([1, 2], field.default)
        self.assertIsNot(field.default, field.default)

    @data.datadriven(
        value_is_none=data.Args(None),
        items_are_empty=data.Args([]),
    )
    def test_required_field_fails_when(self, items):
        with self.assertRaises(wafer.ValidationError) as e:
            self.get_example_model(items, None).validate()
        self.assertEqual(
            e.exception.errors, [("required_collection", "Mandatory field")]
        )

    def test_required_embedded_collection_can_hold_falsy_elements_in_the_array(self):
        example = self.get_example_model(["", None, 0])
        example.validate()

    def test_validator_required_is_for_items(self):
        with self.assertRaises(wafer.ValidationError) as e:
            self.get_example_model([1], [None, "ok"]).validate()
        self.assertEqual(
            e.exception.errors,
            [("items_cant_be_falsy", "Element at 0: Obrigatório")],
        )

    def get_example_model(self, required_collection=None, items_cant_be_falsy=None):
        class EmbeddedExample(wafer.Model):
            required_collection = wafer.EmbeddedCollection(required=True)
            items_cant_be_falsy = wafer.EmbeddedCollection(
                validators=[validators.required()]
            )

        return EmbeddedExample(
            required_collection=required_collection,
            items_cant_be_falsy=items_cant_be_falsy,
        )


class ValidationErrorTests(unittest.TestCase):
    def test_errors_dict(self):
        error = wafer.ValidationError(
            (("players", "mario"), ("worlds", "1-1"), ("players", "luigi"))
        )
        errors_dict = error.errors_dict
        self.assertEqual(["1-1"], errors_dict["worlds"])
        self.assertEqual(["mario", "luigi"], errors_dict["players"])

    def test_errors_dict_empty(self):
        self.assertFalse(wafer.ValidationError([]).errors_dict)


class Name(wafer.Model):
    full_name = wafer.Field(default="")

    @wafer.Computed
    def family_name(self):
        return self.full_name.split(" ", 1)[1] if " " in self.full_name else ""

    @family_name.setter
    def family_name(self, value):
        self.full_name = "{}{}".format(
            self.given_name + " " if self.given_name else "", value
        )

    @wafer.Computed(json_name="givenName")
    def given_name(self):
        return self.full_name.split(" ")[0]

    @given_name.setter
    def given_name(self, value):
        self.full_name = "{}{}".format(
            value, " " + self.family_name if self.family_name else ""
        )

    def __init__(self, given_name=None, **kwargs):
        super(Name, self).__init__(**kwargs)
        if given_name:
            self.given_name = given_name


class ComputedFieldsTest(unittest.TestCase):
    def test_computed_reflects_changes_on_underliyng_field(self):
        name = Name(full_name="Leonardo Da Vinci")
        self.assertEqual(name.given_name, "Leonardo")
        self.assertEqual(name.family_name, "Da Vinci")
        name.full_name = "Aspirina Da Vinte"
        self.assertEqual(name.given_name, "Aspirina")
        self.assertEqual(name.family_name, "Da Vinte")

    def test_skipping_computed_in_load(self):
        name = Name("Sheldon Cooper")
        serialized = name.serialize()
        self.assertEqual(
            serialized,
            {
                "full_name": "Sheldon Cooper",
                "given_name": "Sheldon",
                "family_name": "Cooper",
            },
        )
        # Changing computed values directly in mongo should never happen
        serialized["given_name"] = "Leonard"
        serialized["family_name"] = "Hofstadter"
        loaded_name = Name.load(serialized)
        self.assertEqual(loaded_name.full_name, "Sheldon Cooper")

    def test_argument_setter_changes_underlying_fields(self):
        jon = Name("Jon Snow")
        jon.family_name = "Stark"
        self.assertEqual(jon.full_name, "Jon Stark")

    def test_decorator_setter_changes_underlying_fields(self):
        close = Name("Luis Gambine Moreira")
        close.given_name = "Roberta"
        self.assertEqual(close.full_name, "Roberta Gambine Moreira")
        close.family_name = "Close"
        self.assertEqual(close.full_name, "Roberta Close")

    def test_cant_set_computed_in_init(self):
        with self.assertRaises(ValueError):
            Name(family_name="Valjean")

    def test_computed_with_no_accessor_raises_attribute_error(self):
        class SomeClass(object):
            field = wafer.Computed()

        example = SomeClass()
        with self.assertRaises(AttributeError):
            example.field
        with self.assertRaises(AttributeError):
            example.field = 10

    def test_subclass_can_handle_computed_in_init(self):
        name = Name(given_name="Jean")
        self.assertEqual(name.given_name, "Jean")
        self.assertEqual(name.full_name, "Jean")


class SimpleThing(wafer.Model):

    name = fields.StringField()
    some_dict = wafer.DictField()


class SimpleModel(wafer.Model):

    some_id = fields.ObjectIdField()


class ComplexThing(wafer.Model):

    name = fields.StringField()
    some_dict = wafer.DictField(value_field=wafer.EmbeddedCollection(SimpleModel))


class DictFieldTest(unittest.TestCase):
    def test_simple_dict(self):
        thing_dict = {
            "name": "simple",
            "some_dict": {"key1": "value1", "key2": "value2"},
        }
        thing = SimpleThing.load(thing_dict)
        self.assertEqual(thing.some_dict, thing_dict["some_dict"])

        new_thing_dict = thing.serialize()
        self.assertEqual(new_thing_dict, thing_dict)

    def test_complex_dict_validates(self):
        thing_dict = {
            "name": "simple",
            "some_dict": {
                "key2": [{"some_id": bson.ObjectId()}, {"some_id": "some_string"}]
            },
        }
        thing = ComplexThing.load(thing_dict)
        self.assertEqual(
            [
                ("some_dict.some_id", "Deve ser um ObjectId"),
            ],
            list(thing.enumerate_errors()),
        )
        with self.assertRaises(wafer.ValidationError):
            thing.serialize()

    def test_complex_dict_serializes_and_deserializes(self):
        thing_dict = {
            "name": "simple",
            "some_dict": {
                "key1": [{"some_id": bson.ObjectId()}],
                "key2": [{"some_id": bson.ObjectId()}, {"some_id": bson.ObjectId()}],
            },
        }
        thing = ComplexThing.load(thing_dict)
        self.assertEqual(
            thing.some_dict["key1"][0].some_id,
            thing_dict["some_dict"]["key1"][0]["some_id"],
        )

        new_thing_dict = thing.serialize()
        self.assertEqual(new_thing_dict, thing_dict)


class ExpandoModel(wafer.Model):
    _id = wafer.Field()
    declared_field = wafer.Field()


class ModelLegacyFieldsTest(unittest.TestCase):
    @data.datadriven(
        load=data.Args(loader=ExpandoModel.load),
        from_dict=data.Args(loader=ExpandoModel.from_dict),
    )
    def test_can_handle_extra_fields_with(self, loader):
        expando = loader({"_id": "id", "declared_field": "field", "extra": "extra"})
        self.assertEqual(expando.declared_field, "field")
        with self.assertRaises(AttributeError):
            expando.extra

    def test_serialization_keeps_extra_fields(self):
        expando = ExpandoModel.load(
            {"_id": "id", "declared_field": "field", "extra": "extra"}
        )
        expando.declared_field = "another_value"
        self.assertEqual(
            expando.serialize(),
            {"_id": "id", "declared_field": "another_value", "extra": "extra"},
        )

    def test_drops_fields_created_in_the_object(self):
        expando = ExpandoModel.load(
            {"_id": "id", "declared_field": "field", "extra": "extra"}
        )
        expando.another_extra = "value"
        self.assertEqual(
            expando.serialize(),
            {"_id": "id", "declared_field": "field", "extra": "extra"},
        )

    def test_unsets_legacy_field(self):
        expando = ExpandoModel.load(
            {"_id": "id", "declared_field": "field", "extra": "extra"}
        )
        expando.unset_legacy_field("extra")
        self.assertEqual(expando.serialize(), {"_id": "id", "declared_field": "field"})

    def test_cant_unset_field_declared_in_the_model(self):
        expando = ExpandoModel.load({"_id": "id", "declared_field": "field"})
        with self.assertRaises(ValueError):
            expando.unset_legacy_field("declared_field")

    def test_legacy_fields_are_not_in_json_serialization(self):
        expando1 = ExpandoModel.load(
            {"_id": "id", "declared_field": "field", "extra": "extra"}
        )
        expando2 = ExpandoModel.load({"_id": "id", "declared_field": "field"})
        self.assertEqual(expando1.serialize(json=True), expando2.serialize(json=True))
