import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from schwabb import Websocket


async def main():
    websocket = Websocket(provider='redis', host='192.168.1.154')

    await websocket.stream()


asyncio.run(main())
