from pathlib import Path
from typing import Union

from streamlit.components.v1 import components

build_path = Path(__file__).parent / 'build'
_component_func = components.declare_component("get_fragment", path=str(build_path))


def split_string_to_dict(input_string):
    result_dict = {}
    input_string = input_string.lstrip('#')
    pairs = input_string.split("&")
    for pair in pairs:
        key, value = pair.split("=")
        result_dict[key] = value
    return result_dict


def get_fragments() -> Union[str, dict, None]:
    component_value = _component_func()
    if not None:
        import re
        pattern = r'^#[^=&]+=[^&=]+(?:&[^=&]+=[^&=]+)*$'
        if re.match(pattern, component_value):
            return split_string_to_dict(component_value)
    return component_value
