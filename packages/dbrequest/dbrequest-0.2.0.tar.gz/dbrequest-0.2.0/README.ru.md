# dbrequest
dbrequest это простая ORM библиотека для удобной работы с базами данных. Библиотека предназначена в первую очередь для простых проектов, в которых не нужны сложные SQL-запросы и в качестве СУБД может быть использована SQLite (хотя библиотека позволяет работать с другими СУБД). 

Библиотека предоставляет абстракцию от СУБД и позволяет работать с сохранением, загрузкой, изменением и удалением объектов-моделей без явного использования SQL.

## Содержание
- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Документация](#документация)
- [Обратная связь](#обратная-связь)

## Установка

Из репозитория PyPI:

```bash
$ pip install dbrequest
```

Установка из github-репозитория (необходим pip версии 20 и выше)

```sh
$ pip install git+https://github.com/korandr/dbrequest.git
```

Импорт

```python
import dbrequest
```

## Быстрый старт
Для примера создадим таблицу `users`. Опишем её в файле `tables.sql`:

```sql
create table IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    last_message TEXT DEFAULT NULL
);
```

Инициализируем библиотеку:

```python
import dbrequest

dbrequest.init(init_script='tables.sql')
```

Далее опишем модель в виде класса `User`:

```python
class User:
    def __init__(self, id: int | None = None, username: str | None = None) -> None:
        self.id = id
        self.username = username
        self.last_message: str | None = None
```

Теперь создадим объекты `IField` для всех сохраняемых полей класса:

```python
from dbrequest import AutoField

id_field = AutoField('id', int, allowed_none=True)
username_field = AutoField('username', str)
last_message_field = AutoField('last_message', str, allowed_none=True)
```

Здесь мы используем класс `dbrequest.AutoField`, так как название полей и соответствующих колонок в таблице совпадают.   
В более сложных случаях можно использовать класс `dbrequest.BaseField` и явно указать соответствие названий. 

Остаётся создать объект для запросов к базе данных:

```python
from dbrequest import BaseDBRequest

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
```
В параметре `fields` указываем кортеж всех полей в том порядке, в котором были созданы столбцы в таблице.   
`key_fields` - поля с уникальными значениями, по которым можно будет найти конкретный объект в базе данных.  

Generic-параметр класса `BaseDBRequest` не обязательный, но поможет при типизации возврата метода `load_all`.  

Теперь можно удобно выполнять операции с классом `User` и базой данных:

```python
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
```

[Код этого и других примеров](https://github.com/korandr/dbrequest/tree/main/examples)

## Документация

Базовая документация содержится в библиотеке (docstring).
С полной документацией можно ознакомиться [здесь](https://github.com/korandr/dbrequest/wiki) (только на русском)

## Обратная связь
Разработчик: Андрей Коровянский | [andrey.korovyansky@gmail.com](mailto:andrey.korovyansky@gmail.com) 
