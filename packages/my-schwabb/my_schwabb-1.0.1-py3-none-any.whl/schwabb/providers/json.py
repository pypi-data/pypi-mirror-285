from pathlib import Path

try:
    import orjson as json
except ImportError:
    print("orjson not found, using json")
    import json

from .base import Provider

class JSONProvider(Provider):
    __slots__ = ('_path',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Format key into a hidden .json file
        if not self._key.startswith('.'):
            self._key = f".{self._key}"
        self._key = self._key.rstrip('.json')

        # Create a directory to store tokens
        token_directory = Path.home() / Path('.tokens')
        if not token_directory.exists():
            token_directory.mkdir(parents=True, exist_ok=True)
        self._path = token_directory / self._key

        # Create a JSON file if it doesn't exist
        if not self._path.exists():
            with open(self._path, 'w') as file:
                file.write('{}')

        print("JSON provider initialized")

    def close(self):
        pass

    def retrieve(self, **kwargs):
        with open(self._path, 'rb') as file:
            return json.loads(file.read())

    def store(self, key=None, data=None, **kwargs):
        key = key or self._key
        if data is None:
            raise ValueError('Data must be provided')
        with open(self._path, 'wb') as file:
            file.write(json.dumps(data))