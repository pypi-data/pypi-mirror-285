import pytest

import wafer.utils


class ConstantAlias(object):
    prop = 1
    prop_alias = wafer.utils.alias("prop")


class PropertyAlias(object):
    _prop = 1

    @property
    def prop(self):
        return self._prop

    @prop.setter
    def prop(self, value):
        self._prop = value

    prop_alias = wafer.utils.alias("prop")


@pytest.mark.parametrize("Model", [ConstantAlias, PropertyAlias])
def test_alias(Model):
    model = Model()

    assert model.prop == 1
    assert model.prop_alias == 1

    model.prop = 2
    assert model.prop == 2
    assert model.prop_alias == 2

    model.prop_alias = 3
    assert model.prop == 3
    assert model.prop_alias == 3
