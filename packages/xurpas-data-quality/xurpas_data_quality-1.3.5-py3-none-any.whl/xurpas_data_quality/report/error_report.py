from pandas import DataFrame

from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import HTMLBase
from xurpas_data_quality.render.render_error import render_error

def get_error_report(df:DataFrame,invalid_df:DataFrame, errors:list,name:str, is_empty:bool, minimal:bool)-> HTMLBase:
    """
    Generates an error report
    """

    return render_error(df, invalid_df, errors,name,is_empty,minimal)