import inspect

from .ui import display_none, INTERACTION_TYPE
from .file import File


class Render:
    def generate_static_layout(layout, resolver):
        executed = None

        if callable(layout):
            layout_params = inspect.signature(layout).parameters
            kwargs = {}
            if "resolve" in layout_params:
                kwargs["resolve"] = resolver
            executed = layout(**kwargs)
        else:
            executed = layout

        if executed is None:
            return display_none()

        return executed

    def find_component_by_id(static_layout, component_id):
        if static_layout["model"]["id"] == component_id:
            return static_layout

        if static_layout["interactionType"] == INTERACTION_TYPE.LAYOUT:
            children = (
                static_layout["model"]["children"]
                if isinstance(static_layout["model"]["children"], list)
                else [static_layout["model"]["children"]]
            )

            for child in children:
                found = Render.find_component_by_id(child, component_id)
                if found is not None:
                    return found

        return None

    def hydrate_form_data(form_data, temp_files):
        hydrated = {}
        temp_files_to_delete = []

        for key, data in form_data.items():
            try:
                if (
                    isinstance(data, list)
                    and "fileId" in data[0]
                    and isinstance(data[0]["fileId"], str)
                ):
                    hydrated[key] = [
                        File(
                            temp_files[file["fileId"]],
                            file["fileName"],
                            file["fileType"],
                        )
                        for file in data
                    ]
                    temp_files_to_delete.extend([file["fileId"] for file in data])
                else:
                    hydrated[key] = data
            except Exception:
                hydrated[key] = data

        return hydrated, temp_files_to_delete

    def get_form_input_errors(form_data, static_layout):
        input_errors = {}
        has_errors = False

        for component_id, data in form_data.items():
            input_component = Render.find_component_by_id(static_layout, component_id)

            if (
                input_component is None
                or input_component["interactionType"] != INTERACTION_TYPE.INPUT
                or input_component["hooks"]["validate"] is None
            ):
                continue

            validatorResponse = input_component["hooks"]["validate"](data)

            if isinstance(validatorResponse, str):
                has_errors = True
                input_errors[component_id] = validatorResponse

        if has_errors:
            return input_errors

        return None

    def get_form_error(component, form_data):
        if component["hooks"]["validate"] is None:
            return None

        validator_response = component["hooks"]["validate"](form_data)

        if isinstance(validator_response, str):
            return validator_response

        return None
