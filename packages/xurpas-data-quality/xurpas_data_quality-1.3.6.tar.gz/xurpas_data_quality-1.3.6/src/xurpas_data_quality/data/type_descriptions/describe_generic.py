import pandas as pd

from typing import Tuple

def describe_generic(series: pd.Series, summary: dict)-> Tuple[pd.Series, dict]:
    """
    Describes a series with information for any data type.

    Args:
        series: series to describe
        summary: dict containing the descriptions of the series so far

    Return:
        The series and the updated summary dict

    """
    value_counts = series.value_counts()

    series_len = len(series)
    distinct = series.nunique()
    missing = series.isnull().sum().sum()
    memory = series.memory_usage()

    _get_percentage = lambda divisor, dividend=series_len:(divisor/dividend)*100
    
    series_stats ={
        "distinct": distinct,
        "distinct_perc": _get_percentage(distinct),
        "missing": missing,
        "missing_perc": _get_percentage(missing),
        "memory": memory,
        "value_counts": value_counts
    }

    summary.update(series_stats)

    return summary
