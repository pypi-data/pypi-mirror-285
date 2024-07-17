from xurpas_data_quality.render.render import render_report
from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import BaseRenderer, HTMLBase,HTMLContainer
from xurpas_data_quality.render.render_error import render_error

def get_error_report(data:TableDescription, invalid_data:TableDescription, errors:list,name:str, is_empty:bool, minimal:bool)-> BaseRenderer:
    """
    Generates an error report
    """

    content = [render_error(data, invalid_data, errors)]
    content.extend(render_report(data=data, report_name=name, minimal=minimal))
    body = HTMLContainer(
        type="sections",
        container_items = content
    )


    return HTMLBase(body=body, name='Data Report' if name is None else name)