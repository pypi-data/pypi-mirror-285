__all__ = [
    'BaseTypeConverter',
    'BaseJsonTypeConverter',
    'BoolTypeConverter',
    'ListTypeConverter',
    'TupleTypeConverter',
    'DictTypeConverter',
    'DatetimeTypeConverter',
    'DateTypeConverter',
    'TimedeltaTypeConverter',
]

from typing import override, Callable
from datetime import datetime as Datetime, date as Date, timedelta as Timedelta

import json 

from ..exceptions import TypeConverterError
from ..interfaces import ITypeConverter, SOURCE_TYPE, DB_TYPE


class BaseTypeConverter(ITypeConverter[SOURCE_TYPE, DB_TYPE]):
    '''
    Convert the selected type to a type supported by the database via convert functions in constructor.

    If convert functions are not setted, they are created automatically with simple type transform (like `int('123')`)
    
    Generic[SOURCE_TYPE, DB_TYPE]
    '''
    def __init__(
            self,
            source_type: type[SOURCE_TYPE],
            db_type: type[DB_TYPE],
            *,
            to_database_func: Callable[[SOURCE_TYPE], DB_TYPE] | None = None,
            from_database_func: Callable[[DB_TYPE], SOURCE_TYPE] | None = None,
        ) -> None:

        self._source_type = source_type
        self._db_type = db_type
        self._to_database_func = to_database_func if to_database_func else lambda value: self._db_type.__call__(value)
        self._from_database_func = from_database_func if from_database_func else lambda value: self._source_type.__call__(value)
    
    @property
    @override
    def source_type(self) -> type[SOURCE_TYPE]:
        return self._source_type

    @override
    def to_database(self, value: SOURCE_TYPE) -> DB_TYPE:
        if not isinstance(value, self._source_type):
            raise TypeConverterError(
                f'TypeConverter got unexpected source type {type(value)}. '
                f'Expected: {self._source_type}'
            )

        db_value = self._to_database_func(value)

        if not isinstance(db_value, self._db_type):
            raise TypeConverterError(
                f'`to_database_func` in TypeConverter `{self.__class__.__name__}` '
                f'returned unexpected type {type(db_value)}. ' 
                f'Expected: {self._db_type}.'
            )
        
        return db_value
    
    @override
    def from_database(self, value: DB_TYPE) -> SOURCE_TYPE:
        if not isinstance(value, self._db_type):
            raise TypeConverterError(
                f'TypeConverter got unexpected database type {type(value)}. ' 
                f'Expected: {self._db_type}'
            )
        
        source_value = self._from_database_func(value)

        if not isinstance(source_value, self._source_type):
            raise TypeConverterError(
                f'`from_database_func` in TypeConverter `{self.__class__.__name__}`'
                f'returned unexpected type {type(source_value)}. ' 
                f'Expected: {self._source_type}.'
            )
        
        return source_value


class BaseJsonTypeConverter(BaseTypeConverter[SOURCE_TYPE, str]):
    def __init__(self, source_type:type[SOURCE_TYPE], **json_kwargs) -> None:
        to_database_func = lambda value: json.dumps(value, **json_kwargs)
        from_database_func = lambda value: source_type.__call__(json.loads(value))
        super().__init__(
            source_type = source_type,
            db_type = str,
            to_database_func = to_database_func,
            from_database_func = from_database_func
        )

# Default converters

class BoolTypeConverter(BaseTypeConverter[bool, int]):
    def __init__(self) -> None:
        super().__init__(source_type=bool, db_type=int)

class ListTypeConverter(BaseJsonTypeConverter[list]): 
    def __init__(self, **json_kwargs: dict) -> None:
        super().__init__(source_type=list, **json_kwargs)

class TupleTypeConverter(BaseJsonTypeConverter[tuple]):
    def __init__(self, **json_kwargs: dict) -> None:
        super().__init__(source_type=tuple, **json_kwargs)

class DictTypeConverter(BaseJsonTypeConverter[dict]):
    def __init__(self, **json_kwargs: dict) -> None:
        super().__init__(source_type=dict, **json_kwargs)

class DatetimeTypeConverter(BaseTypeConverter[Datetime, DB_TYPE]):
    def __init__(self, db_type:type[DB_TYPE]) -> None:
        to_database_func = lambda value: db_type.__call__(value.timestamp())
        from_database_func = lambda value: Datetime.fromtimestamp(value)
        super().__init__(
            source_type = Datetime,
            db_type = db_type,
            to_database_func = to_database_func,
            from_database_func = from_database_func
        )

class DateTypeConverter(BaseTypeConverter[Date, int]):
    def __init__(self) -> None:
        to_database_func = lambda value: value.toordinal()
        from_database_func = lambda value: Date.fromordinal(value)
        super().__init__(
            source_type = Date,
            db_type = int,
            to_database_func = to_database_func,
            from_database_func = from_database_func
        )

class TimedeltaTypeConverter(BaseTypeConverter[Timedelta, DB_TYPE]):
    def __init__(self, db_type:type[DB_TYPE]) -> None:
        to_database_func = lambda value: db_type.__call__(value.total_seconds())
        from_database_func = lambda value: Timedelta(seconds=value)
        super().__init__(
            source_type = Timedelta,
            db_type = db_type,
            to_database_func = to_database_func,
            from_database_func = from_database_func
        )
