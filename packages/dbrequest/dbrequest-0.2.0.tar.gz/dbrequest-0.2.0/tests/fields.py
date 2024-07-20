import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'src'))

from unittest import TestCase, main
from unittest.mock import MagicMock

from dbrequest.core.fields import BaseField, AutoField


class Model: pass
class FieldType: pass

class Test_BaseField(TestCase):
    def setUp(self):
        self._model = Model()
        self._field_type = FieldType
        self._name = 'test_field'
        self._allowed_none = False
        self._getter_mock = MagicMock()
        self._setter_mock = MagicMock()

        self._base_field = BaseField(
            self._name,
            self._field_type,
            getter=self._getter_mock,
            setter=self._setter_mock,
            allowed_none=self._allowed_none,
        )

    def test__init__type_errors(self):
        with self.assertRaises(TypeError):
            BaseField(123, self._field_type)  # `name` is not str
        with self.assertRaises(TypeError):
            BaseField(self._name, 123)  # `field_type` is not type
        with self.assertRaises(TypeError):
            BaseField(self._name, self._field_type, allowed_none='true')  # `allowed_none` is not bool

    def test__value_property__ok(self):
        value = FieldType()
        self._base_field.value = value

        self.assertEqual(self._base_field.value, value)

    def test__value_property__type_error(self):
        with self.assertRaises(TypeError):
            self._base_field.value = 'incorrect_type'
        
        if not self._allowed_none:
            with self.assertRaises(TypeError):
                self._base_field.value = None 

    def test__get_value_from_object__ok(self):
        value = FieldType()
        self._getter_mock.return_value = value
        
        self._base_field.get_value_from_object(self._model)
        
        self.assertEqual(self._base_field.value, value)
        self._getter_mock.assert_called_once_with(self._model)
        self._setter_mock.assert_not_called()

    def test__set_value_to_object__ok(self):
        value = FieldType()
        self._base_field.value = value

        self._base_field.set_value_to_object(self._model)
        
        self._setter_mock.assert_called_once_with(self._model, value)
        self._getter_mock.assert_not_called()


class FakeModel:
    def __init__(self) -> None:
        self.simple_field: int = 123
        self._property_field: str = 'abc'

    @property
    def property_field(self) -> str:
        return self._property_field
    
    @property_field.setter
    def property_field(self, value:str):
        self._property_field = value

class Test_AutoField(TestCase):
    def setUp(self) -> None:
        self._model = FakeModel()

        self._simple_field = AutoField[FakeModel, int]('simple_field', int)
        self._property_field = AutoField[FakeModel, str]('property_field', str)

    def test__getter__ok(self):
        self._simple_field.get_value_from_object(self._model)
        self._property_field.get_value_from_object(self._model)

        self.assertEqual(self._model.simple_field, self._simple_field.value)
        self.assertEqual(self._model.property_field, self._property_field.value)

    def test__setter__ok(self): 
        value_1 = 456
        value_2 = 'xyz'

        self._simple_field.value = value_1
        self._property_field.value = value_2

        self._simple_field.set_value_to_object(self._model)
        self._property_field.set_value_to_object(self._model)

        self.assertEqual(self._model.simple_field, value_1)
        self.assertEqual(self._model.property_field, value_2)

    def test__getter__no_attribute(self): 
        field = AutoField('unexisting_attribute', bool)

        with self.assertRaises(AttributeError):
            field.get_value_from_object(self._model)


if __name__ == '__main__':
    main()

