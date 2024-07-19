from ..constants import INTERACTION_TYPE, TYPE, Nullable, DISPLAY_UTILS
from ...utils import Utils


def display_text(text: str, *, style: Nullable.Style = None):
    id = Utils.generate_id()

    return {
        "model": {"id": id, "style": style, "properties": {"text": text}},
        "hooks": None,
        "type": TYPE.DISPLAY_TEXT,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }


def display_header(text: str, *, style: Nullable.Style = None):
    id = Utils.generate_id()

    return {
        "model": {"id": id, "style": style, "properties": {"text": text}},
        "hooks": None,
        "type": TYPE.DISPLAY_HEADER,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }


def display_json(
    json: DISPLAY_UTILS.Json,
    *,
    label: Nullable.Str = None,
    description: Nullable.Str = None,
    style: Nullable.Style = None
):
    id = Utils.generate_id()

    return {
        "model": {
            "id": id,
            "style": style,
            "properties": {
                "label": label,
                "description": description,
                "json": json,
            },
        },
        "hooks": None,
        "type": TYPE.DISPLAY_JSON,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }


def display_spinner(*, text: Nullable.Str = None, style: Nullable.Style = None):
    id = Utils.generate_id()

    return {
        "model": {
            "id": id,
            "style": style,
            "properties": {
                "text": text,
            },
        },
        "hooks": None,
        "type": TYPE.DISPLAY_SPINNER,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }


def display_code(
    code: str,
    *,
    label: Nullable.Str = None,
    description: Nullable.Str = None,
    style: Nullable.Style = None
):
    id = Utils.generate_id()

    return {
        "model": {
            "id": id,
            "style": style,
            "properties": {
                "code": code,
                "label": label,
                "description": description,
            },
        },
        "hooks": None,
        "type": TYPE.DISPLAY_CODE,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }


def display_image(src: str, *, style: Nullable.Style = None):
    id = Utils.generate_id()

    return {
        "model": {
            "id": id,
            "style": style,
            "properties": {
                "src": src,
            },
        },
        "hooks": None,
        "type": TYPE.DISPLAY_IMAGE,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }


def display_markdown(markdown: str, *, style: Nullable.Style = None):
    id = Utils.generate_id()

    return {
        "model": {
            "id": id,
            "style": style,
            "properties": {
                "markdown": markdown,
            },
        },
        "hooks": None,
        "type": TYPE.DISPLAY_MARKDOWN,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }


def display_none():
    id = Utils.generate_id()

    return {
        "model": {
            "id": id,
            "style": None,
            "properties": {},
        },
        "hooks": None,
        "type": TYPE.DISPLAY_NONE,
        "interactionType": INTERACTION_TYPE.DISPLAY,
    }
