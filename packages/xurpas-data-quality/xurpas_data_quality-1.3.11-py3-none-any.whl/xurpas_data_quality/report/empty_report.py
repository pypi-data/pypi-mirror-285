import pandas as pd

from xurpas_data_quality.render.renderer import HTMLBase
from xurpas_data_quality.render.render_empty import render_empty

def get_empty_report(df: pd.DataFrame, name:str)-> HTMLBase:
    """
    Generates an empty report
    """

    return render_empty(df, name)