from gwstreamlit.models import BaseConfig


def construct_function(function_name):
    if function_name is None:
        return None
    function_module = function_name.split(":")[0]
    function_function = function_name.split(":")[1]
    defined_function = getattr(__import__(function_module, globals(), locals(), [function_function]), function_function)
    return defined_function


def option_function(item: BaseConfig):
    if len(item.InputOptions) == 1 and item.InputOptions[0].Function is not None:
        function_name = item.InputOptions[0].Function
        defined_function = construct_function(function_name)
        return defined_function
    else:
        return None


def get_default_rows(gws):
    default_rows_dict = {}
    for item in [table_inputs for table_inputs in gws.yaml_file.get("inputs", []) if
                 table_inputs.get("type") == "table"]:
        default_rows = item.get("default_rows", dict())
        default_rows_dict[item.get("label")] = default_rows
    return default_rows_dict
