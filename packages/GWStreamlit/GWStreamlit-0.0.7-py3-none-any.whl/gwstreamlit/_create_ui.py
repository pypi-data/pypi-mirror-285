from typing import Optional

import streamlit as st
import pandas as pd

from gwstreamlit._utils import construct_function, option_function
from gwstreamlit.models import BaseConfig, InputFieldsBase
from gwstreamlit.utils import disabled, build_label, fetch_boolean


def create_ui_tabs(gws):
    """Creates a list of tabs to be used in the UI"""
    tab_dict = {item.Tab: None for item in gws.model.Inputs if item.Tab is not None}
    if len([item for item in gws.model.Inputs if item.Tab is None]) > 0:
        tab_dict["Main"] = None

    for tab in gws.model.Tabs:
        tab_dict[tab.Label] = None
    tab_dict["Output"] = None

    tabs = st.tabs(tab_dict.keys())
    tab_position = 0

    for tab in tab_dict.keys():
        tab_dict[tab] = tabs[tab_position]
        tab_position += 1
    gws.tab_dict = tab_dict


def create_ui_title(gws):
    """Creates a title for the UI page and a description if it exists in the YAML file.
    If the title exists in the yaml file no buttons are generated."""
    st.title(gws.model.Name)
    if gws.model.Description is not None:
        st.markdown(gws.model.Description)
    if gws.model.Concept is not None:
        st.write(f"Concept by: {gws.model.Concept}")
    if gws.model.Developer is not None:
        st.write(f"Developed by: {gws.model.Developer}")


def create_ui_buttons(gws):
    """Generates a set of buttons based on the YAML file provided"""
    columns = st.columns([1, 1, 1, 1, 1])
    column_index = 0
    for button in gws.model.Buttons:
        with columns[column_index]:
            on_click = construct_function(button.OnClick)
            st.button(f"{button.Label}", key=button.Key, on_click=on_click, type=button.Variant,
                      use_container_width=True)
        column_index += 1


def create_ui_inputs(gws):
    """Main processing for the inputs defined in the yaml file. Each type of input
    is handled separately. Each input has a key generated that corresponds to the label or code
    and the state name defined in the main module for the application"""

    if gws.model.Inputs is None:
        return
    for ui_item in gws.model.Inputs:
        build_input(gws, ui_item)


def build_input(gws, ui_item):
    """Main processing for the inputs defined in the yaml file. Each type of input
    is handled separately. Each input has a key generated that corresponds to the label or code
    and the state name defined in the main module for the application"""
    if ui_item.Key not in gws.input_values.keys():
        gws.input_values[ui_item.Key] = None

    if ui_item.Type == 'text_input':
        generate_text_input(gws, ui_item, None)

    if ui_item.Type == 'text_area':
        generate_text_input(gws, ui_item, None, True)

    if ui_item.Type == "selectbox":
        generate_selectbox(gws, ui_item, None)

    if ui_item.Type == "image":
        generate_image(gws, ui_item)

    if ui_item.Type == "checkbox":
        generate_checkbox(gws, ui_item, None)

    if ui_item.Type == "toggle":
        generate_checkbox(gws, ui_item, None, True)

    if ui_item.Type == "integer_input":
        generate_integer_input(gws, ui_item, None)

    if ui_item.Type == "file_upload":
        generate_file_upload(gws, ui_item, None)

    if ui_item.Type == "multiselect":
        generate_selectbox(gws, ui_item, None, True)

    if ui_item.Type == "table":
        generate_table(gws, ui_item)

    return ui_item.Key


def generate_text_input(gws, item, input_values, text_area=False):
    """text input processing. The default value is used if it exists in the YAML file. If the value is already
    in the input_values dictionary it is used instead of the default value. The on_change function is constructed
    based on the name provided in the YAML file. The input is disabled if the immutable flag is set in
    the YAML file."""
    default_value = item.Default
    if item.DefaultFunction:
        defined_function = construct_function(item.DefaultFunction)
        default_value = defined_function()
    if gws.input_values.get(item.Key, None) is not None:
        default_value = gws.input_values[item.Key]
    on_change = construct_function(item.OnChange)
    disabled_input = disabled(item)
    if text_area:
        gws.input_values[item.Key] = gws.fetch_tab(item).text_area(build_label(item), default_value, key=item.Key,
                                                                   on_change=on_change, disabled=disabled_input)
    else:
        gws.input_values[item.Key] = gws.fetch_tab(item).text_input(build_label(item), default_value,
                                                                    key=item.Key,
                                                                    on_change=on_change, disabled=disabled_input)


def generate_image(gws, item):
    if item.Image is not None:
        caption = f"{build_label(item)} - {item.Image}"
        gws.fetch_tab(item).image(item.Image, caption=caption)


def generate_checkbox(gws, item: BaseConfig, input_values, toggle=False):
    """Check Box Processing. The default value is used if it exists in the YAML file. If the value is already
    in the input_values dictionary it is used instead of the default value. The on_change function is constructed
    based on the name provided in the YAML file. The input is disabled if the immutable flag is set in the
    YAML file."""
    default_value = item.Default
    if gws.input_values.get(item.Key, None) is not None:
        default_value = gws.input_values[item.Key]
    on_change = construct_function(item.OnChange)
    disabled_field = fetch_boolean(item.Immutable)
    if not toggle:
        gws.input_values[item.Key] = gws.fetch_tab(item).checkbox(build_label(item), default_value, key=item.Key,
                                                                  on_change=on_change, disabled=disabled_field)
    else:
        gws.input_values[item.Key] = gws.fetch_tab(item).toggle(build_label(item), default_value, key=item.Key,
                                                                on_change=on_change, disabled=disabled_field)


def generate_file_upload(gws, item, input_values):
    """File Upload Processing. The extension is used to set the type of file that can be uploaded.
    The on_change function is constructed based on the name provided in the YAML file.
    The input is disabled if the immutable flag is set in the YAML file."""
    on_change = construct_function(item.OnChange)
    gws.input_values[item.Key] = gws.fetch_tab(item).file_uploader(build_label(item), type=item.Extension,
                                                                   accept_multiple_files=False, key=item.Key,
                                                                   on_change=on_change)


def generate_integer_input(gws, item: InputFieldsBase, input_values):
    """Integer Input Processing. The default value is used if it exists in the YAML file. If the value is already
    in the input_values dictionary it is used instead of the default value. The on_change function is constructed
    based on the name provided in the YAML file. The input is disabled if the immutable flag is set in the
    YAML file. The min and max values are used to set the range of the input."""
    if item.Min:
        min_value = item.Min
    else:
        min_value = 0

    if item.Max:
        max_value = item.Max
    else:
        max_value = 100

    if gws.input_values.get(item.Key, None):
        default_value = gws.input_values[item.Key]
    else:
        default_value = min_value
    on_change = construct_function(item.OnChange)
    disabled_field = fetch_boolean(item.Immutable)
    gws.input_values[item.Key] = gws.fetch_tab(item).number_input(build_label(item), value=default_value,
                                                                  key=item.Key, step=1, min_value=min_value,
                                                                  max_value=max_value, on_change=on_change,
                                                                  disabled=disabled_field)


def generate_selectbox(gws, item: BaseConfig, input_values, multiselect=False):
    """select box processing. The default value is used if it exists in the YAML file. If the value is already
    in the input_values dictionary it is used instead of the default value. The on_change function is constructed
    based on the name provided in the YAML file. The input is disabled if the immutable flag is set in the
    YAML file.
    If the options are defined as a function the function is called to get the options. If the default value is not
    in the options list the first option is used as the default value."""
    default_value = item.Default
    options_dict = options_list(gws, item)
    options = options_dict.get("options")
    default_value = options_dict.get("default_value")
    on_change = construct_function(item.OnChange)
    if options is not None and len(options) > 0 and default_value is not None:
        index_value = options.index(default_value)
    else:
        index_value = None
    with st.container():
        disabled_field = fetch_boolean(item.Immutable)
        if multiselect:
            gws.input_values[item.Key] = gws.fetch_tab(item).multiselect(build_label(item), options,
                                                                         default_value,
                                                                         key=item.Key, on_change=on_change,
                                                                         disabled=disabled_field)
        else:
            gws.input_values[item.Key] = gws.fetch_tab(item).selectbox(build_label(item), options, index_value,
                                                                       key=item.Key,
                                                                       on_change=on_change,
                                                                       disabled=disabled_field)


def generate_table(gws, item):
    """Main Processing for table generation. Each table is backed by a dataframe that is stored
    in self.data_frame."""
    default_rows = gws.default_rows.get(item.Label, dict())
    generate_dataframe(gws, item, default_rows)


def generate_dataframe(gws, item: InputFieldsBase, default_rows: dict):
    """Generate the Table Dataframe. The default rows are used to populate the dataframe if it is empty. The columns
    are generated based on the YAML file provided. The dataframe is stored in self.data_frame and can be updated"""
    if item.Columns is None:
        return

    if item.Columns[0].Function is not None:
        defined_function = construct_function(item.Columns[0].Function)
        columns = defined_function()
    else:
        columns = [entity_item.Label for entity_item in item.Columns]
    df_key = f"{item.Key}_df"
    if df_key in st.session_state.keys():
        df = st.session_state[df_key]
    else:
        df = pd.DataFrame(columns=columns, data=default_rows)
        if item.Order:
            df.sort_values(by=[item.Order], inplace=True, ignore_index=True)

    column_config = create_column_config(gws, item.Columns)
    gws.fetch_tab(item).markdown(f"**{item.Label}**")

    st.session_state[df_key] = df
    if item.Immutable:
        if default_rows:
            num_rows = len(default_rows)
        else:
            num_rows = 0
        gws.fetch_tab(item).data_editor(st.session_state[df_key], num_rows=num_rows,
                                        column_config=column_config, use_container_width=True, key=item.Key)
    else:
        gws.fetch_tab(item).data_editor(st.session_state[df_key], num_rows="dynamic", column_config=column_config,
                                        use_container_width=True, key=item.Key)


def create_column_config(gws, columns: list[InputFieldsBase]):
    """Define the column configuration for the data editor, multiselect is not supported in the data editor and
    list column is used"""
    column_config = {}
    for column_item in columns:
        column = column_item.Label
        if column is None:
            column = column_item
        if column_item.InputOptions:
            options_dict = options_list(gws, column_item)
            options = options_dict.get("options")
            default_value = options_dict.get("default_value")
            column_config[column] = st.column_config.SelectboxColumn(options=options, default=default_value)
        if column_item.Type == "checkbox":
            column_config[column] = st.column_config.CheckboxColumn(default=False)
        if column_item.Type == "integer_input":
            min_value = column_item.get('min', -1)
            max_value = column_item.get('max', 100)
            column_config[column] = st.column_config.NumberColumn(max_value=max_value, min_value=min_value, step=1,
                                                                  default=-1)
        if column_item.Type == "multiselect":
            column_config[column] = st.column_config.ListColumn()
    return column_config


def options_list(gws, item):
    defined_option_function = option_function(item)
    default_value: Optional[str] = None
    if defined_option_function is None:
        options = [option.Value for option in item.InputOptions]
        if item.Default not in options:
            default_value = item.InputOptions[0].Value
        if gws.input_values.get(item.Key, None) is not None:
            default_value = gws.input_values[item.Key]
    else:
        options = defined_option_function()
    return {"options": options, "default_value": default_value}
