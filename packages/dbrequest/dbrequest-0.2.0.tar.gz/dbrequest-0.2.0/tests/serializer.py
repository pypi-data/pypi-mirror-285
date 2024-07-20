import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'src'))

from unittest import TestCase, main
from unittest.mock import MagicMock

from dbrequest.interfaces import ITypeConverter, IField, FIELD_TYPE
from dbrequest.core.serializer import Serializer


class FakeModel: pass

class FakeField(IField[FakeModel, FIELD_TYPE]):
    def __init__(self, name:str, value:FIELD_TYPE, field_type:type[FIELD_TYPE]) -> None:
        self._name = name
        self._value = value
        self._field_type = field_type

        self.get_mock = MagicMock()
        self.set_mock = MagicMock()

    @property
    def name(self) -> str: return self._name

    @property
    def type(self) -> type[FIELD_TYPE]: return self._field_type

    @property
    def value(self) -> FIELD_TYPE: return self._value

    @value.setter
    def value(self, value:FIELD_TYPE) -> None: self._value = value

    def get_value_from_object(self, object: FakeModel) -> None:
        self.get_mock(object)

    def set_value_to_object(self, object: FakeModel) -> None:
        self.set_mock(object)
        
class FakeIntTypeConverter(ITypeConverter[int, str]):
    def __init__(self) -> None:
        self.to_mock = MagicMock()
        self.from_mock = MagicMock()
    
    @property
    def source_type(self) -> type[int]: return int
    
    def to_database(self, value: int) -> str:
        self.to_mock(value)
        return str(value)
    
    def from_database(self, value: str) -> int:
        self.from_mock(value)
        return int(value)

class Test_Serializer(TestCase):
    def setUp(self):
        self._field_one = FakeField[int]('field_one', 123, int)
        self._field_two = FakeField[str]('field_two', 'abc', str)
        self._converter = FakeIntTypeConverter()
        self._model = FakeModel()
        self._result = (('field_one', 'field_two'), ('123', 'abc'))

        self._serializer = Serializer[FakeModel](
            fields = (self._field_one, self._field_two),
            supported_types = (str, ),
            type_converters = (self._converter, )
        )

    def test__ok(self):
        with self.subTest('get'):
            result = self._serializer.get_params_and_values(self._model)
            self.assertEqual(result, self._result)

            self._field_one.get_mock.assert_called_once_with(self._model)
            self._field_two.get_mock.assert_called_once_with(self._model)
            self._converter.to_mock.assert_called_once_with(123)

        with self.subTest('set'):
            self._serializer.set_values_to_object(self._model, self._result[1])

            self.assertEqual(self._field_one.value, 123)
            self.assertEqual(self._field_two.value, 'abc')

            self._field_one.set_mock.assert_called_once_with(self._model)
            self._field_two.set_mock.assert_called_once_with(self._model)
            self._converter.from_mock.assert_called_once_with('123')


if __name__ == '__main__':
    main()

