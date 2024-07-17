from pathlib import Path
from typing import Any

import streamlit as st

from gwstreamlit._create_ui import create_ui_title, create_ui_buttons, create_ui_tabs, create_ui_inputs, generate_image
from gwstreamlit._utils import get_default_rows
from gwstreamlit.process_templates import _process_template_by_name
from gwstreamlit.utils import find_yaml_ui, find_yaml_other, \
    build_model, _fetch_key, _fetch_configs, \
    _completed_required_fields, _create_saved_state, _save_config, _load_config, _write_string, _fetch_tab, \
    _create_storage_key


class GWStreamlit:

    def create_ui(self):
        """Builds the UI for the application"""
        create_ui_title(self)
        create_ui_buttons(self)
        if not self.model.Title:
            create_ui_tabs(self)
        create_ui_inputs(self)

    def fetch_tab(self, item: Any):
        if isinstance(item, str):
            tab = self.tab_dict.get(item)
        else:
            tab_name = item.Tab
            if tab_name is None:
                tab_name = "Main"
            tab = self.tab_dict.get(tab_name)
        return tab

    def fetch_model_input(self):
        ...

    def find_model_part(self, identifier: str):
        """Finds a model part by the identifier provided. The identifier can be the code or the
        label of the item. If the item is not found None is returned.
        @param identifier: str"""
        items = [item for item in self.model.Inputs if item.Code == identifier]
        if len(items) == 0:
            items = [item for item in self.model.Inputs if item.Label == identifier]
        if len(items) == 0:
            return None
        return items[0]

    def generate_image(self, item):
        generate_image(self, item)

    def __init__(self, application: str, yaml_file: dict):
        st.session_state["GWStreamlit"] = self
        self.application = application
        self.yaml_file = yaml_file
        self.model = build_model(self.yaml_file)
        self.keys = []
        self.input_values = {}
        self.tab_dict = {}
        self.default_rows = get_default_rows(self)


def initialize(application: str, yaml_file_name: str):
    if Path(yaml_file_name).name == yaml_file_name:
        yaml_file = find_yaml_ui(yaml_file_name)
    else:
        yaml_file = find_yaml_other(yaml_file_name)
    st.session_state["GWStreamlit"] = GWStreamlit(application, yaml_file)
    st.session_state["GWStreamlit"].create_ui()


def required_fields() -> bool:
    return _completed_required_fields()


def fetch_key(ui_item: Any) -> str:
    return _fetch_key(ui_item)


def fetch_configs(application_name: str) -> list:
    return _fetch_configs(application_name)


def create_saved_state():
    """Creates a saved state for the application"""
    return _create_saved_state()


def save_config(application_name: str, file_name, config_data):
    _save_config(application_name, file_name, config_data)


def load_config(file_name):
    _load_config(file_name)


def process_template_by_name(template_name, input_dict: dict):
    return _process_template_by_name(template_name, input_dict)


def write_string(location, file_name, content, **kwargs):
    _write_string(location, file_name, content, **kwargs)


def fetch_tab(item: Any):
    return _fetch_tab(item)


def create_storage_key(value: str):
    return _create_storage_key(value)
