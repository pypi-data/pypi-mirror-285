from typing import (
    TypedDict,
    NotRequired,
    Literal,
    Union,
    Dict,
    List,
    Any,
    Callable,
    TYPE_CHECKING,
    get_type_hints,
)

if TYPE_CHECKING:
    from .components import ComponentsType


class INTERACTION_TYPE:
    INPUT = "input"
    BUTTON = "button"
    DISPLAY = "display"
    LAYOUT = "layout"


class TYPE:
    # INPUT TYPES
    INPUT_TEXT = "input-text"
    INPUT_NUMBER = "input-number"
    INPUT_EMAIL = "input-email"
    INPUT_URL = "input-url"
    INPUT_RADIO_GROUP = "input-radio-group"
    INPUT_SELECT_DROPDOWN_SINGLE = "input-select-dropdown-single"
    INPUT_SELECT_DROPDOWN_MULTI = "input-select-dropdown-multi"
    INPUT_TABLE = "input-table"
    INPUT_FILE_DROP_ZONE = "input-file-drop-zone"

    # BUTTON TYPES
    BUTTON_DEFAULT = "button-default"
    BUTTON_FORM_SUBMIT = "button-form-submit"

    # DISPLAY TYPES
    DISPLAY_TEXT = "display-text"
    DISPLAY_HEADER = "display-header"
    DISPLAY_JSON = "display-json"
    DISPLAY_SPINNER = "display-spinner"
    DISPLAY_CODE = "display-code"
    DISPLAY_IMAGE = "display-image"
    DISPLAY_MARKDOWN = "display-markdown"
    # A special type that's used to represent when a render returns None
    DISPLAY_NONE = "display-none"

    # LAYOUT TYPES
    LAYOUT_STACK = "layout-stack"
    LAYOUT_FORM = "layout-form"


def add_type_hints_as_class_attributes(cls):
    hints = get_type_hints(cls)
    for name, hint in hints.items():
        setattr(cls, name, hint)
    return cls


@add_type_hints_as_class_attributes
class LAYOUT_UTILS:
    DEFAULT_DIRECTION = "vertical"
    DEFAULT_JUSTIFY = "start"
    DEFAULT_ALIGN = "start"

    Direction: Literal[
        "vertical", "vertical-reverse", "horizontal", "horizontal-reverse"
    ]
    Justify: Literal["start", "end", "center", "between", "around", "evenly"]
    Align: Literal[
        "start",
        "end",
        "center",
        "baseline",
        "stretch",
    ]


@add_type_hints_as_class_attributes
class INPUT_UTILS:
    MULTI_SELECTION_MIN_DEFAULT = 0
    MULTI_SELECTION_MAX_DEFAULT = 1000000000

    class SelectOption(TypedDict):
        value: Any
        label: str
        description: NotRequired[str]

    SelectOptions = list[SelectOption]

    TableDataRow = Dict[str, Union[str, int, float, None]]
    TableData = list[TableDataRow]

    class TableColumn(TypedDict):
        label: str
        key: str

    TableColumns = list[TableColumn]

    def hydate_input_select_options(options):
        return [
            {
                "value": opt["value"],
                "label": opt["label"],
                "description": opt.get("description", None),
            }
            for opt in options
        ]


@add_type_hints_as_class_attributes
class DISPLAY_UTILS:
    JsonValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
    Json = Union[Dict[str, JsonValue], List[JsonValue]]


class ComponentStyle(TypedDict):
    width: NotRequired[str]
    height: NotRequired[str]
    margin: NotRequired[str]
    marginTop: NotRequired[str]
    marginBottom: NotRequired[str]
    marginLeft: NotRequired[str]
    marginRight: NotRequired[str]
    padding: NotRequired[str]
    paddingTop: NotRequired[str]
    paddingBottom: NotRequired[str]
    paddingLeft: NotRequired[str]
    paddingRight: NotRequired[str]
    overflowX: NotRequired[Literal["visible", "hidden", "scroll", "auto", "clip"]]
    overflowY: NotRequired[Literal["visible", "hidden", "scroll", "auto", "clip"]]
    backgroundColor: NotRequired[str]
    borderRadius: NotRequired[str]


@add_type_hints_as_class_attributes
class Nullable:
    Callable = Union[Callable, None]
    Str = Union[str, None]
    Bool = Union[bool, None]
    Int = Union[int, None]
    Float = Union[float, None]
    Style = Union[ComponentStyle, None]

    TableColumns = Union[INPUT_UTILS.TableColumns, None]

    class List:
        Str = Union[List[str], None]
        Int = Union[List[int], None]
        Float = Union[List[float], None]
        Bool = Union[List[bool], None]
