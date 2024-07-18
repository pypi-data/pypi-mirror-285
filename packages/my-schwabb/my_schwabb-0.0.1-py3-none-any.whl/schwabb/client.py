from os import environ
from datetime import datetime, date, timedelta
from functools import cache, wraps

import requests

from .models import Accounts, Orders, Order, Positions, QuoteData, UserPreferences
from ._token import Token
from .urls import urls
from .utils import ratelimit

SEVEN_DAYS = 604800

def validate_response(func):
    @wraps(func)
    def request(self, *args, **kwargs):
        try:
            response = func(self, *args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            print(f"Request timed out: {e}, retrying...")
            return request(self, *args, **kwargs)

        if not str(response.status_code).startswith('2'):
            print(f"Request failed: {response.text}")
            raise Exception(f"Request failed.")
        return response
    return request

def get_account_number(func):
    @wraps(func)
    def request(self, account_number=None, *args, **kwargs):
        account_number = account_number or self.primary_account
        return func(self, account_number=account_number, *args, **kwargs)
    return request

class BaseClient:
    urls = urls

    @ratelimit(120, 60)
    def _request(self, method, url, *args, **kwargs):
        method = method.lower()
        if method not in {'get', 'post', 'put', 'delete'}:
            raise ValueError(f"Invalid method '{method}'. Method must be one of {'get', 'post', 'put', 'delete'}")
        return self.session.request(method, url, *args, **kwargs)

    @validate_response
    def _get_request(self, url, params=None, headers=None, **kwargs):
        headers = headers or self.token.headers
        # response = self.session.get(url, params=params, headers=headers)
        return self._request('GET', url, params=params, headers=headers)

    @validate_response
    def _post_request(self, url, data, headers=None, **kwargs):
        headers = headers or self.token.headers
        response = self._request('POST', url, json=data, headers=headers)
        return response

    @validate_response
    def _put_request(self, url, data, headers=None, **kwargs):
        headers = headers or self.token.headers
        response = self._request('PUT', url, json=data, headers=headers)
        return response

    @validate_response
    def _delete_request(self, url, headers=None, **kwargs):
        headers = headers or self.token.headers
        response = self._request('PUT', url, headers=headers)
        return response


class Client(BaseClient):
    urls = urls

    def __init__(self, primary_account=None, provider='redis', encrypt=False, app_key=None, secret=None, fetch=False, **kwargs):
        self.app_key = app_key or environ.get("SCHWABB_APP_KEY")
        if self.app_key is None:
            self.app_key = input('Enter your Schwabb API app key: ')

        self.secret = secret or environ.get("SCHWABB_SECRET")
        if self.secret is None:
            self.secret = input('Enter your API secret: ')

        self.session = requests.Session()
        self.token = Token(
            provider=provider,
            encrypt=encrypt,
            session=self.session,
            app_key=self.app_key,
            secret=self.secret,
            **kwargs
        )

        if fetch:
            # Setup account information
            self.accounts = Accounts(self._accounts(account_numbers=True))

            if primary_account is not None:
                primary_account = int(primary_account)
                self.accounts.set_primary(primary_account)

                for account in self.accounts:
                    if account.number == primary_account:
                        self.primary_account = account
                        break
            else:
                self.primary_account = self.accounts[0]
                print(f"\033[91m[Warning]\033[0m: Primary account not specified. Using {self.primary_account.number} as primary")
                print(f"           Methods not given an exclusive account_number as a parameter will default to primary account number: {self.primary_account.number}")
                print('           You\'ve been warned.')

            # Retrieve current positions
            self.positions = self._positions(self.primary_account)
        else:
            self.accounts = None
            self.positions = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_traceback:
            import traceback
            traceback.print_exc()
        return

    # Websocket
    @cache
    def user_preferences(self):
        preferences = self._get_request(self.urls.user_preference_url).json()
        preferences = preferences['streamerInfo'][0]
        return UserPreferences(
            ws_url=preferences['streamerSocketUrl'],
            client_customer_id=preferences['schwabClientCustomerId'],
            client_correl_id=preferences['schwabClientCorrelId'],
            client_channel=preferences['schwabClientChannel'],
            client_function_id=preferences['schwabClientFunctionId'],
        )

    def get_user_preferences(self):
        return self.user_preferences()

    # Accounts
    def _accounts(self, account_number=None, account_numbers=False, **kwargs):
        params = None
        if not account_numbers and account_number is None:
            url = urls.accounts_url
        elif account_number is not None:
            url = f"{urls.accounts_url}/{account_number}?fields=positions"
            params = {'fields': 'positions'}
        else:
            url = f"{urls.accounts_url}/accountNumbers"
        response = self._get_request(url=url, params=params)
        return response.json()

    def account_numbers(self, **kwargs):
        return self._accounts(account_numbers=True, **kwargs)

    @get_account_number
    def account(self, account_number=None, **kwargs):
        # account_number = account_number or self.primary_account
        return self._accounts(account_number=account_number)

    @get_account_number
    def _positions(self, account_number=None, **kwargs):
        # account_number = account_number or self.primary_account
        return Positions(self._accounts(account_number=account_number)['securitiesAccount']['positions'])

    def get_accounts(self, account_number=None, account_numbers=False, **kwargs):
        return self._accounts(account_number=account_number, account_numbers=account_numbers, **kwargs)

    @get_account_number
    def get_positions(self, account_number=None, **kwargs):
        # account_number = account_number or self.primary_account
        return self._positions(account_number=account_number, **kwargs)

    # Orders
    @get_account_number
    def get_orders(
        self,
        account_number = None,
        from_date: datetime = None,
        to_date: datetime = None,
        **kwargs):

        if from_date is not None:
            from_date = from_date.isoformat() + 'Z'
        else:
            from_date = (datetime.now() - timedelta(days=14)).isoformat() + 'Z'
        if to_date is not None:
            to_date = to_date.isoformat() + 'Z'
        else:
            to_date = datetime.now().isoformat() + 'Z'

        orders = self._get_request(urls.orders_url(account_number), params=dict(fromEnteredTime=from_date, toEnteredTime=to_date)).json()
        return Orders([
            Order(**order)
            for order in orders
        ])

    def place_order(self, symbol, account_number=None, **kwargs):
        account_number = account_number or self.primary_account
        data = Order.new(symbol, **kwargs)
        return self._post_request(urls.orders_url(account_number), data)

    def place_market_order(self, symbol, account_number=None, *, qty, side, **kwargs):
        account_number = account_number or self.primary_account
        return self.place_order(symbol, account_number, qty=qty, side=side, order_type='market', **kwargs)

    # Market Data
    def quote(self, symbol, fields=('quote', 'reference'), all=False, **kwargs):
        if all:
            fields = ('quote', 'fundamental', 'extended', 'reference', 'regular')
        params = {'fields': ','.join(fields)}
        quote = self._get_request(urls.quote_url(symbol), params=params).json()
        quote = quote[symbol]
        return QuoteData.new(symbol, quote, fields)

    def quotes(self, symbols, fields=('quote', 'reference'), all=False, **kwargs):
        if all:
            fields = ('quote', 'fundamental', 'extended', 'reference', 'regular')
        params = {'fields': ','.join(fields)}

        quotes = self._get_request(urls.quotes_url(symbols), params=params).json()
        errors = quotes.pop('errors', None)
        if errors is not None:
            print(f"Error fetching quotes: {errors}")
        return {symbol: QuoteData.new(symbol, quote, fields) for symbol, quote in quotes.items()}
