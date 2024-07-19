class SDK_TO_SERVER_EVENT_TYPE:
    APP_ERROR = "aa"
    INITIALIZE = "ab"
    RENDER_UI = "ac"
    FORM_VALIDATION_ERROR = "ad"
    RERENDER_UI = "ae"
    PAGE_CONFIG = "af"


class SERVER_TO_SDK_EVENT_TYPE:
    START_EXECUTION = "aa"
    ON_CLICK_HOOK = "ab"
    ON_SUBMIT_FORM_HOOK = "ac"
    FILE_TRANSFER = "ad"


class EventType:
    SdkToServer = SDK_TO_SERVER_EVENT_TYPE
    ServerToSdk = SERVER_TO_SDK_EVENT_TYPE
