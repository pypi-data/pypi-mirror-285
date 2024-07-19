import asyncio
import json
import ssl
import uuid
import websockets

from ..core import EventType

DEV_WS_URL = "ws://localhost:8080/api/v1/sdk/ws"
PROD_WS_URL = "wss://app.composehq.com/api/v1/sdk/ws"


def create_buffer_from_json(data):
    # Remove callable objects from the data. Python doesn't do this
    # automatically.
    def remove_callables(obj):
        if isinstance(obj, dict):
            return {k: remove_callables(v) for k, v in obj.items() if not callable(v)}
        elif isinstance(obj, list):
            return [remove_callables(item) for item in obj]
        else:
            return obj

    cleaned_data = remove_callables(data)
    json_string = json.dumps(cleaned_data)
    return json_string.encode("utf-8")


def create_binary_ws_message(header_string, data):
    header_buffer = header_string.encode("utf-8")
    combined_buffer = bytearray(header_buffer)
    combined_buffer.extend(data)
    return bytes(combined_buffer)


class APIHandler:
    def __init__(
        self, loop: asyncio.AbstractEventLoop, isDevelopment: bool, apiKey: str
    ) -> None:
        self.loop = loop
        self.isDevelopment = isDevelopment
        self.apiKey = apiKey

        self.listeners: dict[str, callable] = {}

        self.ws = None
        self.isConnected = False
        self.push = None
        self.send_queue = {}

    def add_listener(self, id: str, listener: callable) -> None:
        if id in self.listeners:
            raise ValueError(f"Listener with id {id} already exists")

        self.listeners[id] = listener

    def remove_listener(self, id: str) -> None:
        if id not in self.listeners:
            return

        del self.listeners[id]

    def connect(self, on_connect_data: dict) -> None:
        if self.ws is not None:
            return

        # This will block the thread until the connection is established
        self.loop.run_until_complete(self.__makeConnectionRequest(on_connect_data))

    async def send(self, data: object, sessionId: str | None = None) -> None:
        headerStr = (
            data["type"]
            if data["type"] == EventType.SdkToServer.INITIALIZE
            else data["type"] + sessionId
        )

        binary = create_binary_ws_message(headerStr, create_buffer_from_json(data))

        if self.isConnected == True:
            await self.push(binary)
        else:
            id = str(uuid.uuid4())
            self.send_queue[id] = binary

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
                self.isConnected = True

                async def push(data):
                    if ws is not None:
                        await ws.send(data)

                self.push = push

                await self.send(on_connect_data)

                async for message in ws:
                    self.__flush_send_queue()
                    await self.__on_message(message)

            except websockets.ConnectionClosed:
                self.isConnected = False
                continue

    async def __on_message(self, message) -> None:
        # First 2 bytes are always event type
        event_type = message[:2].decode("utf-8")

        if event_type == EventType.ServerToSdk.FILE_TRANSFER:
            # Bytes 2-38 are the environmentId, hence we start parsing after that
            execution_id = message[38:74].decode("utf-8")
            file_id = message[74:110].decode("utf-8")

            file_contents = message[110:]

            data = {
                "type": EventType.ServerToSdk.FILE_TRANSFER,
                "executionId": execution_id,
                "fileId": file_id,
                "fileContents": file_contents,
            }
        else:
            jsonData = message[38:].decode("utf-8")
            data = json.loads(jsonData)

        for listener in self.listeners.values():
            listener(data)

    def __flush_send_queue(self) -> None:
        if self.isConnected:
            for _, binary in self.send_queue.items():
                self.loop.create_task(self.ws.send(binary))
            self.send_queue = {}
