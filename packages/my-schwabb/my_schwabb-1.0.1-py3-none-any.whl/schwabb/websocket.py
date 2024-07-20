import asyncio
import atexit
import certifi
import ssl
import websockets
import orjson as json
import signal

from .client import Client
from .enums.websocket import Command, Service, EquityOptions


def from_enum(enum, value):
    if any((
        enum is EquityOptions,
    )):
        return enum[value].value
    return enum(value).name

class Websocket:
    __slots__ = ('_conn', '_sub_id', '_preferences', '_ssl_context', '_client_params', '_loop')

    def __init__(self, loop=None, **client_params):
        self._sub_id = 0
        self._client_params = client_params
        self._ssl_context = ssl.create_default_context()
        self._ssl_context.load_verify_locations(certifi.where())
        with Client(fetch=False, **client_params) as client:
            self._preferences = client.get_user_preferences()

        if loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError as e:
                print(f"Error initializing websocket: {e}")
                self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop

        # atexit.register(self._cleanup)
        # self._register_cleanup()

    @property
    def sub_id(self):
        self._sub_id += 1
        return self._sub_id

    def _cleanup(self):
        print("Running cleanup...")
        self.logout()
        print("Cleanup done.")

    def _exit_handler(self, conn):
        async def wrapper():
            await self._cleanup(conn)
            self._loop.stop()

        def handler(signum, frame):
            print("Signal received, running cleanup...")
            asyncio.ensure_future(wrapper())

        return handler

    def _register_cleanup(self):
        # Register signal handlers for SIGINT (Ctrl+C) and SIGTERM
        signal.signal(signal.SIGINT, self.logout)
        signal.signal(signal.SIGTERM, self.logout)

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

    def logout(self, *args, **kwargs):
        params = self._build_request('admin', 'logout', {})
        async def _logout(conn, params):
            try:
                await conn.send(params)
                print(await conn.recv())
            except websockets.exceptions.ConnectionClosedError:
                return await _logout(conn, params)
        # try:
        #     loop = asyncio.get_running_loop()
        # except RuntimeError:
        #     loop = asyncio.get_event_loop()
        # loop = asyncio.new_event_loop()
        asyncio.create_task(_logout(self._conn, params))
        # self._loop.run_until_complete(_logout(self._conn, params))


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

    async def subscribe_account(self, conn):
        params = {
            'keys': 'Account Activity',
            'fields': '0,1,2,3'
        }
        params = self._build_request('account_activity', 'subs', params)
        await conn.send(params)
        print(await conn.recv())

    async def stream(self):
        async for conn in websockets.connect(self._preferences.ws_url, ping_interval=5):
            self._conn = conn
            try:
                await self.login(conn)
                # await self.subscribe_equities(conn, ('AAPL', 'MSFT'))
                await self.subscribe_account(conn)
                print('Successfully authenticated and subscribed. Streaming...')

                while True:
                    res = await conn.recv()
                    res = json.loads(res)
                    print(res, type(res))

            except Exception as e:
                import traceback
                traceback.print_exc()
                self._sub_id = 0
