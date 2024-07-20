import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'src'))

import uuid

import dbrequest
from dbrequest import BaseDBRequest, AutoField


dbrequest.init(init_script='examples/uuid_field.sql', database_filename='examples/uuid_field.db')

class User:
    def __init__(self, id: str | None = None) -> None:
        self.id = id

    def issue_id(self) -> None:
        self.id = uuid.uuid4().hex

id_field = AutoField('id', str, allowed_none=True)

user_db_request = BaseDBRequest[User](
    model_type = User,
    table_name = 'users',
    fields = (id_field, ),
    key_fields = (id_field, ),
)

if __name__ == '__main__':
    user = User()
    user.issue_id()
    print(user.id)
    user_db_request.save(user)

    same_user = user_db_request.load_all(User(), limit=1, reverse=True)[0]
    print(same_user.id)

