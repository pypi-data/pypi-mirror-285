from .buttonInteraction import button_default, button_form_submit
from .displayInteraction import (
    display_code,
    display_header,
    display_image,
    display_json,
    display_markdown,
    display_none,
    display_spinner,
    display_text,
)
from .layoutInteraction import layout_form, layout_stack
from .inputInteraction import (
    input_email,
    input_text,
    input_number,
    input_file_drop_zone,
    input_url,
    select_dropdown_multi,
    select_dropdown_single,
    table,
    dataframe,
    radio_group,
)
from .dynamicInteraction import dynamic_cond


class _Components:
    # Inputs
    @property
    def text_input(self):
        return input_text

    @property
    def email_input(self):
        return input_email

    @property
    def number_input(self):
        return input_number

    @property
    def url_input(self):
        return input_url

    @property
    def file_drop_zone(self):
        return input_file_drop_zone

    @property
    def radio_group(self):
        return radio_group

    @property
    def multi_select_box(self):
        return select_dropdown_multi

    @property
    def select_box(self):
        return select_dropdown_single

    @property
    def table(self):
        return table

    @property
    def dataframe(self):
        return dataframe

    # Display
    @property
    def code(self):
        return display_code

    @property
    def header(self):
        return display_header

    @property
    def image(self):
        return display_image

    @property
    def json(self):
        return display_json

    @property
    def markdown(self):
        return display_markdown

    @property
    def spinner(self):
        return display_spinner

    @property
    def text(self):
        return display_text

    # Layout
    @property
    def form(self):
        return layout_form

    @property
    def stack(self):
        return layout_stack

    # Button
    @property
    def button(self):
        return button_default

    @property
    def submit_button(self):
        return button_form_submit

    # Dynamic
    @property
    def cond(self):
        return dynamic_cond


Components = _Components()
ComponentsType = type(Components)
