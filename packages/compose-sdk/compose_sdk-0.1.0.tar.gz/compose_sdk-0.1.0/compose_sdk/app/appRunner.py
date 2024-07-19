import asyncio
import inspect

from .appDefinition import AppDefinition
from ..api import ApiHandler
from ..core import Utils, EventType, Render, Components, INTERACTION_TYPE, TYPE


class State:
    def __init__(self, appRunner):
        self._state = {}
        self.appRunner = appRunner

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value
        asyncio.create_task(self.appRunner.set_state())

    def update(self, new_state):
        self._state.update(new_state)
        asyncio.create_task(self.appRunner.set_state())

    def __repr__(self):
        return repr(self._state)


class Page:
    def __init__(self, appRunner):
        self.appRunner = appRunner

    def add(self, layout):
        return asyncio.ensure_future(self.appRunner.render_ui(layout))

    def set_config(self, config):
        return asyncio.create_task(self.appRunner.set_config(config))


class AppRunner:
    def __init__(
        self,
        api: ApiHandler,
        appDefinition: AppDefinition,
        executionId: str,
        browserSessionId: str,
    ):
        self.api = api
        self.appDefinition = appDefinition
        self.executionId = executionId
        self.browserSessionId = browserSessionId

        self.renders = {}
        self.tempFiles = {}

    async def render_ui(self, layout):
        try:
            future = asyncio.Future()

            def resolve_render(data):
                if not future.done():
                    future.set_result(data)

            renderId = Utils.generate_id()

            static_layout = Render.generate_static_layout(layout, resolve_render)

            self.renders[renderId] = {
                "resolve": resolve_render,
                "is_resolved": False,
                "layout": layout,
                "static_layout": static_layout,
            }

            await self.api.send(
                {
                    "type": EventType.SdkToServer.RENDER_UI,
                    "ui": static_layout,
                    "executionId": self.executionId,
                    "renderId": renderId,
                },
                self.browserSessionId,
            )
        except Exception as error:
            await self.__send_error(
                f"An error occurred in the page.add fragment: {str(error)}"
            )

        return await future

    async def set_config(self, config):
        await self.api.send(
            {
                "type": EventType.SdkToServer.PAGE_CONFIG,
                "config": config,
                "executionId": self.executionId,
            },
            self.browserSessionId,
        )

    async def set_state(self):
        updatedRenders = {}

        for renderId in self.renders:
            layout = self.renders[renderId]["layout"]
            resolveFn = self.renders[renderId]["resolve"]

            # No need to check for changes for static layouts
            if not callable(layout):
                continue

            newLayout = Render.generate_static_layout(layout, resolveFn)

            updatedRenders[renderId] = newLayout

            self.renders[renderId]["staticLayout"] = newLayout

        if len(updatedRenders) > 0:
            await self.api.send(
                {
                    "type": EventType.SdkToServer.RERENDER_UI,
                    "diff": updatedRenders,
                    "executionId": self.executionId,
                },
                self.browserSessionId,
            )

    async def __send_error(self, errorMsg: str):
        await self.api.send(
            {
                "type": EventType.SdkToServer.APP_ERROR,
                "errorMessage": errorMsg,
                "executionId": self.executionId,
            },
            self.browserSessionId,
        )

    async def execute(self):
        page = Page(self)
        state = State(self)

        try:
            handler = self.appDefinition.handler
            handler_params = inspect.signature(handler).parameters
            kwargs = {}
            if "page" in handler_params:
                kwargs["page"] = page
            if "state" in handler_params:
                kwargs["state"] = state
            if "ui" in handler_params:
                kwargs["ui"] = Components

            if inspect.iscoroutinefunction(self.appDefinition.handler):
                asyncio.create_task(self.appDefinition.handler(**kwargs))
            else:
                self.appDefinition.handler(**kwargs)
        except Exception as error:
            await self.__send_error(
                f"An error occurred while running the app: {str(error)}"
            )

    async def on_click_hook(self, component_id: str, render_id: str):
        if render_id not in self.renders:
            return

        static_layout = self.renders[render_id]["static_layout"]

        component = Render.find_component_by_id(static_layout, component_id)

        if (
            component is None
            or component["interactionType"] is not INTERACTION_TYPE.BUTTON
        ):
            return

        hookFunc = component["hooks"]["onClick"]

        if hookFunc is not None:
            await self.hook_error_handler(hookFunc)

    async def on_submit_form_hook(
        self, form_component_id: str, render_id: str, form_data: dict
    ):
        if render_id not in self.renders:
            return

        hydrated, temp_files_to_delete = Render.hydrate_form_data(
            form_data, self.tempFiles
        )

        for file_id in temp_files_to_delete:
            del self.tempFiles[file_id]

        static_layout = self.renders[render_id]["static_layout"]
        component = Render.find_component_by_id(static_layout, form_component_id)

        if component is None or component["type"] != TYPE.LAYOUT_FORM:
            return

        input_errors = Render.get_form_input_errors(hydrated, static_layout)
        form_error = Render.get_form_error(component, hydrated)

        if input_errors is not None or form_error is not None:
            await self.api.send(
                {
                    "type": EventType.SdkToServer.FORM_VALIDATION_ERROR,
                    "renderId": render_id,
                    "inputComponentErrors": input_errors,
                    "formError": form_error,
                    "executionId": self.executionId,
                    "formComponentId": form_component_id,
                },
                self.browserSessionId,
            )

            return

        hookFunc = component["hooks"]["onSubmit"]

        if hookFunc is not None:
            await self.hook_error_handler(lambda: hookFunc(hydrated))

    def on_file_transfer(self, file_id: str, file_contents: bytes):
        self.tempFiles[file_id] = file_contents

    async def hook_error_handler(self, func):
        try:
            func()
        except Exception as error:
            await self.__send_error(
                f"An error occurred while executing a callback function: {str(error)}"
            )
