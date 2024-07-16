from .core import (
    validate, Connection
)

__all__ = [
    'PyObject', 'PyRow', 'PyRows',
    'PyColumn', 'PyColumns', 'PyTable'
]


class PyObject:
    """
        RU: Базовый класс для объектов, связанных с базой данных.
        EN: Base class for objects associated with a database.
        """

    def __init__(self, parent):
        """
        RU: Инициализирует объект ExObject с указанным родителем.
        EN: Initializes the ExObject object with the specified parent.
        """
        self._parent = parent
        self._cursor = self.parent(Connection).cursor()

    def parent(self, cls: type = None):
        """
        RU: Возвращает родительский объект указанного типа.
        EN: Returns the parent object of the specified type.
        """
        if cls is None:
            return self._parent
        if cls is type(self):
            return None
        parent = self._parent
        while not isinstance(parent, (cls, Connection)):
            parent = parent.parent()
        return parent


class PyRow(PyObject):
    """
    RU: Класс PyRow представляет собой строку в таблице базы данных.
    EN: The PyRow class represents a row in a database table.
    """

    def __init__(self, parent, _id: int):
        """
        RU: Инициализирует объект PyRow с указанным родителем и идентификатором.
        EN: Initializes the PyRow object with the specified parent and identifier.
        """
        super().__init__(parent)
        self._id = _id
        self._row = {}

    def _exists(self) -> bool:
        """
        RU: Проверяет, существует ли строка в родительской таблице.
        EN: Checks whether the row exists in the parent table.
        """
        return self.id in self.parent()

    @property
    def id(self):
        """
        RU: Возвращает идентификатор строки.
        EN: Returns the row identifier.
        """
        return self._id

    @property
    @validate
    def ids(self) -> tuple[str, ...]:
        """
        RU: Возвращает идентификаторы столбцов в родительской таблице.
        EN: Returns the column identifiers in the parent table.
        """
        return self.parent(PyTable).columns.ids

    @validate
    def get(self, _id: str):
        """
        RU: Возвращает значение указанного столбца в этой строке.
        EN: Returns the value of the specified column in this row.
        """
        if _id not in self:
            raise KeyError(_id)
        if _id not in self._row:
            cmd = (
                f"SELECT {_id}"
                f" FROM {self.parent(PyTable).id}"
                f" WHERE rowid=?;"
            )
            self._cursor.execute(cmd, (self.id,))
            self._row[_id] = self._cursor.fetchitem(0)
        return self._row[_id]

    @validate
    def get_by_index(self, index: int):
        """
        RU: Возвращает значение столбца по указанному индексу в этой строке.
        EN: Returns the column value at the specified index in this row.
        """
        if not (0 <= index < len(self)):
            raise IndexError(
                "PyRow index out of range."
            )
        cmd = (
            f"SELECT *"
            f" FROM {self.parent(PyTable).id}"
            f" WHERE rowid=?;"
        )
        self._cursor.execute(cmd, (self.id,))
        return self._cursor.fetchitem(index)

    @validate
    def deserialize(self):
        cmd = (
            f"SELECT * FROM"
            f" {self.parent(PyTable).id}"
            f" WHERE rowid=?;"
        )
        self._cursor.execute(cmd, (self.id,))
        return self._cursor.fetchone()

    @validate
    def set(self, _id: str, value) -> None:
        """
        RU: Устанавливает значение указанного столбца в этой строке.
        EN: Sets the value of the specified column in this row.
        """
        if _id not in self:
            raise KeyError(_id)
        cmd = (
            f"UPDATE {self.parent(PyTable).id}"
            f" SET {_id}=?"
            f" WHERE rowid=?;"
        )
        self._cursor.execute(cmd, (value, self.id))

    @validate
    def set_by_index(self, index: int, value):
        """
        RU: Устанавливает значение столбца по указанному индексу в этой строке.
        EN: Sets the column value at the specified index in this row.
        """
        if not (0 <= index < len(self)):
            raise IndexError(
                "PyRow index out of range."
            )
        columns = self.parent(PyTable).columns
        column = columns.get_by_index(index)
        return self.set(column.id, value)

    @validate
    def __contains__(self, _id: str):
        """
        RU: Проверяет, содержит ли строка указанный столбец.
        EN: Checks whether the row contains the specified column.
        """
        contains = _id in self.parent(PyTable).columns
        if not contains:
            self._row.pop(_id, None)
        return contains

    @validate
    def __iter__(self):
        """
        RU: Возвращает итератор по значениям столбцов в этой строке.
        EN: Returns an iterator over the column values in this row.
        """
        return iter(self.get(item) for item in self.ids)

    @validate
    def __len__(self):
        """
        RU: Возвращает количество столбцов в этой строке.
        EN: Returns the number of columns in this row.
        """
        return len(self.parent(PyTable).columns)

    @validate
    def __repr__(self):
        """
        RU: Возвращает строковое представление объекта PyRow.
        EN: Returns a string representation of the PyRow object.
        """
        content = f"'{self._id}'"
        return f"<PyRow object at 0x{id(self)}: {content}>"


class PyRows(PyObject):
    """
    RU: Класс PyRows представляет собой набор строк в таблице базы данных.
    EN: The PyRows class represents a set of rows in a database table.
    """

    def __init__(self, parent):
        """
        RU: Инициализирует объект PyRows с указанным родителем.
        EN: Initializes the PyRows object with the specified parent.
        """
        super().__init__(parent)
        self._rows = {}

    def _exists(self) -> bool:
        """
        RU: Проверяет, существует ли родительская таблица.
        EN: Checks whether the parent table exists.
        """
        return self.parent()._exists()

    @property
    @validate
    def ids(self) -> tuple[int, ...]:
        """
        RU: Возвращает идентификаторы строк в родительской таблице.
        EN: Returns the row identifiers in the parent table.
        """
        cmd = (
            f"SELECT rowid"
            f" FROM {self.parent().id}"
            f" ORDER BY rowid;"
        )
        self._cursor.execute(cmd)
        return self._cursor.fetchitems(0)

    @validate
    def get(self, _id: int) -> PyRow:
        """
        RU: Возвращает объект PyRow для указанного идентификатора строки.
        EN: Returns the PyRow object for the specified row identifier.
        """
        if _id not in self:
            raise KeyError(_id)
        if _id not in self._rows:
            self._rows[_id] = PyRow(self, _id)
        return self._rows[_id]

    @validate
    def get_by_index(self, index: int) -> PyRow:
        """
        RU: Возвращает объект PyRow для строки по указанному индексу.
        EN: Returns the PyRow object for the row at the specified index.
        """
        if not (0 <= index < len(self)):
            raise IndexError("PyRows index out of range.")
        cmd = (
            f" SELECT rowid"
            f" FROM {self.parent().id}"
            f" ORDER BY rowid"
            f" LIMIT 1 OFFSET ?;"
        )
        self._cursor.execute(cmd, (index,))
        return self.get(self._cursor.fetchitem(0))

    @validate
    def get_by_sql(
            self,
            where: str = None,
            limit: int = None,
            offset: int = None
    ) -> list[PyRow]:
        """
        RU: Возвращает список объектов PyRow для строк, удовлетворяющих указанному условию.
        EN: Returns a list of PyRow objects for rows that satisfy the specified condition.
        """
        columns = "rowid"
        order = " ORDER BY rowid"
        where = (
            f" WHERE {where}"
            if where else ''
        )
        limit = (
            f" LIMIT {limit}"
            if limit else ''
        )
        offset = (
            f" OFFSET {offset}"
            if offset and limit else ''
        )
        cmd = (
            f"SELECT {columns}"
            f" FROM {self.parent().id}"
            f"{where}{order}{limit}{offset};"
        )
        self._cursor.execute(cmd)
        items = self._cursor.fetchitems(0)
        if items:
            return [self.get(item) for item in items]
        raise KeyError(where)

    @validate
    def deserialize(
            self,
            columns: tuple[str, ...] = None,
            where: str = None,
            order: str = None,
            limit: int = None,
            offset: int = None
    ) -> list[tuple]:
        """
        RU: Выполняет SQL-запрос SELECT с указанными параметрами и возвращает результаты.
        EN: Performs a SQL SELECT query with the specified parameters and returns the results.
        """
        columns = (
            ", ".join(columns)
            if columns else '*'
        )
        where = (
            f" WHERE {where}"
            if where else ''
        )
        order = (
            f" ORDER BY {order}"
            if order else ''
        )
        limit = (
            f" LIMIT {limit}"
            if limit else ''
        )
        offset = (
            f" OFFSET {offset}"
            if offset and limit else ''
        )
        cmd = (
            f'SELECT {columns}'
            f' FROM {self.parent().id}'
            f'{where}{order}{limit}{offset};'
        )
        self._cursor.execute(cmd)
        return self._cursor.fetchall()

    @validate
    def delete(self, _id: int) -> None:
        """
        RU: Удаляет строку с указанным идентификатором из таблицы.
        EN: Deletes the row with the specified identifier from the table.
        """
        self._rows.pop(_id, None)
        cmd = (
            f"DELETE FROM {self.parent().id}"
            f" WHERE rowid=?;")
        self._cursor.execute(cmd, (_id,))

    @validate
    def delete_by_index(self, index: int):
        """
        RU: Удаляет строку по указанному индексу из таблицы.
        EN: Deletes the row at the specified index from the table.
        """
        return self.delete(self.ids[index])

    @validate
    def delete_by_where(self, where: str) -> None:
        """
        RU: Удаляет строки, удовлетворяющие указанному условию, из таблицы.
        EN: Deletes rows that satisfy the specified condition from the table.
        """
        cmd = (
            f"SELECT rowid"
            f" FROM {self.parent().id}"
            f" WHERE {where}"
            f" ORDER BY rowid;"
        )
        self._cursor.execute(cmd)
        for item in self._cursor.fetchitems(0):
            self._rows.pop(item, None)

        cmd = (
            f"DELETE FROM {self.parent().id}"
            f" WHERE {where};"
        )
        self._cursor.execute(cmd)

    @validate
    def insert(
            self,
            columns: tuple[str, ...] = None,
            values: tuple = None
    ) -> None:
        """
        RU: Вставляет новую строку с указанными столбцами и значениями в таблицу.
        EN: Inserts a new row with the specified columns and values into the table.
        """
        if not columns:
            columns = self.parent().columns.ids
        elif not isinstance(columns, tuple):
            raise ValueError(
                'The columns must be a tuple[str, ...] or None.'
            )
        if not (values and isinstance(values, tuple)):
            raise ValueError(
                'The values must be a tuple[any, ...].'
            )
        plugs = ','.join(['?'] * len(values))
        cmd = (
            f"INSERT INTO {self.parent().id}"
            f" {columns} VALUES({plugs});"
        )
        self._cursor.execute(cmd, values)

    @validate
    def __contains__(self, _id):
        """
        RU: Проверяет, содержит ли таблица строку с указанным идентификатором.
        EN: Checks whether the table contains a row with the specified identifier.
        """
        cmd = (
            f"SELECT EXISTS"
            f"(SELECT 1 FROM {self.parent().id} "
            f"WHERE rowid=? LIMIT 1);"
        )
        self._cursor.execute(cmd, (_id,))
        contains = self._cursor.fetchitem(0) > 0
        if not contains:
            self._rows.pop(_id, None)
        return contains

    @validate
    def __iter__(self):
        """
        RU: Возвращает итератор по объектам PyRow в таблице.
        EN: Returns an iterator over the PyRow objects in the table.
        """
        return iter(self.get(item) for item in self.ids)

    @validate
    def __len__(self):
        """
        RU: Возвращает количество строк в таблице.
        EN: Returns the number of rows in the table.
        """
        cmd = (
            f"SELECT COUNT(rowid)"
            f" FROM {self.parent(PyTable).id};"
        )
        self._cursor.execute(cmd)
        return int(self._cursor.fetchitem(0))

    @validate
    def __repr__(self):
        """
        RU: Возвращает строковое представление объекта PyRows.
        EN: Returns a string representation of the PyRows object.
        """
        content = (
            "()" if not len(self)
            else f"({self.get_by_index(0)}, ...)"
        )
        return f"<PyRows object at 0x{id(self)}: {content}>"


class PyColumn(PyObject):
    """
    RU: Класс PyColumn представляет собой столбец в таблице базы данных.
    EN: The PyColumn class represents a column in a database table.
    """

    def __init__(self, parent, _id: str):
        """
        RU: Инициализирует объект PyColumn с указанным родителем и идентификатором.
        EN: Initializes the PyColumn object with the specified parent and identifier.
        """
        super().__init__(parent)
        self._id = _id

    def _exists(self) -> bool:
        """
        RU: Проверяет, существует ли столбец в родительской таблице.
        EN: Checks whether the column exists in the parent table.
        """
        return self._id in self.parent()

    @property
    def id(self) -> str:
        """
        RU: Возвращает идентификатор столбца.
        EN: Returns the column identifier.
        """
        return self._id

    @property
    @validate
    def pragma(self) -> tuple:
        """
        RU: Возвращает информацию о столбце из PRAGMA_TABLE_INFO.
        EN: Returns column information from PRAGMA_TABLE_INFO.
        """
        cmd = (
            "SELECT *"
            " FROM PRAGMA_TABLE_INFO(?)"
            " WHERE name=?;"
        )
        self._cursor.execute(cmd, (self.parent(PyTable).id, self.id))
        return self._cursor.fetchone()

    @property
    @validate
    def type(self) -> str:
        """
        RU: Возвращает тип данных столбца.
        EN: Returns the data type of the column.
        """
        return self.pragma[2]

    @property
    @validate
    def not_null(self) -> bool:
        """
        RU: Проверяет, является ли столбец NOT NULL.
        EN: Checks whether the column is NOT NULL.
        """
        return bool(self.pragma[3])

    @property
    @validate
    def default(self):
        """
        RU: Возвращает значение по умолчанию для столбца.
        EN: Returns the default value for the column.
        """
        return self.pragma[4]

    @property
    @validate
    def pk(self) -> bool:
        """
        RU: Проверяет, является ли столбец первичным ключом.
        EN: Checks whether the column is a primary key.
        """
        return bool(self.pragma[5])

    @validate
    def __repr__(self):
        """
        RU: Возвращает строковое представление объекта PyColumn.
        EN: Returns a string representation of the PyColumn object.
        """
        content = f"'{self.id}'"
        return f"<PyColumn object at 0x{id(self)}: {content}>"


class PyColumns(PyObject):
    """
    RU: Класс PyColumns представляет собой набор столбцов в таблице базы данных.
    EN: The PyColumns class represents a set of columns in a database table.
    """

    def __init__(self, parent):
        """
        RU: Инициализирует объект PyColumns с указанным родителем.
        EN: Initializes the PyColumns object with the specified parent.
        """
        super().__init__(parent)
        self._columns = {}

    def _exists(self) -> bool:
        """
        RU: Проверяет, существует ли родительская таблица.
        EN: Checks whether the parent table exists.
        """
        return self.parent()._exists()

    @property
    @validate
    def ids(self) -> tuple[str, ...]:
        """
        RU: Возвращает идентификаторы столбцов в родительской таблице.
        EN: Returns the column identifiers in the parent table.
        """
        cmd = (
            f"SELECT name"
            f" FROM PRAGMA_TABLE_INFO(?);"
        )
        self._cursor.execute(cmd, (self.parent().id,))
        return self._cursor.fetchitems(0)

    @property
    @validate
    def pragma(self) -> list[tuple]:
        """
        RU: Возвращает информацию о столбцах из PRAGMA_TABLE_INFO.
        EN: Returns column information from PRAGMA_TABLE_INFO.
        """
        cmd = (
            f"SELECT * FROM"
            f" PRAGMA_TABLE_INFO(?);"
        )
        self._cursor.execute(cmd, (self.parent().id,))
        return self._cursor.fetchall()

    @validate
    def get(self, _id: str) -> PyColumn:
        """
        RU: Возвращает объект PyColumn для указанного идентификатора столбца.
        EN: Returns the PyColumn object for the specified column identifier.
        """
        if _id not in self:
            raise KeyError(_id)
        if _id not in self._columns:
            self._columns[_id] = PyColumn(self, _id)
        return self._columns[_id]

    @validate
    def get_by_index(self, index: int) -> PyColumn:
        """
        RU: Возвращает объект PyColumn для столбца по указанному индексу.
        EN: Returns the PyColumn object for the column at the specified index.
        """
        if not (0 <= index < len(self)):
            raise IndexError(
                "PyColumns index out of range."
            )
        cmd = (
            f"SELECT name"
            f" FROM PRAGMA_TABLE_INFO(?)"
            f" LIMIT 1 OFFSET ?;"
        )
        self._cursor.execute(cmd, (self.parent().id, index))
        return self.get(self._cursor.fetchitem(0))

    @validate
    def __contains__(self, _id: str):
        """
        RU: Проверяет, содержит ли таблица столбец с указанным идентификатором.
        EN: Checks whether the table contains a column with the specified identifier.
        """
        cmd = (
            f"SELECT EXISTS"
            f"(SELECT 1 FROM PRAGMA_TABLE_INFO(?)"
            f" WHERE name=? LIMIT 1);"
        )
        self._cursor.execute(cmd, (self.parent().id, _id))
        contains = self._cursor.fetchitem(0) > 0
        if not contains:
            self._columns.pop(_id, None)
        return contains

    @validate
    def __iter__(self):
        """
        RU: Возвращает итератор по объектам PyColumn в таблице.
        EN: Returns an iterator over the PyColumn objects in the table.
        """
        return iter(self.get(item) for item in self.ids)

    @validate
    def __len__(self):
        """
        RU: Возвращает количество столбцов в таблице.
        EN: Returns the number of columns in the table.
        """
        cmd = (
            f"SELECT COUNT(*)"
            f" FROM PRAGMA_TABLE_INFO(?);"
        )
        self._cursor.execute(cmd, (self.parent().id,))
        return int(self._cursor.fetchitem(0))

    @validate
    def __repr__(self):
        """
        RU: Возвращает строковое представление объекта PyColumns.
        EN: Returns a string representation of the PyColumns object.
        """
        content = self.ids
        return f"<PyColumns object at 0x{id(self)}: {content}>"


class PyTable(PyObject):
    """
    RU: Класс PyTable представляет собой таблицу в базе данных.
    EN: The PyTable class represents a table in a database.
    """

    def __init__(self, parent, _id):
        """
        RU: Инициализирует объект PyTable с указанным родителем и идентификатором.
        EN: Initializes the PyTable object with the specified parent and identifier.
        """
        super().__init__(parent)
        self._id = _id
        self._columns = PyColumns(self)
        self._rows = PyRows(self)

    def _exists(self) -> bool:
        """
        RU: Проверяет, существует ли таблица в родительской базе данных.
        EN: Checks whether the table exists in the parent database.
        """
        return self._id in self.parent()

    @property
    def id(self) -> str:
        """
        RU: Возвращает идентификатор таблицы.
        EN: Returns the table identifier.
        """
        return self._id

    @property
    @validate
    def columns(self) -> PyColumns:
        """
        RU: Возвращает объект PyColumns, представляющий столбцы в этой таблице.
        EN: Returns the PyColumns object representing the columns in this table.
        """
        return self._columns

    @property
    @validate
    def rows(self) -> PyRows:
        """
        RU: Возвращает объект PyRows, представляющий строки в этой таблице.
        EN: Returns the PyRows object representing the rows in this table.
        """
        return self._rows

    @property
    def primary_key(self) -> tuple[str, ...]:
        """
        RU: Возвращает первичный ключ этой таблицы.
        EN: Returns the primary key of this table.
        """
        pragma = self.columns.pragma
        return tuple(item[1] for item in pragma if item[5])

    @property
    def foreign_keys(self) -> list[tuple]:
        """
        RU: Возвращает внешние ключи этой таблицы.
        EN: Returns the foreign keys of this table.
        """
        cmd = (
            f"PRAGMA foreign_key_list({self.id});"
        )
        self._cursor.execute(cmd)
        return [item[2:5] for item in self._cursor.fetchall()]

    @validate
    def __repr__(self):
        """
        RU: Возвращает строковое представление объекта PyTable.
        EN: Returns a string representation of the PyTable object.
        """
        content = f"'{self.id}'"
        return f"<PyTable object at 0x{id(self)}: {content}>"


class PyConnection(Connection):
    """
    RU: Класс PyConnection представляет собой соединение с базой данных.
    EN: The PyConnection class represents a connection to a database.
    """

    def __init__(self, *args, **kwargs):
        """
        RU: Инициализирует объект PyConnection с указанными аргументами и ключевыми аргументами.
        EN: Initializes the PyConnection object with the specified arguments and keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self._tables = {}

    @property
    def ids(self) -> tuple[str, ...]:
        """
        RU: Возвращает идентификаторы таблиц в базе данных.
        EN: Returns the identifiers of the tables in the database.
        """
        cmd = (
            f"SELECT name"
            f" FROM sqlite_master"
            f" WHERE type=?;"
        )
        self._cursor.execute(cmd, ('table',))
        return self._cursor.fetchitems(0)

    def get(self, _id: str) -> PyTable:
        """
        RU: Возвращает объект PyTable для указанного идентификатора таблицы.
        EN: Returns the PyTable object for the specified table identifier.
        """
        if _id not in self:
            raise KeyError(_id)
        if _id not in self._tables:
            self._tables[_id] = PyTable(self, _id)
        return self._tables[_id]

    def get_by_index(self, index: int) -> PyTable:
        """
        RU: Возвращает объект PyTable для таблицы по указанному индексу.
        EN: Returns the PyTable object for the table at the specified index.
        """
        if not (0 <= index < len(self)):
            raise IndexError(
                "PyConnection index out of range."
            )
        cmd = (
            f"SELECT name"
            f" FROM sqlite_master"
            f" WHERE type=? LIMIT 1 OFFSET ?;"
        )
        self._cursor.execute(cmd, ('table', index))
        return self.get(self._cursor.fetchitem(0))

    def __contains__(self, _id: str):
        """
        RU: Проверяет, содержит ли база данных таблицу с указанным идентификатором.
        EN: Checks whether the database contains a table with the specified identifier.
        """
        cmd = (
            f"SELECT EXISTS"
            f"(SELECT 1 FROM sqlite_master"
            f" WHERE type=? and name=? LIMIT 1);"
        )
        self._cursor.execute(cmd, ('table', _id))
        contains = self._cursor.fetchitem(0) > 0
        if not contains:
            self._tables.pop(_id, None)
        return contains

    def __iter__(self):
        """
        RU: Возвращает итератор по объектам PyTable в базе данных.
        EN: Returns an iterator over the PyTable objects in the database.
        """
        return iter(self.get(item) for item in self.ids)

    def __len__(self):
        """
        RU: Возвращает количество таблиц в базе данных.
        EN: Returns the number of tables in the database.
        """
        cmd = (
            f"SELECT COUNT(*)"
            f" FROM sqlite_master"
            f" WHERE type=?;"
        )
        self._cursor.execute(cmd, ('table',))
        return int(self._cursor.fetchitem(0))

    def __repr__(self):
        """
        RU: Возвращает строковое представление объекта PyConnection.
        EN: Returns a string representation of the PyConnection object.
        """
        content = self.ids
        return f"<PyConnection object at 0x{id(self)}: {content}>"
