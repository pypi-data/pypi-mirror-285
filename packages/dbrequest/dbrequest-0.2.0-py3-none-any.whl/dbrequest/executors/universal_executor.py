from typing import Any

from ..config import config
from ..exceptions import FactoryError
from ..interfaces import ISQLRequest, ITypeConverter, IDatabaseExecutor
from .sqlite_executor import SQLiteExecutor


class UniversalExecutor(IDatabaseExecutor):
    '''`IDatabaseExecutor` implementation with `IDatabaseExecutor` factory depends on global library config.'''
    def __init__(self, database_filename: str | None = None) -> None:
        self._EXECUTORS: dict[config.Executor, IDatabaseExecutor] = {
            'sqlite': SQLiteExecutor(database_filename),
        }
        self._executor: IDatabaseExecutor
   
        if isinstance(config.EXECUTOR, IDatabaseExecutor):
            self._executor = config.EXECUTOR
        else:
            executor = self._EXECUTORS.get(config.EXECUTOR, None)
            if executor is None:
                raise FactoryError(f'Unknown executor "{config.EXECUTOR}"')
            self._executor = executor

    @property
    def supported_types(self) -> tuple[type, ...]:
        return self._executor.supported_types
    
    @property
    def default_type_converters(self) -> tuple[ITypeConverter, ...]:
        return self._executor.default_type_converters
    
    @property
    def internal_row_id_name(self) -> str | None:
        return self._executor.internal_row_id_name

    def start(self, sql_request: ISQLRequest) -> list[tuple[Any]]:
        return self._executor.start(sql_request)
    
    