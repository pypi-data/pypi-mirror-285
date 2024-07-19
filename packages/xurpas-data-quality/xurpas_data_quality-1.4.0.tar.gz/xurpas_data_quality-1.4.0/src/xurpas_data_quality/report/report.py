from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.render import render_report
from xurpas_data_quality.render.renderer import HTMLContainer, HTMLBase

from dataclasses import fields


def get_report(data: TableDescription,minimal:bool, name:str=None):
    """
    Generates a report
    """

    body = HTMLContainer(
        type="sections",
        container_items = render_report(data=data, report_name=name, minimal=minimal)
    )

    return HTMLBase(body=body, name='Data Report' if name is None else name)
