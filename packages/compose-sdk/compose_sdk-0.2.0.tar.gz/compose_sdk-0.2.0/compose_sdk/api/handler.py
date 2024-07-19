import ssl
import websockets
import queue

from ..scheduler import Scheduler
from ..core import EventType
from .ws_message import (
    encode_json,
    encode_ws_message,
    decode_file_transfer_message,
    decode_json_message,
)

DEV_WS_URL = "ws://localhost:8080/api/v1/sdk/ws"
PROD_WS_URL = "wss://app.composehq.com/api/v1/sdk/ws"


class APIHandler:
    def __init__(self, scheduler: Scheduler, isDevelopment: bool, apiKey: str) -> None:
        self.scheduler = scheduler

        self.isDevelopment = isDevelopment
        self.apiKey = apiKey

        self.listeners: dict[str, callable] = {}

        self.ws = None
        self.is_connected = False
        self.push = None

        self.send_queue = queue.Queue()

    def add_listener(self, id: str, listener: callable) -> None:
        if id in self.listeners:
            raise ValueError(f"Listener with id {id} already exists")

        self.listeners[id] = listener

    def remove_listener(self, id: str) -> None:
        if id not in self.listeners:
            return

        del self.listeners[id]

    def connect(self, on_connect_data: dict) -> None:
        self.scheduler.run_until_complete(self.__makeConnectionRequest(on_connect_data))

    async def send(self, data: object, sessionId: str | None = None) -> None:
        headerStr = (
            data["type"]
            if data["type"] == EventType.SdkToServer.INITIALIZE
            else data["type"] + sessionId
        )

        binary = encode_ws_message(headerStr, encode_json(data))

        if self.is_connected == True:
            await self.push(binary)
        else:
            self.send_queue.put(binary)

    async def __makeConnectionRequest(self, on_connect_data: dict) -> None:
        WS_URL = DEV_WS_URL if self.isDevelopment else PROD_WS_URL

        headers = {"x-api-key": self.apiKey}

        ssl_context = None
        if not self.isDevelopment:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED

        async for ws in websockets.connect(
            uri=WS_URL, extra_headers=headers, ssl=ssl_context
        ):
            try:
                self.is_connected = True

                async def push(data):
                    if ws is not None:
                        await ws.send(data)

                self.push = push

                await self.send(on_connect_data)

                async for message in ws:
                    self.__flush_send_queue()
                    await self.__on_message(message)

            except websockets.ConnectionClosed:
                self.is_connected = False
                continue

    async def __on_message(self, message) -> None:
        # First 2 bytes are always event type
        event_type = message[:2].decode("utf-8")

        if event_type == EventType.ServerToSdk.FILE_TRANSFER:
            data = decode_file_transfer_message(message)
        else:
            data = decode_json_message(message)

        for listener in self.listeners.values():
            listener(data)

    def __flush_send_queue(self) -> None:
        if self.is_connected:
            while not self.send_queue.empty():
                binary = self.send_queue.get()
                self.scheduler.create_task(self.ws.send(binary))
