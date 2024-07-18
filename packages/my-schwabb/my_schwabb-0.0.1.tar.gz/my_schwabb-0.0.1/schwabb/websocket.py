import asyncio
import certifi
import ssl
import websockets
import orjson as json

from .client import Client
from .enums.websocket import Command, Service, EquityOptions

def from_enum(enum, value):
    if any((
        enum is EquityOptions,
    )):
        return enum[value].value
    return enum(value).name

class Websocket:
    __slots__ = ('_sub_id', '_preferences', '_ssl_context', '_client_params')

    def __init__(self, **client_params):
        self._sub_id = 0
        self._client_params = client_params
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.load_verify_locations(certifi.where())
        with Client(fetch=False, **client_params) as client:
            self._preferences = client.get_user_preferences()

    @property
    def sub_id(self):
        self._sub_id += 1
        return self._sub_id

    async def logout(self, conn):
        params = self._build_request('admin', 'logout', {})
        await conn.send(json.dumps(params))
        print(await conn.recv())

    async def login(self, conn):
        with Client(**self._client_params) as client:
            access_token = client.token.access_token

        params = {
            'Authorization': access_token,
            'SchwabClientChannel': self._preferences.client_channel,
            'SchwabClientFunctionId': self._preferences.client_function_id,
        }
        params = self._build_request('admin', 'login', params)

        await conn.send(params)
        print(await conn.recv())

    async def subscribe_equities(self, conn, symbols, fields=(0, 3, 8)):
        fields = sorted(fields)
        symbols = ','.join(symbols)
        fields = ','.join(str(n) for n in fields)
        params = {
            'keys': symbols,
            'fields': fields,
        }
        params = self._build_request('equities', 'subs', params)
        print(f"Subscribing with: {params}")
        await conn.send(params)
        print(await conn.recv())

    def _build_request(self, service, command, params):
        return json.dumps({
            'requests': [{
                'requestid': self.sub_id,
                'service': from_enum(Service, service),
                'command': from_enum(Command, command),
                'SchwabClientCustomerId': self._preferences.client_customer_id,
                'SchwabClientCorrelId': self._preferences.client_correl_id,
                'parameters': params
            }]
        }).decode('utf-8')

    async def subscribe_account(self, conn):
        pass

    async def stream(self):
        async for conn in websockets.connect(self._preferences.ws_url, ping_interval=5):
            try:
                await self.login(conn)
                # await self.subscribe_equities(conn, ('AAPL', 'MSFT'))
                print('Successfully authenticated and subscribed. Streaming..')

                while True:
                    res = await conn.recv()
                    res = json.loads(res)
                    print(res, type(res))

            except Exception as e:
                import traceback
                traceback.print_exc()
                self._sub_id = 0
