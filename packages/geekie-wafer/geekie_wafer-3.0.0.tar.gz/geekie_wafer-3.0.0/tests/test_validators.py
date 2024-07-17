# coding: utf-8
import datadriven as data
import six
import unittest

import wafer.validators


class ValidatorsTest(unittest.TestCase):
    longMessage = True

    def test_required_accepts_falsy_values(self):
        self.assertValid(0, according_to=wafer.validators.required())
        self.assertValid(False, according_to=wafer.validators.required())
        self.assertValid([], according_to=wafer.validators.required())
        self.assertValid("", according_to=wafer.validators.required())

    def test_required_doesnt_accept_none(self):
        self.assertInvalid(
            None, according_to=wafer.validators.required(), because="Obrigatório"
        )
        self.assertInvalid(
            None,
            according_to=wafer.validators.required(msg="I've told you so"),
            because="I've told you so",
        )

    def test_integer_accepts_valid_values(self):
        self.assertValid(
            None,
            according_to=wafer.validators.integer(),
            msg="integer validator should accept None",
        )
        self.assertValid(0, according_to=wafer.validators.integer())
        self.assertValid(-1, according_to=wafer.validators.integer())
        self.assertValid(10, according_to=wafer.validators.integer())

    def test_integer_rejects_bad_values(self):
        self.assertInvalid(
            1.0, according_to=wafer.validators.integer(), because="Deve ser um inteiro"
        )
        self.assertInvalid(
            "1", according_to=wafer.validators.integer(), because="Deve ser um inteiro"
        )

    def test_greater_than_accepts_valid_values(self):
        self.assertValid(None, according_to=wafer.validators.greater_than(0))
        self.assertValid(1.1, according_to=wafer.validators.greater_than(1.0))
        self.assertValid(1, according_to=wafer.validators.greater_than(0))

    def test_greater_than_rejects_bad_values(self):
        self.assertInvalid(
            0,
            according_to=wafer.validators.greater_than(0, msg="must be positive"),
            because="must be positive",
        )
        self.assertInvalid(
            0,
            according_to=wafer.validators.greater_than(0),
            because="Deve ser maior que 0",
        )
        self.assertInvalid(
            -1,
            according_to=wafer.validators.greater_than(0),
            because="Deve ser maior que 0",
        )

    def test_less_than_accepts_valid_values(self):
        self.assertValid(None, according_to=wafer.validators.less_than(0))
        self.assertValid(0.9, according_to=wafer.validators.less_than(1.0))
        self.assertValid(1, according_to=wafer.validators.less_than(2))

    def test_less_than_rejects_bad_values(self):
        self.assertInvalid(
            0,
            according_to=wafer.validators.less_than(0, msg="must be negative"),
            because="must be negative",
        )
        self.assertInvalid(
            0,
            according_to=wafer.validators.less_than(0),
            because="Deve ser menor que 0",
        )
        self.assertInvalid(
            1,
            according_to=wafer.validators.less_than(0),
            because="Deve ser menor que 0",
        )

    def test_matches_regex_accepts_valid_values(self):
        self.assertValid(
            None, according_to=wafer.validators.matches_regex(r"abrakadabra")
        )
        self.assertValid(
            "pikachu",
            according_to=wafer.validators.matches_regex(r"(pikachu|pichu|raichu)"),
        )

    def test_matches_regex_rejects_bad_values(self):
        self.assertInvalid(
            " pikachu",
            according_to=wafer.validators.matches_regex(r"pikachu"),
            because="Valor inválido",
            msg="Validator must check for whole string match",
        )
        self.assertInvalid(
            "pikachu ",
            according_to=wafer.validators.matches_regex(r"pikachu"),
            because="Valor inválido",
            msg="Validator must check for whole string match",
        )
        self.assertInvalid(
            "bulbasaur",
            according_to=wafer.validators.matches_regex(
                r"pikachu", msg="It's not Pikachu"
            ),
            because="It's not Pikachu",
        )

    def test_non_empty_string(self):
        self.assertValid("foo", according_to=wafer.validators.non_empty_string())
        self.assertInvalid("", according_to=wafer.validators.non_empty_string())

    @data.datadriven(
        none=data.Args(None),
        integer=data.Args("10"),
        negative_integer=data.Args("-10"),
        positive_integer=data.Args("+10"),
        integer_with_dot=data.Args("10."),
        decimal_without_integer_part=data.Args(".34"),
        decimal_with_integer_part=data.Args("0.34"),
        float=data.Args("50.3"),
        negative_float=data.Args("-70.3"),
    )
    def test_number_str_accepts(self, value):
        self.assertValid(value, according_to=wafer.validators.number_str())

    @data.datadriven(
        text=data.Args("aaa"),
        begins_with_non_number=data.Args("a10"),
        ends_with_non_number=data.Args("10.3a"),
        portuguese_float=data.Args("30,5"),
        number_with_dash_in_the_middle=data.Args("70-3"),
        number_with_two_dots=data.Args("7.3.5"),
        empty=data.Args(""),
        number_with_multiple_signals=data.Args("+-70"),
    )
    def test_number_str_rejects(self, value):
        self.assertInvalid(
            value,
            according_to=wafer.validators.number_str(),
            because=wafer.validators.NUMBER,
        )

    @data.datadriven(
        equal_min=data.Args("10", 10, 11),
        equal_max=data.Args("11", 10, 11),
        between=data.Args("11", 10, 12),
        equal_min_when_negative=data.Args("-10", -10, -9),
        equal_max_when_negative=data.Args("-9", -10, -9),
    )
    def test_number_str_with_inclusive_limits_accepts(self, value, lower, upper):
        self.assertValid(
            value,
            according_to=wafer.validators.number_str(
                min_range_inclusive=lower, max_range_inclusive=upper
            ),
        )

    @data.datadriven(
        less_than_min=data.Args("9.99", 10, 11),
        greater_than_max=data.Args("11.1", 10, 11),
        less_than_min_when_negative=data.Args("-10.1", -10, -9),
        greater_than_max_when_negative=data.Args("-8.9", -10, -9),
    )
    def test_number_str_with_inclusive_limits_rejects(self, value, lower, upper):
        self.assertInvalid(
            value,
            according_to=wafer.validators.number_str(
                min_range_inclusive=lower, max_range_inclusive=upper
            ),
        )

    @data.datadriven(
        between=data.Args("12", 10, 13),
        between_when_negative=data.Args("-12", -13, -10),
    )
    def test_number_str_with_exclusive_limits_accepts(self, value, lower, upper):
        self.assertValid(
            value,
            according_to=wafer.validators.number_str(
                min_range_exclusive=lower, max_range_exclusive=upper
            ),
        )

    @data.datadriven(
        equal_min=data.Args("10", 10, 11),
        equal_max=data.Args("11", 10, 11),
        less_than_min=data.Args("9.99", 10, 11),
        greater_than_max=data.Args("11.1", 10, 11),
        equal_min_when_negative=data.Args("-10", -10, -9),
        equal_max_when_negative=data.Args("-9", -10, -9),
        less_than_min_when_negative=data.Args("-10.1", -10, -9),
        greater_than_max_when_negative=data.Args("-8.9", -10, -9),
    )
    def test_number_str_with_exclusive_limits_rejects(self, value, lower, upper):
        self.assertInvalid(
            value,
            according_to=wafer.validators.number_str(
                min_range_exclusive=lower, max_range_exclusive=upper
            ),
        )

    @data.datadriven(
        float=data.Args(0.1),
        int=data.Args(1),
        none=data.Args(None),
    )
    def test_number_validator_accepts(self, value):
        self.assertValid(value, according_to=wafer.validators.number())

    def test_number_validator_rejects(self):
        self.assertInvalid("", according_to=wafer.validators.number())
        self.assertInvalid("a", according_to=wafer.validators.number())

    @data.datadriven(
        str=data.Args("a"), number=data.Args(1), object=data.Args(object())
    )
    def test_unicode_validation_rejects(self, value):
        if six.PY3 and value == "a":
            raise unittest.SkipTest("All strings are unicode in Python 3")
        self.assertInvalid(value, according_to=wafer.validators.unicode_string())

    @data.datadriven(
        unicode=data.Args("ãçí"),
        none=data.Args(None),
    )
    def test_unicode_validation_accpets_unicode(self, value):
        self.assertValid(value, according_to=wafer.validators.unicode_string())

    @data.datadriven(
        zero=data.Args(value="0", allowed_values=["0", "1"]),
        one=data.Args(value="1", allowed_values=["0", "1"]),
        none=data.Args(value=None, allowed_values=["0", "1"]),
    )
    def test_in_list_valid(self, value, allowed_values):
        self.assertValid(value, according_to=wafer.validators.in_list(allowed_values))

    @data.datadriven(
        zero=data.Args(value="0", allowed_values=["000", "111"]),
        one=data.Args(value="1", allowed_values=["3", "-"]),
    )
    def test_in_list_invalid(self, value, allowed_values):
        self.assertInvalid(value, according_to=wafer.validators.in_list(allowed_values))

    def assertValid(self, value, according_to, msg=None):
        errors = [error for error in according_to(value)]
        self.assertEqual([], errors, msg=msg or "{value} is valid".format(value=value))

    def assertInvalid(self, value, according_to, because=None, msg=None):
        errors = [error for error in according_to(value)]
        if because:
            self.assertEqual(
                [because], errors, msg=msg or "{value} is invalid".format(value=value)
            )
        else:
            self.assertTrue(errors)


class FieldValidationTest(unittest.TestCase):
    longMessage = True

    def test_unrestricted_field_validation(self):
        six.assertCountEqual(self, [], wafer.Field().validate("something"))

    def test_field_validation(self):
        field = wafer.Field(
            validators=[
                wafer.validators.required(),
                wafer.validators.integer(),
                wafer.validators.greater_than(2),
            ]
        )
        six.assertCountEqual(self, [], field.validate(3), "3 is valid")
        six.assertCountEqual(
            self,
            ["Deve ser um inteiro", "Deve ser maior que 2"],
            field.validate(1.0),
            "1.0 has two validation errors",
        )

    def test_embedded_collection_validation(self):
        field = wafer.EmbeddedCollection(validators=[wafer.validators.integer()])
        six.assertCountEqual(self, [], field.validate(None))
        six.assertCountEqual(self, [], field.validate([1, 2, 3]))
        six.assertCountEqual(
            self,
            ["Element at 1: Deve ser um inteiro", "Element at 3: Deve ser um inteiro"],
            field.validate([1, "2", 3, "4", 5]),
        )


class ModelValidationTest(unittest.TestCase):
    longMessage = True

    class Model(wafer.Model):
        name = wafer.Field(validators=[wafer.validators.required()])
        age = wafer.Field(
            validators=[
                wafer.validators.required(),
                wafer.validators.integer(),
                wafer.validators.greater_than(17),
            ]
        )

    def test_validate_and_enumerate_errors(self):
        valid_model = self.Model(name="John", age=20)
        six.assertCountEqual(self, [], valid_model.enumerate_errors())
        valid_model.validate()  # Should not raise exception

        invalid_model = self.Model(age=10.0)
        invalid_model_errors = [
            ("name", "Obrigatório"),
            ("age", "Deve ser um inteiro"),
            ("age", "Deve ser maior que 17"),
        ]
        six.assertCountEqual(
            self, invalid_model_errors, invalid_model.enumerate_errors()
        )
        with self.assertRaises(wafer.ValidationError) as e:
            invalid_model.validate()

        six.assertRegex(self, repr(e.exception), r"(name, age)|(age, name)")
        six.assertCountEqual(self, invalid_model_errors, e.exception.errors)

    def test_validates_on_serialization(self):
        model = self.Model()
        model.age = 10

        with self.assertRaises(wafer.ValidationError):
            model.serialize()
