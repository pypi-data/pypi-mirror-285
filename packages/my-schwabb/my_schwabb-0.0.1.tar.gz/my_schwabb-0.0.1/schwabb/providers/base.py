from os import environ
from cryptography.fernet import Fernet

from .abstract import AbstractProvider


class Provider(AbstractProvider):
    __slots__ = ('_key', '_cipher')

    def __init__(self, key='schwabb', encrypt=False, *args, **kwargs):
        self._key = key
        if encrypt:
            if not isinstance(encrypt, str):
                encrypt = environ.get('SCHWABB_SECRET_KEY')
                if encrypt is None:
                    encrypt = Fernet.generate_key()
                else:
                    encrypt = bytes(encrypt, 'utf-8')

            self._cipher = Fernet(encrypt)

    def encrypt(self, data):
        data['refresh_token'] = self._cipher.encrypt(data['refresh_token'].encode('utf-8')).decode('utf-8')
        data['access_token'] = self._cipher.encrypt(data['access_token'].encode('utf-8')).decode('utf-8')
        return data

    def decrypt(self, data):
        data['refresh_token'] = self._cipher.decrypt(data['refresh_token'])
        data['access_token'] = self._cipher.decrypt(data['access_token'])
        return data