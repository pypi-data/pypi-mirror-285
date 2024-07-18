import base64
import time
import webbrowser
from dataclasses import dataclass
from os import environ
from atexit import register as register_exit_function

import requests

from .providers import Provider
from .urls import urls

SEVEN_DAYS = 604800
KEYS = {'access_expiration', 'refresh_expiration', 'access_token', 'refresh_token', 'token_type', 'id_token', 'scope'}

@dataclass(slots=True, eq=False, order=False, frozen=True, kw_only=True)
class TokenData:
    access_expiration: float
    refresh_expiration: float
    access_token: str
    refresh_token: str
    token_type: str
    id_token: str | None = None
    scope: str | None = None

    def __post_init__(self):
        object.__setattr__(self, 'access_expiration', float(self.access_expiration))
        object.__setattr__(self, 'refresh_expiration', float(self.refresh_expiration))

    def __getitem__(self, key):
        return getattr(self, key)


class Token:
    __slots__ = ('_app_key', '_secret', '_session', '_provider')

    def __init__(self, provider='redis', key='schwabb', encrypt=False, session=None, app_key=None, secret=None, **kwargs):
        self._app_key = app_key or environ.get('SCHWABB_APP_KEY')
        if self._app_key is None:
            self._app_key = input('Enter your Schwabb API app key: ')

        self._secret = secret or environ.get('SCHWABB_SECRET')
        if self._secret is None:
            self._secret = input('Enter your API secret: ')

        self._session = session or requests.Session()
        self._provider = Provider.new(provider, key=key, encrypt=encrypt, **kwargs)

        # Cleanup redis connection
        register_exit_function(self._cleanup)

    def __repr__(self):
        return repr(self._data)

    def __getitem__(self, key):
        if key not in KEYS:
            raise KeyError(f"Key must be one of {KEYS}")
        return self._data[key]

    def _cleanup(self):
        self._provider.close()

    @property
    def _now(self):
        return time.time()

    @property
    def _data(self):
        data = self._provider.retrieve()
        if not data:
            data = self.manual_flow()
        return TokenData(**data)

    @_data.setter
    def _data(self, value):
        if not isinstance(value, (dict, TokenData)):
            raise ValueError('Value must be a dictionary or TokenData object')
        if 'access_expiration' not in value:
            raise ValueError('Value must contain access_expiration key')
        if 'access_token' not in value:
            raise ValueError('Value must contain access_token key')
        if 'refresh_token' not in value:
            raise ValueError('Value must contain refresh_token key')
        if 'token_type' not in value:
            raise ValueError('Value must contain token_type key')
        self._provider.store(key='schwabb', data=value)

    @property
    def access_token(self):
        data = self._data
        if self._now >= data['access_expiration']:
            data = self._post_oauth_token(grant_type='refresh_token')
        return data['access_token']

    @property
    def access_expiration(self):
        return self._data['access_expiration']

    @property
    def refresh_token(self):
        return self._data['refresh_token']

    @property
    def refresh_expiration(self):
        return self._data['refresh_expiration']

    @property
    def token_type(self):
        return self._data['token_type']

    @property
    def scope(self):
        return self._data['scope']

    @property
    def id_token(self):
        return self._data['id_token']

    @property
    def headers(self):
        data = self._data
        if self._now >= data['access_expiration']:
            data = self._post_oauth_token(grant_type='refresh_token')

        return {
            'Authorization': f"{data['token_type']} {data['access_token']}",
            'Accept': 'application/json'
        }


    def _post_oauth_token(self, grant_type='refresh_token', code=None):
        """
        Makes API calls for auth code and refresh tokens
        """
        headers = {
            'Authorization': f"Basic {base64.b64encode(bytes(f'{self._app_key}:{self._secret}', 'utf-8')).decode("utf-8")}",
            'Accept': 'application/x-www-form-urlencoded'
        }
        if grant_type == 'authorization_code':  # gets access and refresh tokens using authorization code
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': urls.redirect_uri
            }
        elif grant_type == 'refresh_token':  # refreshes the access token
            # Retrieve the code from OAuth Redis database
            if code is None:
                data = self._provider.retrieve(key='schwabb')
                code = data['refresh_token']

            data = {
                'grant_type': 'refresh_token',
                'refresh_token': code
            }

        response = self._session.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)

        if response.status_code != 200:
            if response.json()['error'] == 'unsupported_token_type':
                data = self.manual_flow()

            print(f"Failed to get token: {response.text}")
            print(f"Json: {response.json()}")
            raise Exception(f"Failed to get token: {response.text}")

        # Set the expiration time for the access token
        data = response.json()
        now = self._now

        data['access_expiration'] = now + data.pop('expires_in')

        if grant_type == 'authorization_code':
            data['refresh_expiration'] = now + SEVEN_DAYS

        # Store the data in the Redis database
        self._data = data

        return data

    def manual_flow(self):
        webbrowser.register("chrome", None, webbrowser.BackgroundBrowser("/usr/bin/google-chrome"))
        browser = webbrowser.get("chrome")
        url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={self._app_key}&redirect_uri=https://127.0.0.1"

        print(f"Browsing to: {url}")
        browser.open(url)

        def parse_code(url):
            return url.split("code=")[1].split("%40")[0] + "@"

        code = parse_code(input("Enter the URL: "))

        return self._post_oauth_token(
            grant_type='authorization_code',
            code=code
        )