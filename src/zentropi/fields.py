# coding=utf-8
from typing import Any, Optional


class Field(object):
    """
    A Field allows us to store data with extra information associated with it.

    Example:
        >>> from zentropi import Field
        >>> test_field = Field(42, name='the_answer')
        >>> test_field.default
        42
        >>> test_field.value
        42
        >>> test_field.name
        'the_answer'
        >>> test_field.kind
        'Field'
        >>> test_field.describe()
        {'kind': 'Field', 'name': 'the_answer', 'value': 42}
    """
    __slots__ = ['_default', '_value', '_name', '_meta']

    def __init__(self,
                 default: Optional[Any] = None,
                 *,
                 name: Optional[str] = None) -> None:
        self._default = self.clean_and_validate(default)
        self._value = self._default
        self._name = name or str(id(self))
        self._meta = ['kind', 'name', 'value']

    @property
    def default(self) -> Any:
        return self._default

    @property
    def kind(self) -> str:
        return type(self).__name__

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Expected non-empty string for name, '
                             'got: {!r}'.format(name))
        self._name = name

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = self.clean_and_validate(value)

    def clean_and_validate(self, value: Any):
        value_ = self.clean(value)
        try:
            if self.validate(value_):
                return value_
            raise ValueError('Field: {} got invalid value: {!r}.'.format(self._name, value))
        except Exception as e:
            raise e

    def clean(self, value: Any) -> Any:
        """Override: Convert types or clean up text; return cleaned value."""
        return value

    def validate(self, value: Any) -> bool:
        """Override: Return True if given value is valid,
        this should only accept cleaned values and return False if the
        value is not valid. Alternatively, raise an exception."""
        return True

    def describe(self) -> dict:
        return {k: getattr(self, k) for k in self._meta}


class PersistentField(Field):
    __slots__ = ['_default', '_value', '_name', '_meta', '_store']

    def __init__(self,
                 default: Optional[Any] = None,
                 *,
                 name: Optional[str] = None,
                 store: Optional[Any] = None) -> None:
        super().__init__(default, name=name)
        self._store = store
        if name not in store:
            self._store[name] = self.clean_and_validate(default)

    @property
    def value(self) -> Any:
        if self._name in self._store:
            return self._store[self._name]
        return self._default

    @value.setter
    def value(self, value: Any) -> None:
        import transaction
        self._store[self._name] = self.clean_and_validate(value)
        transaction.commit()


class PersistentStore(object):
    def __init__(self, file_name: str, extra_tables: Optional[dict] = None):
        from BTrees.OOBTree import OOBTree
        from persistent import Persistent
        valid_store_cls = (OOBTree, Persistent)
        self.tables = {
            'states': OOBTree,
        }
        if extra_tables is not None:
            for name, cls in extra_tables.items():
                if not isinstance(name, str):
                    raise AssertionError('Expected name to be str, got: {!r}'.format(name))
                if not issubclass(cls, valid_store_cls):
                    raise AssertionError('Expected cls to be one of {}, got: {!r}'.format(
                        ', '.join([cls.__name__ for cls in valid_store_cls]),
                        cls
                    ))
            self.tables.update(extra_tables)
        self.zodb_connection = None
        self.zodb_db = None
        self.zodb_storage = None
        self.db = self.load_db(file_name)

    def load_db(self, file_name):
        import os
        import atexit
        from ZODB import DB, FileStorage
        file_name = os.path.expanduser(file_name)
        print('*** Loading db {!r}'.format(file_name))
        storage = FileStorage.FileStorage(file_name)
        db = DB(storage)
        conn = db.open()
        root = conn.root()
        for table_name, table_class in self.tables.items():
            if not hasattr(root, table_name):
                setattr(root, table_name, table_class())
                print('*** Created table {!r}'.format(table_name))
        self.zodb_connection = conn
        self.zodb_db = db
        self.zodb_storage = storage
        atexit.register(self.save_db)
        return root

    def save_db(self):
        print('*** Saving db...')
        self.zodb_connection.close()
        self.zodb_db.close()
        self.zodb_storage.close()

    def field(self, default, *, name: Optional[str] = None):
        return PersistentField(default, name=name, store=self.db.states)
