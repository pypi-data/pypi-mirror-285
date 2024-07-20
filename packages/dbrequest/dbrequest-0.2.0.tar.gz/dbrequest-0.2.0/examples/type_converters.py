import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'src'))

from datetime import datetime as Datetime

import dbrequest
from dbrequest import BaseDBRequest, AutoField
from dbrequest.core.type_converters import BaseTypeConverter, DatetimeTypeConverter


dbrequest.init(init_script='examples/type_converters.sql', database_filename='examples/type_converters.db')

class CustomType:
    # `__call__` method will be called if custom
    # `from_database_func` function in `BaseTypeConverter` not set.
    # 
    # Alternative you can define other `from_database_func`. 
    def __call__(value:str):
        return CustomType(value)
    
    def __init__(self, value:str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value

class Model:
    def __init__(self, id:int, custom:CustomType, custom_bool:bool, datetime:Datetime) -> None:
        self.id = id
        self.custom = custom
        self.custom_bool = custom_bool
        self.datetime = datetime

id_field = AutoField('id', int)
custom_field = AutoField('custom', CustomType) # There is not default TypeConverter for this type
custom_bool_field = AutoField('custom_bool', bool) # Default TypeConverter transform bool to int
datetime_field = AutoField('datetime', Datetime) # Default TypeConverter round value for integer seconds

db_request = BaseDBRequest[Model](
    model_type = Model,
    table_name = 'models',
    fields = (
        id_field,
        custom_field,
        custom_bool_field,
        datetime_field,
    ),
    key_fields = (id_field, ),
    type_converters = (
        BaseTypeConverter[CustomType, str](source_type=CustomType, db_type=str), # New converter for custom type
        DatetimeTypeConverter[float](db_type=float), # Overrive defalut Datetime-to-int converter
        BaseTypeConverter[bool, str](
            source_type=bool, db_type=str,
            to_database_func = lambda value: 'T' if value else 'F',
            from_database_func = lambda value: True if value == 'T' else False,
        ) # Override default bool-to-int converter
    )
)

if __name__ == '__main__':
    model = Model(id=123, custom=CustomType('value'), custom_bool=True, datetime=Datetime.now())
    db_request.save(model)
    db_request.load(model)

