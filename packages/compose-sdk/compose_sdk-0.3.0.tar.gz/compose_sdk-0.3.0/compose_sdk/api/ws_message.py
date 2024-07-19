import json

from ..core import EventType


def encode_json(data):
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


def encode_ws_message(header_string, data):
    header_buffer = header_string.encode("utf-8")
    combined_buffer = bytearray(header_buffer)
    combined_buffer.extend(data)
    return bytes(combined_buffer)


def decode_file_transfer_message(message: bytes) -> dict:
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

    return data


def decode_json_message(message: bytes) -> dict:
    jsonData = message[38:].decode("utf-8")
    return json.loads(jsonData)
