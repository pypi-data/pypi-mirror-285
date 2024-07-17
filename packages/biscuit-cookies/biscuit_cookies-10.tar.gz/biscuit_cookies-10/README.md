# BISCUIT-COOKIES

Этот проект представляет собой программу для взаимодействия с куками (cookies) в браузере пользователя. Программа позволяет извлекать и расшифровывать зашифрованные данные о куках, а также добавлять новые данные куков в базу данных.

## Используемые пакеты
- pyql3
- pywin32
- pycryptodome

## Функциональность
1. Инициализация Biscuit объекта с указанием пути к каталогу пользователя и профиля браузера.
2. Метод `get()`: Получение куков из базы данных с возможностью применения SQL операторов WHERE, ORDER BY, LIMIT, OFFSET.
3. Метод `add()`: Добавление новых куков в базу данных.

## Использование
1. Создать объект Biscuit, указав путь к каталогу пользователя и профиля браузера.
2. Вызвать метод `get()` для получения списка куков или `add()` для добавления новых куков.

## Пример использования
```python
from biscuit.cookies import Biscuit

biscuit = Biscuit('/path/to/user/data/directory', profile='Default')

# Пример использования метода add() для добавления куков
new_cookies = [
    {'name': 'username', 'value': 'john_doe', 'domain': 'example.com', 'path': '/', 'expires': '1656079200'},
    {'name': 'session', 'value': '1234567890', 'domain': 'sub.example.com', 'path': '/admin', 'expires': '1656079200'},
]

biscuit.add(new_cookies)

# Проверка добавленных куков
cookies = biscuit.get(where='domain LIKE "%.example.com"')
print(cookies)
```