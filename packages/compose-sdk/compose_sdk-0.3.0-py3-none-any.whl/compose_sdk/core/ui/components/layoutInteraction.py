from typing import TYPE_CHECKING, Union
from ..constants import INTERACTION_TYPE, TYPE, LAYOUT_UTILS, Nullable
from ...utils import Utils

if TYPE_CHECKING:
    from ..components import ComponentsType

Children = Union["ComponentsType", list["ComponentsType"]]


def layout_stack(
    children: Children,
    *,
    direction: LAYOUT_UTILS.Direction = LAYOUT_UTILS.DEFAULT_DIRECTION,
    justify: LAYOUT_UTILS.Justify = LAYOUT_UTILS.DEFAULT_JUSTIFY,
    align: LAYOUT_UTILS.Align = LAYOUT_UTILS.DEFAULT_ALIGN,
    style: Nullable.Style = None
):
    id = Utils.generate_id()

    return {
        "model": {
            "id": id,
            "children": children,
            "direction": direction,
            "justify": justify,
            "align": align,
            "style": style,
            "properties": {},
        },
        "hooks": None,
        "type": TYPE.LAYOUT_STACK,
        "interactionType": INTERACTION_TYPE.LAYOUT,
    }


def layout_form(
    id: str,
    children: Children,
    *,
    direction: LAYOUT_UTILS.Direction = LAYOUT_UTILS.DEFAULT_DIRECTION,
    justify: LAYOUT_UTILS.Justify = LAYOUT_UTILS.DEFAULT_JUSTIFY,
    align: LAYOUT_UTILS.Align = LAYOUT_UTILS.DEFAULT_ALIGN,
    style: Nullable.Style = None,
    validate: Nullable.Callable = None,
    on_submit: Nullable.Callable = None
):
    return {
        "model": {
            "id": id,
            "children": children,
            "direction": direction,
            "justify": justify,
            "align": align,
            "style": style,
            "properties": {
                "hasOnSubmitHook": on_submit is not None,
                "hasValidateHook": validate is not None,
            },
        },
        "hooks": {
            "validate": validate,
            "onSubmit": on_submit,
        },
        "type": TYPE.LAYOUT_FORM,
        "interactionType": INTERACTION_TYPE.LAYOUT,
    }
