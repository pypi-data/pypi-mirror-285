import json
from pathlib import Path
from typing import Optional, Any

import streamlit as st

from gw_streamlit._create_ui import create_ui_title, create_ui_buttons, create_ui_tabs, create_ui_inputs, generate_image
from gw_streamlit._utils import get_default_rows
from gw_streamlit.utils import to_list, codeify_string, \
    updated_edited_rows, get_config_path, update_data_editor, build_model, find_yaml_ui, find_yaml_other, \
    create_saved_state



class GWStreamlit:

    def create_ui(self):
        """Builds the UI for the application"""
        create_ui_title(self)
        create_ui_buttons(self)
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

    def create_saved_state(self):
        """Creates a saved state for the application"""
        create_saved_state()

    def load_config(self, file_name):
        """Loads the configuration from a JSON file, or returns an empty dictionary if the file does not exist."""
        if file_name is None:
            return
        if Path(file_name).name == file_name:
            directory = codeify_string(input_string=self.application)
            config_path = get_config_path(directory, file_name)
        else:
            config_path = file_name
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                for key, value in config.items():
                    if str(key).startswith("input_"):
                        if type(value) is list:
                            update_data_editor(key=key, replace_values=value)
                        else:
                            st.session_state[key] = value
        except FileNotFoundError:
            return

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
