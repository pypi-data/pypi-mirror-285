__all__ = [
    'ISQLRequest',
    'ITypeConverter',
    'IDatabaseExecutor',
    'IField',
    'IDBRequest',
    'SOURCE_TYPE',
    'DB_TYPE',
    'MODEL',
    'FIELD_TYPE',
]

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic
from types import MethodType


class ISQLRequest(ABC):
    '''Represent some SQL query.'''

    @abstractmethod
    def get_request(self) -> tuple[str, tuple[Any]] | tuple[str]:
        '''Compile SQL query string.'''


SOURCE_TYPE = TypeVar('SOURCE_TYPE')
DB_TYPE = TypeVar('DB_TYPE')

class ITypeConverter(ABC, Generic[SOURCE_TYPE, DB_TYPE]):
    '''
    Convert the selected type to a type supported by the database, and vice versa.
    
    Generic[SOURCE_TYPE, DB_TYPE]
    '''
    @property
    @abstractmethod
    def source_type(self) -> type[SOURCE_TYPE]: pass

    @abstractmethod
    def to_database(self, value:SOURCE_TYPE) -> DB_TYPE: pass

    @abstractmethod
    def from_database(self, value:DB_TYPE) -> SOURCE_TYPE: pass
    

class IDatabaseExecutor(ABC):
    '''Execute SQL requests (`ISQLRequest`) using the specific database library.'''

    @abstractmethod
    def __init__(self, database_filename: str | None = None) -> None: pass

    @property
    @abstractmethod
    def supported_types(self) -> tuple[type, ...]:
        '''All types supported by specific database.'''

    @property
    @abstractmethod
    def default_type_converters(self) -> tuple[ITypeConverter, ...]:
        '''`ITypeConverter` objects for some basic python types not supported by default.'''

    @property
    @abstractmethod
    def internal_row_id_name(self) -> str | None:
        '''Name of hiden column contents unique internal row id or None if not applicable for specific database.'''

    @abstractmethod
    def start(self, sql_request:ISQLRequest) -> list[tuple[Any]]: pass


MODEL = TypeVar('MODEL')
FIELD_TYPE = TypeVar('FIELD_TYPE')

class IField(ABC, Generic[MODEL, FIELD_TYPE]):
    '''
    Represent a persisted field (attribute) of a model class.
    - Store part of table schema (column name, type and ability to be `None`).
    - Retrieve value of their model object.
    - Write value to model object.

    Generic[MODEL, FIELD_TYPE]
    '''
    
    @property
    @abstractmethod
    def name(self) -> str:
        '''Get name of the column in the database table.'''

    @property
    @abstractmethod
    def type(self) -> type[FIELD_TYPE]: 
        '''Get type of the database table column.'''

    @property
    @abstractmethod
    def value(self) -> FIELD_TYPE: pass

    @value.setter
    @abstractmethod
    def value(self, value:FIELD_TYPE) -> None: pass

    @abstractmethod
    def get_value_from_object(self, object:MODEL) -> None:
        '''Retrieve value of their model object.'''

    @abstractmethod
    def set_value_to_object(self, object:MODEL) -> None:
        '''Write value to model object.'''


class IDBRequest(ABC, Generic[MODEL]):
    '''
    High-level class that represents most important table operations in a database.
    - save
    - load
    - update
    - delete
    - load_all 
    
    Generic[MODEL]
    '''

    @property
    @abstractmethod
    def model_type(self) -> type[MODEL]:
        '''Get model class.'''
    
    @abstractmethod
    def save(self, object:MODEL) -> None:
        '''Serialize and store input object to database.'''

    @abstractmethod
    def load(self, object:MODEL) -> bool:
        '''
        Load object from database.
        - Search by passed values in the object.
        - Write values to the passed object.
        - Use the first one if more than one is found.
        - If object not found in database, return `False`.
        '''
    
    @abstractmethod
    def update(self, object:MODEL) -> None:
        '''Find and overwrite the old values of an object in the database with the current values.'''

    @abstractmethod
    def delete(self, object:MODEL) -> None:
        '''Find and delete object from database table.'''
    
    @abstractmethod
    def load_all(
        self,
        object_sample: MODEL,
        *,
        limit: int | None = None,
        reverse: bool = False,
        sort_by: IField | str | None = None
    ) -> list[MODEL]:
        '''
        Load all objects that meet the conditions.

        Args: 
            `object_sample`: Some instance of the model class. It will be used to clone objects.   
            `limit`: Maximum number of objects to load.
            `reverse`: Reverse result list.
            `sort_by`: Parameter by which sorting will be performed. It can be just name or IField object.
        Returns:
            List of new model objects.
        '''
    
