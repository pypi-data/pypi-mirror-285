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


def built_default_original_rows(gws) -> dict:
    default_rows_dict = {}
    for item in [table_inputs for table_inputs in gws.yaml_file.get("inputs", []) if
                 table_inputs.get("type") == "table"]:
        default_rows = item.get("default_rows", dict())
        default_rows_dict[item.get("label")] = default_rows
    return default_rows_dict


def build_default_rows(gws) -> dict:
    default_rows_dict = built_default_original_rows(gws)
    for table in [item for item in gws.model.Inputs if item.Type == "table"]:
        if table.DefaultRows is None:
            continue
        headers = [item.Header for item in table.DefaultRows if item.Header is not None]
        rows = [item.Row for item in table.DefaultRows if item.Row is not None]
        if len(headers) == 0:
            continue
        header_list = [item.strip() for item in str(headers[0]).split(",")]
        row_list = []
        for row in rows:
            row_dict = {}
            rows_items = [item.strip() for item in str(row).split(",")]
            for header in header_list:
                row_dict[header] = rows_items[header_list.index(header)]
            row_list.append(row_dict)
        default_rows_dict.update({table.Label: row_list})
    return default_rows_dict

