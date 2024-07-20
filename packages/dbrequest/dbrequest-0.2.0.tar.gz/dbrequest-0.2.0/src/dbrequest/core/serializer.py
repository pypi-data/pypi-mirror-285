__all__ = ['Serializer']

from typing import Any, Generic

from ..exceptions import InternalError
from ..interfaces import ITypeConverter, IField, MODEL


class Serializer(Generic[MODEL]):
    '''
    Internal library class.

    - Retrieve values from `IField` objects and prepare for writing to the database.
    - Prepare values from the database for saving to `IField` objects.
    - Convert unsupported values using `ITypeConverter` objects.

    Generic[MODEL]
    '''
    def __init__(
            self,
            fields: tuple[IField, ...],
            supported_types: tuple[type, ...],
            type_converters: tuple[ITypeConverter, ...],
        ) -> None:
        '''
        Class constructor.

        Args:
        `fields`: `IField` objects in the order in which parameters are declared in the database
        `supported_types`: types supported by a specific database
        `type_converters`: `ITypeConverter` objects for converting unsupported types
        '''
        self._fields = fields
        self._supported_types = supported_types
        self._type_converters = type_converters
    
    @property
    def fields(self) -> tuple[IField, ...]:
        '''Return current `IField` objects.'''
        return self._fields

    def get_params_and_values(self, object:MODEL) -> tuple[tuple[str, ...], tuple[Any, ...]]:
        '''Return prepared parameters and values tuples from input object for writing to the database.'''
        params_list: list[str] = [field.name for field in self._fields]
        values_list: list[Any] = []

        for field in self._fields:
            field.get_value_from_object(object)
            value = self._get_field_value(field)
            values_list.append(value)
        
        return tuple(params_list), tuple(values_list)
    
    def set_values_to_object(self, object:MODEL, values:tuple[Any]) -> None:
        '''Prepare and set values from database to object.'''
        if len(self._fields) != len(values):
            raise InternalError(f'Number of values ({len(self._fields)}) not equal to number of fields ({len(values)}).')
        
        data: dict[IField, Any] = dict(zip(self._fields, values))

        for field in data.keys():
            self._set_field_value(field, data[field])
            field.set_value_to_object(object)

    def _get_field_value(self, field:IField) -> Any:
        '''Retrieve value from the `IField` object and convert if necessary.'''
        value = field.value
        if not type(value) in self._supported_types:
            for converter in self._type_converters:
                if issubclass(field.type, converter.source_type):
                    if not value is None:
                        value = converter.to_database(value)
                    break
            else:
                raise TypeError(
                    f'Object type {type(value)} not supported by current database. '
                    'You can set a custom `DBTypeConverter` for this type.'
                )

        return value

    def _set_field_value(self, field:IField, value:Any) -> None:
        '''Set database value to the `IField` object and convert if necessary.'''
        if not field.type in self._supported_types:
            for converter in self._type_converters:
                if issubclass(converter.source_type, field.type):
                    if not value is None:
                        value = converter.from_database(value)
                    break
            else:
                raise TypeError(
                    f'Can not convert value type {type(value)} '
                    f'to required field type {field.type}. '
                    'You can set a custom `DBTypeConverter` for this type.'
                )
        
        field.value = value


