from typing import TYPE_CHECKING, Union, Callable
from .displayInteraction import display_none

if TYPE_CHECKING:
    from ..components import ComponentsType

Child = type["ComponentsType"]


def dynamic_cond(
    condition: Union[bool, Callable[[], bool]],
    *,
    true: Union[Child, None] = None,
    false: Union[Child, None] = None
):
    condition_result = condition() if callable(condition) else condition

    if condition_result:
        if true is None:
            return display_none()
        return true
    else:
        if false is None:
            return display_none()
        return false
