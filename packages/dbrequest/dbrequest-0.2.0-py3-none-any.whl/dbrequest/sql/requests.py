__all__ = ['SQLInsert', 'SQLSelect', 'SQLUpdate', 'SQLDelete', 'SQLCustom', 'SQLFile']

from typing import Any, override

from ..exceptions import SQLArgsError
from ..interfaces import ISQLRequest
from .properties import TableProp, ColumnsProp, ValuesProp, WhereProp, OrderByProp, LimitProp, All


class SQLInsert(ISQLRequest, TableProp, ColumnsProp, ValuesProp):
    def __init__(
            self,
            table: str,
            *,
            columns: tuple[str, ...],
            values: tuple[Any, ...],
            is_default: bool = False,
            is_replace: bool = False,
        ) -> None:
        TableProp.__init__(self, table)
        ColumnsProp.__init__(self, columns, allow_all=False)
        ValuesProp.__init__(self, values)
        self._is_default = is_default
        self._is_replace = is_replace

    @override
    def get_request(self) -> tuple[str, tuple[Any]] | tuple[str]:
        request: tuple[str, tuple[Any]] | tuple[str]

        command = 'INSERT'
        if self._is_replace:
            command = 'REPLACE'
        
        request_str = f'{command} INTO {self._table} ({self._columns_str}) '

        if self._is_default:
            request_str += 'DEFAULT VALUES;'
            request = (request_str, )
        else:
            request_str += f'VALUES ({self._values_template});'

            request = (request_str, self.values)

        return request
    
class SQLSelect(ISQLRequest, TableProp, ColumnsProp, WhereProp, OrderByProp, LimitProp):
    def __init__(
            self,
            table: str,
            *,
            columns: tuple[str, ...] | All,
            where: str | None = None,
            where_values: tuple[Any, ...] | None = None,
            is_distinct: bool = False,
            order_by: str | None = None,
            limit: int | str | None = None,
        ) -> None:
        TableProp.__init__(self, table)
        ColumnsProp.__init__(self, columns, allow_all=True)
        WhereProp.__init__(self, where, where_values)
        OrderByProp.__init__(self, order_by)
        LimitProp.__init__(self, limit)
        self._is_distinct = is_distinct 
        
    @override
    def get_request(self) -> tuple[str, tuple[Any]] | tuple[str]:
        request: tuple[str, tuple[Any]] | tuple[str]

        distinct = ''
        if self._is_distinct:
            distinct = ' DISTINCT'

        request_str = f'SELECT{distinct} {self._columns_str} FROM {self._table}{self._where_str}{self._order_str}{self._limit_str};'

        if self.where_values is None:
            request = (request_str, )
        else:
            request = (request_str, self.where_values)

        return request

class SQLUpdate(ISQLRequest, TableProp, ColumnsProp, ValuesProp, WhereProp):
    def __init__(
            self,
            table: str,
            *,
            columns: tuple[str, ...],
            values: tuple[Any, ...],
            where: str | None = None,
            where_values: tuple[Any, ...] | None = None,
        ) -> None:
        TableProp.__init__(self, table)
        ColumnsProp.__init__(self, columns, allow_all=False)
        ValuesProp.__init__(self, values)
        WhereProp.__init__(self, where, where_values)

    @override
    def get_request(self) -> tuple[str, tuple[Any]]:
        request: tuple[str, tuple[Any]]

        columns_and_values = ', '.join([f'{column} = ?' for column in self._columns])
        request_str = f'UPDATE {self._table} SET {columns_and_values}{self._where_str};'

        if self.where_values is None:
            request = (request_str, self._values)
        else:
            request = (request_str, self._values + self.where_values)

        return request

class SQLDelete(ISQLRequest, TableProp, WhereProp):
    def __init__(self, table:str, where:str | None = None, where_values: tuple[Any, ...] | None = None) -> None:
        TableProp.__init__(self, table)
        WhereProp.__init__(self, where, where_values)

    @override
    def get_request(self) -> tuple[str, tuple[Any]] | tuple[str]:
        request: tuple[str, tuple[Any]] | tuple[str]
        request_str = f'DELETE FROM {self._table}{self._where_str};'

        if self.where_values is None:
            request = (request_str, )
        else:
            request = (request_str, self.where_values)
        
        return request

class SQLCustom(ISQLRequest):
    def __init__(self, request:str, values:tuple[Any, ...] | None) -> None:
        if request == '':
            raise SQLArgsError('`request_str` parameter can not be empty string.')
        if values == (): 
            raise SQLArgsError('`values` tuple can not be empty. Use `None` for skip `values`.')

        self._request = request
        self._values = values

    @override
    def get_request(self) -> tuple[str, tuple[Any]] | tuple[str]:
        request: tuple[str, tuple[Any]] | tuple[str]
        if self._values:
            request = (self._request, self._values)
        else:
            request = (self._request, )

        return request

class SQLFile(ISQLRequest):
    def __init__(self, file_name:str) -> None:
        with open(file_name, 'r') as file:
            self._request_str = file.read()  

        if ';' not in self._request_str:
            raise SQLArgsError(f'`{file_name}` file doesn\'t contains complete SQL request because ";" not in file.')      

    @override                
    def get_request(self) -> tuple[str]:
        return (self._request_str, )

