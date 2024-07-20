__all__ = ['BaseDBRequest']

from typing import Any
from types import MethodType

from ..exceptions import SchemaError
from ..interfaces import IDatabaseExecutor, ITypeConverter, IDBRequest, IField, MODEL
from ..executors import UniversalExecutor
from ..sql.requests import SQLInsert, SQLSelect, SQLUpdate, SQLDelete
from .serializer import Serializer 


class BaseDBRequest(IDBRequest[MODEL]):
    '''
    High-level class that represents most important table operations in a database.
    - save
    - load
    - update
    - delete
    - load_all 
    
    Generic[MODEL]
    '''
    def __init__(
            self,
            model_type: type[MODEL],
            table_name: str,
            fields: tuple[IField, ...],
            key_fields: tuple[IField, ...],
            *,
            executor: IDatabaseExecutor = UniversalExecutor(),
            type_converters: tuple[ITypeConverter, ...] = (),
            replace_type_converters: bool = False,
        ) -> None:
        '''
        Class constructor.

        Args:
            `model_type`: Model class.
            `table_name`: Name of the table in database.
            `fields`: `IField` objects in the same order that the columns in table.
            `key_fields`: Unique `IFields` objects, that can be used as object UID.
            `executor`: Set specific `IDatabaseExecutor` only for that DBRequest instance.
            `type_converters`: Tuple of `ITypeConverter` objects used for convert unsupported types. 
                Passed converters override defaults (it check before default converters).
            `replace_type_converters`: Set `True` for drop default `ITypeConverters` object.
        '''

        self._model_type = model_type
        self._table_name = table_name
        self._executor = executor
        self._key_fields = key_fields

        if not replace_type_converters:
            type_converters = type_converters + executor.default_type_converters

        self._serializer = Serializer[MODEL](
            fields = fields,
            supported_types = executor.supported_types,
            type_converters = type_converters,
        )

        if len(key_fields) == 0:
            raise SchemaError('`key_fields` must contents at least one element.')
        for key_field in key_fields:
            if key_field.name not in [field.name for field in fields]:
                raise SchemaError(f'Key field "{key_field.name}" not found in `fields` tuple.')

    @property
    def model_type(self) -> type[MODEL]:
        return self._model_type

    def save(self, object:MODEL) -> None:
        self._check_type(object)
        
        params, values = self._serializer.get_params_and_values(object)

        request = SQLInsert(self._table_name, columns=params, values=values)
        self._executor.start(request)
        
    def load(self, object:MODEL) -> bool:
        self._check_type(object)
        is_found = False
        condition, condition_values = self._get_key_field_condition(object)
        
        request = SQLSelect(self._table_name, columns='*', where=condition, where_values=condition_values, limit=1)
        response = self._executor.start(request)

        if len(response) > 0:
            is_found = True
            values = response[0]
            self._serializer.set_values_to_object(object, values)
        
        return is_found
        
    def update(self, object:MODEL) -> None:
        self._check_type(object)
        condition, condition_values = self._get_key_field_condition(object)
        
        params, values = self._serializer.get_params_and_values(object)

        request = SQLUpdate(self._table_name, columns=params, values=values, where=condition, where_values=condition_values)
        self._executor.start(request)
        
    def delete(self, object:MODEL) -> None:
        self._check_type(object)
        condition, condition_values = self._get_key_field_condition(object)
        
        request = SQLDelete(self._table_name, where=condition, where_values=condition_values)
        self._executor.start(request)

    def load_all(self, object_sample:MODEL, *, limit:int | None=None, reverse:bool=False, sort_by:IField | str | None=None) -> list[MODEL]:
        self._check_type(object_sample)
        objects_list = []

        order_by = None

        if sort_by is not None:
            sort_field_name = None
            if isinstance(sort_by, IField):
                sort_field_name = sort_by.name
            elif isinstance(sort_by, str):
                sort_field_name = sort_by
            else:
                raise TypeError(f'The `sort_by` parameter might be IField, str` or MetodType, not {type(sort_by)}.')

            if sort_field_name in [field.name for field in self._serializer.fields]:
                order_by = sort_field_name
            else:
                raise SchemaError(f'Unable to sort by field name "{sort_field_name}": field not exist.')
        else:
            if limit is not None:
                order_by = self._executor.internal_row_id_name if self._executor.internal_row_id_name else self._key_fields[0].name

        if order_by is not None:
            if reverse:
                order_by += ' DESC' 
        
        request = SQLSelect(self._table_name, columns='*', order_by=order_by, limit=limit)
        table = self._executor.start(request)
        
        for row in table:
            object = type(object_sample)()
            self._serializer.set_values_to_object(object, row)
            objects_list.append(object)

        return objects_list

    def _check_type(self, object:MODEL) -> None:
        if not isinstance(object, self._model_type):
            raise TypeError(f'Got unexpected model object type {type(object)}. Expected: {self._model_type}.')

    def _get_key_field_condition(self, object:MODEL) -> tuple[str, tuple[Any, ...]]:
        condition = ''
        values: tuple[Any, ...] = ()
        for field in self._key_fields:
            try:
                field.get_value_from_object(object)
            except ValueError: pass
            else:
                if field.value is not None:
                    condition = f'{field.name} = ' + '{}'
                    values = (field.value, )
                    break
        else:
            raise SchemaError(f'Unable to compose SQL condition: all key fields are empty (None type).')

        return condition, values
        