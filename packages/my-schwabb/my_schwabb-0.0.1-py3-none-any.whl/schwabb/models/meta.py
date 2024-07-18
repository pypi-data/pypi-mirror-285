from dataclasses import dataclass

@dataclass(slots=True)
class Indexable:
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
        return tuple((item[0], getattr(self, item[0])) for item in self.__dataclass_fields__.items() if not item[0].startswith('_'))

    def keys(self):
        return tuple(item[0] for item in self.__dataclass_fields__.items() if not item[0].startswith('_'))

    def values(self):
        return tuple(getattr(self, item[0]) for item in self.__dataclass_fields__.items() if not item[0].startswith('_'))