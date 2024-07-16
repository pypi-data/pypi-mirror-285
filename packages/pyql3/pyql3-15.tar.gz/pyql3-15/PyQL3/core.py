from sqlite3 import (
    Cursor as _Cursor,
    Connection as _Connection
)

__all__ = [
    'validate', 'Connection', 'Cursor'
]


def validate(func):
    """
    RU: Декоратор для проверки существования объекта в базе данных перед выполнением функции.
    EN: Decorator for validating if the object exists in the database before executing the function.
    """

    def wrapper(self, *args, **kwargs):
        if not self._exists():
            raise RuntimeError(
                f'{self} is not present in the database,'
                f' it has been deleted or moved.'
            )
        return func(self, *args, **kwargs)

    return wrapper


class Cursor(_Cursor):
    """
    RU: Расширение стандартного курсора SQLite для добавления дополнительных методов.
    EN: Extension of the standard SQLite cursor to add additional methods.
    """

    def __init__(self, *args, **kwargs):
        """
        RU: Инициализирует объект ExCursor с указанными аргументами и ключевыми аргументами.
        EN: Initializes the ExCursor object with the specified arguments and keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def fetchitem(self, index: int = 0):
        """
        RU: Возвращает элемент по указанному индексу из следующей строки результата запроса.
        EN: Returns the item at the specified index from the next row of the query result.
        """
        return self.fetchone()[index]

    def fetchitems(self, index: int = 0):
        """
        RU: Возвращает элементы по указанному индексу из всех строк результата запроса.
        EN: Returns the items at the specified index from all rows of the query result.
        """
        return tuple(item[index] for item in self.fetchall())


class Connection(_Connection):
    """
    RU: Расширение стандартного соединения SQLite для использования ExCursor вместо стандартного курсора.
    EN: Extension of the standard SQLite connection to use ExCursor instead of the standard cursor.
    """

    def __init__(self, *args, **kwargs):
        """
        RU: Инициализирует объект ExConnection с указанными аргументами и ключевыми аргументами.
        EN: Initializes the ExConnection object with the specified arguments and keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self._cursor = self.cursor()

    def cursor(self, cls=Cursor):
        """
        RU: Возвращает новый объект курсора указанного класса.
        EN: Returns a new cursor object of the specified class.
        """
        return super().cursor(cls)
