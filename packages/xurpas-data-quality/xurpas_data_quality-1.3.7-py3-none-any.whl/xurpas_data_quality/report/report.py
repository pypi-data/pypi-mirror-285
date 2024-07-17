from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.render import render_report

from dataclasses import fields


def get_report(data: TableDescription,minimal:bool, name:str=None):
    return render_report(data=data, report_name=name, minimal=minimal)

