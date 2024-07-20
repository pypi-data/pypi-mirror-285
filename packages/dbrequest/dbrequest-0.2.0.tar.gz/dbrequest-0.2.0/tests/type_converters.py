import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'src'))

from datetime import datetime as Datetime, date as Date, timedelta as Timedelta
from unittest import TestCase, main
from unittest.mock import MagicMock

from dbrequest.exceptions import TypeConverterError
from dbrequest.core.type_converters import (
    BaseTypeConverter,
    BaseJsonTypeConverter,
    BoolTypeConverter,
    ListTypeConverter,
    TupleTypeConverter,
    DictTypeConverter,
    DatetimeTypeConverter,
    DateTypeConverter,
    TimedeltaTypeConverter,
)


class Test_BaseTypeConverter(TestCase):
    def test__getter_setter__mock__ok(self) -> None:
        to_database_mock = MagicMock()
        from_database_mock = MagicMock()

        to_database_mock.return_value = 'abc'
        from_database_mock.return_value = 0


        converter = BaseTypeConverter[int, str](
            source_type = int,
            db_type = str,
            to_database_func = to_database_mock,
            from_database_func = from_database_mock,
        )

        self.assertEqual(converter.to_database(123), 'abc')
        to_database_mock.assert_called_once_with(123)

        self.assertEqual(converter.from_database('xxx'), 0)
        from_database_mock.assert_called_once_with('xxx')


    def test__getter_setter__ok(self) -> None:
        converter = BaseTypeConverter[int, int](
            source_type = int,
            db_type = int,
            to_database_func = lambda value: value + 111,
            from_database_func = lambda value: value - 111,
        )

        self.assertEqual(converter.to_database(25), 136)
        self.assertEqual(converter.from_database(136), 25)


class Test_BoolTypeConverter(TestCase):
    def setUp(self) -> None:
        self.converter = BoolTypeConverter()

    def test__type__ok(self) -> None:
        self.assertEqual(self.converter.source_type, bool)
    
    def test__to_database__ok(self) -> None:
        self.assertEqual(self.converter.to_database(True), 1)
        self.assertEqual(self.converter.to_database(False), 0)

    def test__from_database__ok(self) -> None:
        self.assertEqual(self.converter.from_database(1), True)
        self.assertEqual(self.converter.from_database(0), False)

    def test__from_database__wrong_but_working(self) -> None:
        self.assertEqual(self.converter.from_database(2), True)
        self.assertEqual(self.converter.from_database(True), True)
    
    def test__wrong_types__type_converter_error(self) -> None:
        with self.assertRaises(TypeConverterError):
            self.converter.from_database(None)
        
        with self.assertRaises(TypeConverterError):
            self.converter.to_database('asdas')

class Test_ListTypeConverter(TestCase):
    def setUp(self) -> None:
        self.converter = ListTypeConverter()
        self.value = [123, 'abc', True, None]
        self.converted_value = '[123, "abc", true, null]'

    def test__type__ok(self) -> None:
        self.assertEqual(self.converter.source_type, list)

    def test__to_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.to_database(self.value), self.converted_value)

    def test__from_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.from_database(self.converted_value), self.value)

    def test__to_database__empty__ok(self) -> None:
        self.assertEqual(self.converter.to_database([]), '[]')

    def test__from_database__empty__ok(self) -> None:
        self.assertEqual(self.converter.from_database('[]'), [])

class Test_TupleTypeConverter(TestCase):
    def setUp(self) -> None:
        self.converter = TupleTypeConverter()
        self.value = (123, 'abc', True, None)
        self.converted_value = '[123, "abc", true, null]'

    def test__type__ok(self) -> None:
        self.assertEqual(self.converter.source_type, tuple)

    def test__to_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.to_database(self.value), self.converted_value)

    def test__from_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.from_database(self.converted_value), self.value)

    def test__to_database__empty__ok(self) -> None:
        self.assertEqual(self.converter.to_database(()), '[]')

    def test__from_database__empty__ok(self) -> None:
        self.assertEqual(self.converter.from_database('[]'), ())

class Test_DictTypeConverter(TestCase):
    def setUp(self) -> None:
        self.converter = DictTypeConverter()
        self.value = {'123': 'abc', 'xxx': None}
        self.converted_value = '{"123": "abc", "xxx": null}'

    def test__type__ok(self) -> None:
        self.assertEqual(self.converter.source_type, dict)

    def test__to_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.to_database(self.value), self.converted_value)

    def test__from_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.from_database(self.converted_value), self.value)

    def test__to_database__empty__ok(self) -> None:
        self.assertEqual(self.converter.to_database({}), r'{}')

    def test__from_database__empty__ok(self) -> None:
        self.assertEqual(self.converter.from_database(r'{}'), {})

class Test_DatetimeTypeConverter(TestCase):
    def setUp(self) -> None:
        self.converter = DatetimeTypeConverter[int](db_type=int)
        self.value = Datetime.now()
        self.converted_value = int(self.value.timestamp())

    def test__type__ok(self) -> None:
        self.assertEqual(self.converter.source_type, Datetime)

    def test__to_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.to_database(self.value), self.converted_value)

    def test__from_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.from_database(self.converted_value), self.value.replace(microsecond=0))

class Test_DateTypeConverter(TestCase):
    def setUp(self) -> None:
        self.converter = DateTypeConverter()
        self.value = Date.today()
        self.converted_value = self.value.toordinal()

    def test__type__ok(self) -> None:
        self.assertEqual(self.converter.source_type, Date)

    def test__to_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.to_database(self.value), self.converted_value)

    def test__from_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.from_database(self.converted_value), self.value)

class Test_TimedeltaTypeConverter(TestCase):
    def setUp(self) -> None:
        self.converter = TimedeltaTypeConverter[float](db_type=float)
        self.value = Timedelta(days=1, seconds=123.4)
        self.converted_value = 86523.4

    def test__type__ok(self) -> None:
        self.assertEqual(self.converter.source_type, Timedelta)

    def test__to_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.to_database(self.value), self.converted_value)

    def test__from_database__simple__ok(self) -> None:
        self.assertEqual(self.converter.from_database(self.converted_value), self.value)


if __name__ == '__main__':
    main()

