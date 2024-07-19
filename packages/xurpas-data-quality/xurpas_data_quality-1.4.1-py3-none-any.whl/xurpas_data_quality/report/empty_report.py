import pandas as pd

from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer
from xurpas_data_quality.render.render_empty import render_empty

def get_empty_report(df: pd.DataFrame, name:str)-> HTMLBase:
    """
    Generates an empty report
    """

    body = HTMLContainer(type="sections",
                         container_items = render_empty(df, name))


    return HTMLBase(body=body, name='Data Report' if name is None else name)