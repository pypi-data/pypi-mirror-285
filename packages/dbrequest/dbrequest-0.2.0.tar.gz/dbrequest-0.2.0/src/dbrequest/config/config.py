__all__ = ['init']

from typing import Literal, TypeAlias

from ..exceptions import ConfigError
from ..interfaces import IDatabaseExecutor


Executor: TypeAlias = Literal['sqlite', ]

DATABASE_FILENAME: str = 'database.db'
EXECUTOR: Executor | IDatabaseExecutor = 'sqlite'
LOGGER_NAME: str = 'database'

def init(
        *,
        database_filename: str = 'database.db',
        executor: Executor | IDatabaseExecutor = 'sqlite',
        logger_name: str = 'database',
        init_script: str | None = None,
    ) -> None:

    global DATABASE_FILENAME
    global EXECUTOR
    global LOGGER_NAME

    if database_filename == '': raise ConfigError(f'`database_filename` parameter can not be empty string.')
    if logger_name == '': raise ConfigError(f'`logger_name` parameter can not be empty string.')
    if init_script is not None and init_script == '': raise ConfigError(f'`init_script` parameter can not be empty string.')

    EXECUTOR = executor
    DATABASE_FILENAME = database_filename
    LOGGER_NAME = logger_name

    if init_script is not None:
        from ..executors import UniversalExecutor
        from ..sql import SQLFile

        request = SQLFile(file_name=init_script)

        executor = UniversalExecutor()
        executor.start(request)

