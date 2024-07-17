import streamlit as st
from jinja2 import FileSystemLoader, Environment, select_autoescape, TemplateNotFound
from . import utils as utils
from .utils import fetch_key


def process_template(input_dict: dict):
    gw_streamlit = st.session_state["GWStreamlit"]
    env = Environment(
            loader=FileSystemLoader("resources/templates"),
            autoescape=select_autoescape(),
            trim_blocks=True,
    )
    template_result = list()
    if "GWStreamlit" in st.session_state:
        key = fetch_key("templates")
    else:
        key = utils.create_key("templates")
    if input_dict.get(key, None) is not None:
        for item in input_dict.get(key, []):
            if item["Selected"]:
                try:
                    template = env.get_template(item["Template"])
                    template_result.append(template.render(input_dict))
                except TemplateNotFound:
                    gw_streamlit.fetch_tab("Output").warning(f"Template - {item["Template"]} was not found")

    return template_result


def process_template_by_name(template_name, input_dict: dict):
    gw_streamlit = st.session_state["GWStreamlit"]
    env = Environment(
            loader=FileSystemLoader("resources/templates"),
            autoescape=select_autoescape(),
            trim_blocks=True,
    )
    template_result = None
    try:
        template = env.get_template(template_name)
        template_result = template.render(input_dict)
    except TemplateNotFound:
        gw_streamlit.fetch_tab("Output").warning(f"Template - {template_name} was not found")

    return template_result
