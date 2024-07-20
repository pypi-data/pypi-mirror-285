import sqlite3
import logging
from typing import Any

from ..config import config
from ..interfaces import ITypeConverter, ISQLRequest, IDatabaseExecutor
from ..sql import SQLFile
from ..core.type_converters import (
    BoolTypeConverter, ListTypeConverter, TupleTypeConverter, DictTypeConverter,
    DatetimeTypeConverter, DateTypeConverter, TimedeltaTypeConverter,
)


class SQLiteExecutor(IDatabaseExecutor):
    def __init__(self, database_filename: str | None = None) -> None:
        self._logger = logging.getLogger(config.LOGGER_NAME)
        self._database_filename = database_filename

    @property
    def supported_types(self) -> tuple[type, ...]:
        return (int, float, str, bytes, type(None))
    
    @property
    def default_type_converters(self) -> tuple[ITypeConverter, ...]:
        return (
            BoolTypeConverter(),
            ListTypeConverter(),
            TupleTypeConverter(),
            DictTypeConverter(),
            DatetimeTypeConverter[int](db_type=int),
            DateTypeConverter(),
            TimedeltaTypeConverter[int](db_type=int),
        )
    
    @property
    def internal_row_id_name(self) -> str:
        return 'rowid'
    
    def start(self, sql_request:ISQLRequest) -> list[tuple[Any]]:
        if not isinstance(sql_request, ISQLRequest):
            raise TypeError(type(sql_request))
        
        database_filename = config.DATABASE_FILENAME if self._database_filename is None else self._database_filename
        connection = None
        response: list[Any] = []

        try:
            connection = sqlite3.connect(database_filename)
            cursor = connection.cursor()

            request = sql_request.get_request()
            request_log = '\n'.join(str(line) for line in request)
            self._logger.debug(f'Running request:\n{request_log}')
            
            if isinstance(sql_request, SQLFile):
                cursor.executescript(request[0])
            else:
                cursor.execute(*request)
            
            
            if request[0].split()[0].upper() == 'SELECT':
                response = cursor.fetchall()
            
            connection.commit()

            cursor.close()

        except sqlite3.Error as error:
            self._logger.exception(error)
            raise

        finally:
            if connection is not None:
                self._logger.debug(f'Lines changed: {connection.total_changes}')
                connection.close()
        
        return response
        
