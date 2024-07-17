import json
import pathlib
import platform
import os
from typing import Any

import yaml
import streamlit as st
from pathvalidate import is_valid_filepath

from gwstreamlit import constants
from gwstreamlit.constants import KeyType
from gwstreamlit.models import InputFieldsBase, Tab, Button, BaseConfig, UserInterface


def codeify_string(input_string: str):
    new_string = input_string.replace(' ', '_').lower().replace("_/_", "_")
    return new_string


def __create_key(ui_item: any) -> str:
    """Create a key for the item, the key is used to store the value in the session state
    @param ui_item: The item to create the key for"""
    gw_streamlit = st.session_state["GWStreamlit"]
    if isinstance(ui_item, str):
        model_item = gw_streamlit.find_model_part(ui_item)
        return __create_key(model_item)
    if isinstance(ui_item, InputFieldsBase):
        return create_key_process(KeyType.INPUT, ui_item, ["Code", "Name", "Label"])
    if isinstance(ui_item, Tab):
        return create_key_process(KeyType.TAB, ui_item, ["Code", "Label"])
    if isinstance(ui_item, Button):
        return create_key_process(KeyType.BUTTON, ui_item, ["Code", "Label"])


def create_simple_key(key_type: KeyType, value: str):
    gw_streamlit = st.session_state["GWStreamlit"]
    application = gw_streamlit.application
    key = codeify_string(input_string=f"{key_type.value}_{application}_{value}")
    return key


def _create_storage_key(value: str):
    gw_streamlit = st.session_state["GWStreamlit"]
    application = gw_streamlit.application
    key = codeify_string(input_string=f"{KeyType.STORAGE.value}_{application}_{value}")
    return key


def create_key_process(key_type: KeyType, ui_item: any, keys: list):
    gw_streamlit = st.session_state["GWStreamlit"]
    application = gw_streamlit.application
    value = "undefined"
    for key in keys:
        if key in ui_item.model_fields.keys():
            value = getattr(ui_item, key)
            if value is not None:
                break
    key = codeify_string(input_string=f"{key_type.value}_{application}_{value}")
    return key


def read_yaml(yaml_file: str):
    with open(yaml_file, 'r') as file:
        yaml_data = yaml.safe_load(file)
        return yaml_data


def get_config_path(directory, file_name: str):
    """Returns the path to the configuration file depending on the operating system."""
    if file_name.endswith('.json'):
        config_filename = file_name
    else:
        config_filename = f"{file_name}.json"
    if platform.system() == 'Windows':
        # On Windows, it's typical to store config files in the AppData directory
        config_directory = os.path.join(os.getenv('APPDATA'), directory)
    elif platform.system() == 'Darwin':
        # On macOS, it's typical to store config files in the Application Support directory
        user_directory = os.path.expanduser('~/Library/Application Support/')
        config_directory = os.path.join(user_directory, "Field Framework", directory)
    else:
        raise OSError("Unsupported operating system")

    if not os.path.exists(config_directory):
        os.makedirs(config_directory)  # Create the directory if it does not exist

    return os.path.join(config_directory, config_filename)


def disabled(item: BaseConfig) -> bool:
    """Check if the item is enabled"""
    disabled_value = fetch_boolean(getattr(item, "immutable", False))
    if item.Enabled is not None:
        ...
        # if st.session_state.get(create_key(item.get("enabled")), None) is None:
        #     disabled_value = True
        # else:
        #     disabled_value = False
    return disabled_value


def fetch_boolean(value):
    if type(value) is bool:
        return value
    if type(value) is str:
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False


class InputField:
    pass


def build_label(item: BaseConfig):
    if item.Required:
        return f"{item.Label} *"
    else:
        return item.Label





def to_list(item_value) -> list:
    """Convert the item value to a list if it is not already a list
    :arg item_value: Value to be converted to a list
    """
    if type(item_value) is list:
        return item_value
    else:
        return [item_value]


def updated_edited_rows(df, edited_item):
    """Update the edited rows in the dataframe"""
    for key, value in edited_item.items():
        for item_key, item_value in value.items():
            df.loc[key, item_key] = item_value
    return df


def update_data_editor(*, key: str, replace_values: dict):
    update_dataframe(key=key, update_rows=replace_values)


def update_dataframe(key: str, update_rows: dict):
    """Updates a dataframe, the dataframe should have been built and stored in self.data_frame
    The original rows are removed from the dataframe and the new rows are added. As there can be a missmatch in the
    index sizes this is the easiest way to perform the update of the dataframe. This function is only used to update
    the dataframe in the session_state from a saved configuration, otherwise the changes will be available in the
    streamlit data_edit component.
    :param key: The key used to store the dataframe in the session_state
    :param update_rows: The rows to be updated in the dataframe"""
    df_key = f"{key}_df"
    if st.session_state.get(df_key, None) is None:
        return

    st.session_state.get(df_key)

    original_index = st.session_state.get(df_key).index
    original_index_list = list(range(original_index.start, original_index.stop))
    st.session_state.get(df_key).drop(original_index_list, inplace=True)
    for item in update_rows:
        st.session_state.get(df_key).loc[len(st.session_state.get(df_key))] = item
    st.session_state.get(df_key).reset_index(drop=True, inplace=True)


def _load_config(file_name):
    gws = st.session_state["GWStreamlit"]
    if file_name is None:
        return
    if pathlib.Path(file_name).name == file_name:
        directory = codeify_string(input_string=gws.application)
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


def _completed_required_fields() -> bool:
    """Show the required fields that are not filled
    @return: True if all required fields are filled, False if there are required fields that are not filled"""
    required_list = []
    model = st.session_state["GWStreamlit"].model
    for input_field in [model_input for model_input in model.Inputs if model_input.Required]:
        if input_field.Required and st.session_state.get(input_field.Key) is None:
            required_list.append(input_field.Label)
    if len(required_list) > 0:
        st.error(f"The following required fields are not filled: {', '.join(required_list)}")
        return False
    return True


def _write_string(location, file_name, content, **kwargs):
    """Write a string to a file, there are multiple checks to ensure the file is written correctly
    If the path is invalid it will return an error message, if the contents to write are None it will return a message
    if the location is valid but does not exist it will be created.

    Args: location: str: The location to write the file
          file_name: str: The name of the file
          content: str: The content to write to the file
          **kwargs: dict: Additional arguments to specify the package and extension
    """
    gw_streamlit = st.session_state["GWStreamlit"]
    for key, value in kwargs.items():
        if key == "package":
            package_parts = value.split(".")
            for package_part in package_parts:
                location = os.path.join(location, package_part)
        if key == "extension":
            file_name = f"{file_name}.{value}"

    if content is None:
        gw_streamlit.fetch_tab("Output").write(f"File content for: {location}/{file_name} is None")
        return
    if not is_valid_filepath(location, platform="auto"):
        gw_streamlit.fetch_tab("Output").error("Source Location is an invalid path")
        return
    is_exist = os.path.exists(location)
    if not is_exist:
        os.makedirs(location)
        gw_streamlit.fetch_tab("Output").write(f"Directory created: {location}")
    with open(f"{location}/{file_name}", "w") as file:
        file.write(content)
    gw_streamlit.fetch_tab("Output").write(f"File created: {location}/{file_name}")


def _fetch_key(ui_item: Any):
    """Fetch the key for the item, if the item is a string it will find the item in the model and return the key
    otherwise the key will be returned from the item
    @param ui_item: Model part or part identifier to fetch the key for"""
    if isinstance(ui_item, str):
        item_code = codeify_string(ui_item)
        gw_streamlit = st.session_state["GWStreamlit"]
        model_item = gw_streamlit.find_model_part(item_code)
        return _fetch_key(model_item)
    else:
        return ui_item.Key




def build_model(yaml_file):
    """Build the model from the yaml file, and update to add the key and code if missing to the model
    @param yaml_file: The yaml file to build the model from"""
    model = UserInterface.model_validate(yaml_file)
    for input_model in model.Inputs:
        if input_model.Code is None:
            model_code = codeify_string(input_model.Label)
            setattr(input_model, "Code", model_code)
        model_key = __create_key(input_model)
        setattr(input_model, "Key", model_key)

    for button_model in model.Buttons:
        if button_model.Code is None:
            model_code = codeify_string(button_model.Label)
            setattr(button_model, "Code", model_code)
        model_key = __create_key(button_model)
        setattr(button_model, "Key", model_key)
    return model


def find_yaml_ui(yaml_file_name: str):
    templates = st.session_state.get("templates", list_files(constants.YAML_UI_LOCATION, ['.yaml', '.yml']))
    yaml_object_list = [template for template in templates if template["name"] == yaml_file_name]

    if len(yaml_object_list) == 0:
        st.session_state["template_selection"] = None
        return
    yaml_object = yaml_object_list[0]
    st.session_state["template_selection"] = yaml_object["name"]
    return yaml_object


def find_yaml_other(yaml_file_name: str):
    yaml_object = load_yaml(yaml_file_name)
    st.session_state["template_selection"] = yaml_object["name"]
    return yaml_object


def list_files(directory_path, file_types: list):
    found_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_extension = pathlib.Path(file).suffix
            if file_extension in file_types:
                found_files.append(load_yaml(os.path.join(str(root), file)))

    return found_files


def load_yaml(file_path: str):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def _create_saved_state():
    """Creates a saved state for the application"""
    saved_dict = {}
    for key, value in [item for item in st.session_state.items()]:
        if key.startswith("input_"):
            if key.endswith("_df"):
                continue
            if len([item for item in st.session_state.keys() if item == f"{key}_df"]) > 0:
                df = st.session_state[f"{key}_df"]
                for del_index in to_list(st.session_state[key]['deleted_rows']):
                    df.drop(del_index, inplace=True)
                for added_item in to_list(st.session_state[key]['added_rows']):
                    if added_item:
                        df.loc[len(df)] = added_item
                for edited_item in to_list(st.session_state[key]['edited_rows']):
                    if edited_item:
                        updated_edited_rows(df, edited_item)
                df.reset_index(drop=True, inplace=True)
                saved_dict[key] = df.to_dict("records")
            else:
                saved_dict[key] = value

        if key.startswith("storage_"):
            saved_dict[key] = value
    return saved_dict


def _fetch_configs(application_name: str):
    """List of saved configurations for the application"""
    file_list = []
    directory = codeify_string(application_name)
    config_path = get_config_path(directory, 'temp.json')
    for root, dirs, files in os.walk(os.path.dirname(config_path)):
        for file in files:
            if file.endswith('.json'):
                file_list.append(file)
    return file_list


def _save_config(application_name: str, file_name, config_data):
    """Saves the given configuration data to a JSON file."""
    if file_name is None:
        return
    directory = codeify_string(application_name)
    config_path = get_config_path(directory, file_name)
    with open(config_path, 'w') as file:
        json.dump(config_data, file, indent=4)


def _fetch_tab(item: Any):
    if isinstance(item, str):
        tab = st.session_state["GWStreamlit"].tab_dict.get(item)
    else:
        tab_name = item.Tab
        if tab_name is None:
            tab_name = "Main"
        tab = st.session_state["GWStreamlit"].tab_dict.get(tab_name)
    return tab

