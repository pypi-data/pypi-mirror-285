
from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import HTMLBase
from xurpas_data_quality.render.render_compare import render_compare

def get_comparison_report(data:TableDescription, name:str)-> HTMLBase:
    """
    Generates a comparison report
    """

    return render_compare(data, name)