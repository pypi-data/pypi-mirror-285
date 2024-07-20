import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'src'))

import dbrequest
from dbrequest import BaseDBRequest, AutoField


dbrequest.init(init_script='examples/quick_start.sql', database_filename='examples/quick_start.db')

class User:
    def __init__(self, id: int | None = None, username: str | None = None) -> None:
        self.id = id
        self.username = username
        self.last_message: str | None = None

id_field = AutoField('id', int, allowed_none=True)
username_field = AutoField('username', str)
last_message_field = AutoField('last_message', str, allowed_none=True)

user_db_request = BaseDBRequest[User](
    model_type = User,
    table_name = 'users',
    fields = (
        id_field,
        username_field,
        last_message_field,
    ),
    key_fields = (
        id_field,
        username_field,
    ),
)

if __name__ == '__main__':
    user = User(username='simple_user')
    user_db_request.save(user)

    user = user_db_request.load_all(User(), limit=1, reverse=True)[0]
    print(user.id)

    same_user = User(id=user.id)
    user_db_request.load(same_user)
    print(same_user.username)

    user.last_message = 'Hello world!'
    user_db_request.update(user)

    admin = User(username='admin')
    admin.last_message = 'Do you want to be banned?'
    user_db_request.save(admin)

    users = user_db_request.load_all(User())
    for user in users:
        print(f'The user who said "{user.last_message}" has been deleted')
        user_db_request.delete(user)

