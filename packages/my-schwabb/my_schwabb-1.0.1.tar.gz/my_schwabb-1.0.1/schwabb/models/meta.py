# Standard library imports
from dataclasses import dataclass

@dataclass(slots=True)
class Mapping:
    def __getitem__(self, key):
        if isinstance(key, int) and hasattr(self, '_data'):
            return self._data[key]
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        self._data = tuple(getattr(self, name) for name in self.__dataclass_fields__.keys() if not name.startswith('_'))

    def __iter__(self):
        return iter(self._data)

    def items(self):
        return tuple((name, getattr(self, name)) for name in self.__dataclass_fields__.keys() if not name.startswith('_'))

    def keys(self):
        return tuple(name for name in self.__dataclass_fields__.keys() if not name.startswith('_'))

    def values(self):
        return tuple(getattr(self, name) for name in self.__dataclass_fields__.keys() if not name.startswith('_'))


class Filterable:
    def filter(self, value, by):
        return self.__class__([obj for obj in self._data if getattr(obj, by) == value])