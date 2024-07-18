from abc import ABC, abstractmethod

class AbstractProvider(ABC):
    __slots__ = ()

    @abstractmethod
    def retrieve(self):
        pass

    @abstractmethod
    def store(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @classmethod
    def new(cls, provider, *args, **kwargs):
        provider = provider.lower()
        if provider == 'sqlite':
            from .sqlite import SQLiteProvider
            return SQLiteProvider(*args, **kwargs)
        elif provider == 'mysql':
            from .mysql import MySQLProvider
            return MySQLProvider(*args, **kwargs)
        elif provider == 'redis':
            from .redis import RedisProvider
            return RedisProvider(*args, **kwargs)
        elif provider == 'json':
            from .json import JSONProvider
            return JSONProvider(*args, **kwargs)
        raise ValueError(f"Invalid provider '{provider}'")
