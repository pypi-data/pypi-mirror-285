import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from unittest import TestCase, main
from typing import Any

from src.dbrequest import BaseDBRequest, AutoField
from src.dbrequest.interfaces import IDatabaseExecutor, ISQLRequest, ITypeConverter


class User():
    def __init__(self, id: int | None = None, username: str | None = None) -> None:
        self.id = id
        self.username = username

class FakeExecutor(IDatabaseExecutor):
    def __init__(self, database_filename: str | None = None) -> None:
        self._request: tuple[str, tuple[Any, ...]]

    def start(self, sql_request:ISQLRequest) -> list[tuple[Any]]:
        self._request = sql_request.get_request()

    @property
    def last_request(self) -> tuple[str, tuple[Any, ...]]:
        return self._request

    @property
    def supported_types(self) -> tuple[type, ...]:
        return (int, str)

    @property
    def default_type_converters(self) -> tuple[ITypeConverter, ...]:
        return ()

class Test_SQLInjection(TestCase):
    def setUp(self) -> None:
        self._executor = FakeExecutor()

        self._key_fields = (
            AutoField[User, int]('id', int, allowed_none=True),
            AutoField[User, str]('username', str),
        )

        self._database = BaseDBRequest[User](
            model_type = User,
            table_name = 'users',
            fields = self._key_fields,
            key_fields = self._key_fields,
            executor = self._executor
        )

    def test(self) -> None:
        user = User(id=1, username="username'; DROP TABLE users; --")
        self._database.update(user)

        request = self._executor.last_request
        expected = ('UPDATE users SET id = ?, username = ? WHERE id = ?;', (1, "username'; DROP TABLE users; --", 1))

        self.assertEqual(request, expected)


if __name__ == '__main__':
    main()





