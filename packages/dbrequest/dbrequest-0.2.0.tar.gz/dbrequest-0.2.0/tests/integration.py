import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

import logging
from unittest import TestCase, main
from datetime import datetime as Datetime

from src.dbrequest import init, BaseDBRequest, AutoField
from src.dbrequest.core.type_converters import BaseTypeConverter


DATABASE_FILE = 'tests/integration.sqlite'
logging.basicConfig(level=logging.DEBUG)

def delete_database():
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)    

class CustomType: 
    def __call__(value):
        return CustomType(value)
    
    def __init__(self, value:str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value
    

class User():
    def __init__(self, id: int | None = None, username: str | None = None) -> None:
        self.id = id
        self.username = username
        self.is_sign_in: bool = False
        self.datetime: Datetime | None = None
        self.ratio: float = 0.0
        self.hash: bytes | None = None
        self.custom: CustomType | None = None

    def __str__(self) -> str:
        return f'{self.id = }, {self.username = }'


class Test_Integration(TestCase):
    def setUp(self) -> None:
        delete_database()
        init(database_filename=DATABASE_FILE, init_script='tests/integration.sql')

        self._key_fields: tuple[AutoField] = (
            AutoField[User, int]('id', int, allowed_none=True),
            AutoField[User, str]('username', str),
        )
        self._fields: tuple[AutoField] = (
            AutoField[User, bool]('is_sign_in', bool),
            AutoField[User, Datetime]('datetime', Datetime, allowed_none=True),
            AutoField[User, float]('ratio', float),
            AutoField[User, bytes]('hash', bytes, allowed_none=True),
            AutoField[User, CustomType]('custom', CustomType, allowed_none=True)
        )

        self._database = BaseDBRequest[User](
            model_type = User,
            table_name = 'users',
            fields = self._key_fields + self._fields,
            key_fields = self._key_fields,
            type_converters = (BaseTypeConverter[CustomType, str](CustomType, str), )
        )

    def test(self) -> None:
        # Create user and check autoincrement id

        user = User(id=None, username='user_one')
        self._database.save(user)
        self._database.load(user)

        self.assertEqual(user.id, 1)
        del(user)

        # Check loading user by id

        user = User(id=1, username=None)
        self._database.load(user)

        self.assertEqual(user.username, 'user_one')
        self.assertEqual(user.is_sign_in, False)
        self.assertEqual(user.datetime, None)

        # Check saving some different types

        datetime = Datetime(2000, 1, 1, 12, 30)
        user.is_sign_in = True
        user.datetime = datetime
        user.ratio = 3.14
        user.hash = 'hash'.encode()
        user.custom = CustomType('test')

        self._database.update(user)
        del(user)

        user = User(id=1)
        self._database.load(user)

        self.assertEqual(user.is_sign_in, True)
        self.assertEqual(user.datetime, datetime)
        self.assertEqual(user.ratio, 3.14)
        self.assertEqual(user.hash, 'hash'.encode())
        self.assertEqual(user.custom.value, 'test')

        # Simple check load_all

        users = self._database.load_all(user)
        self.assertEqual(len(users), 1)

        # Check load_all with sort

        user_one = User(id=1)
        user_two = User(username='user_two')
        user_two.is_sign_in = True
        user_two.ratio = 1.23
        
        self._database.save(user_two)
        self._database.load(user_one)
        self._database.load(user_two)

        users = self._database.load_all(User(), sort_by='ratio')
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].username, 'user_two')
        
    def tearDown(self) -> None:
        delete_database()


if __name__ == '__main__':
    main()





