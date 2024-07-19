import pandas
from ..constants import (
    INTERACTION_TYPE,
    TYPE,
    INPUT_UTILS,
    Nullable,
)


def input_text(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {},
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_TEXT,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_email(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {},
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_EMAIL,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_url(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {},
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_URL,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def input_number(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {},
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_NUMBER,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def radio_group(
    id: str,
    options: INPUT_UTILS.SelectOption,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "options": INPUT_UTILS.hydate_input_select_options(options),
            },
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_RADIO_GROUP,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def select_dropdown_single(
    id: str,
    options: INPUT_UTILS.SelectOption,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "options": INPUT_UTILS.hydate_input_select_options(options),
            },
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_SELECT_DROPDOWN_SINGLE,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def select_dropdown_multi(
    id: str,
    options: INPUT_UTILS.SelectOption,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "options": INPUT_UTILS.hydate_input_select_options(options),
                "minSelections": min_selections,
                "maxSelections": max_selections,
            },
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_SELECT_DROPDOWN_MULTI,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def _table(
    id: str,
    data: INPUT_UTILS.TableData,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None,
    columns: Nullable.TableColumns = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT,
    allow_select: bool = True
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "data": data,
                "columns": columns,
                "actions": None,
                "minSelections": min_selections,
                "maxSelections": max_selections,
                "allowSelect": allow_select,
            },
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_TABLE,
        "interactionType": INTERACTION_TYPE.INPUT,
    }


def table(
    id: str,
    data: INPUT_UTILS.TableData,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None,
    columns: Nullable.TableColumns = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT,
    allow_select: bool = True
):
    return _table(
        id,
        data,
        label=label,
        required=required,
        description=description,
        validate=validate,
        style=style,
        columns=columns,
        min_selections=min_selections,
        max_selections=max_selections,
        allow_select=allow_select,
    )


def dataframe(
    id: str,
    df: pandas.DataFrame,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None,
    min_selections: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_selections: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT,
    allow_select: bool = True
):
    # Create the "columns" array
    columns = [{"key": col, "label": col} for col in df.columns]

    # Create the "table" array
    table = df.to_dict(orient="records")

    return _table(
        id,
        table,
        label=label,
        required=required,
        description=description,
        validate=validate,
        style=style,
        columns=columns,
        min_selections=min_selections,
        max_selections=max_selections,
        allow_select=allow_select,
    )


def input_file_drop_zone(
    id: str,
    *,
    label: Nullable.Str = None,
    required: bool = True,
    description: Nullable.Str = None,
    validate: Nullable.Callable = None,
    style: Nullable.Style = None,
    accepted_file_types: Nullable.List.Str = None,
    min_count: int = INPUT_UTILS.MULTI_SELECTION_MIN_DEFAULT,
    max_count: int = INPUT_UTILS.MULTI_SELECTION_MAX_DEFAULT
):
    return {
        "model": {
            "id": id,
            "label": label,
            "description": description,
            "required": required,
            "hasValidateHook": validate is not None,
            "style": style,
            "properties": {
                "acceptedFileTypes": accepted_file_types,
                "minCount": min_count,
                "maxCount": max_count,
            },
        },
        "hooks": {
            "validate": validate,
        },
        "type": TYPE.INPUT_FILE_DROP_ZONE,
        "interactionType": INTERACTION_TYPE.INPUT,
    }
