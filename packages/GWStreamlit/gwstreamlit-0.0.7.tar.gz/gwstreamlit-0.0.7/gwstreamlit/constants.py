from enum import Enum


class KeyType(Enum):
    INPUT = "input"
    BUTTON = "button"
    TAB = "tab"
    STORAGE = "storage"


DEFAULT_BUTTONS = [
    {'label': 'Submit', 'on_click': 'gwstreamlit.utils:button_submit', 'type': 'submit', 'variant': 'primary'},
    {'label': 'Cancel', 'on_click': 'gwstreamlit.utils:button_cancel', 'type': 'cancel', 'variant': 'secondary'}
]

YAML_UI_LOCATION = "./resources/yaml_ui"
