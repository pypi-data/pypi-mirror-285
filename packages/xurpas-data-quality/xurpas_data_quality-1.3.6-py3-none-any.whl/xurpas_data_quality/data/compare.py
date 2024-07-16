from typing import List

import pandas as pd

def get_compare(df: pd.DataFrame):
    # for every df, get, number of unique values, number of values per table, what values exist in other tables
    
    value_counts = len(df['volume'].value_counts(dropna=True))
    unique_counts = df['volume'].nunique(dropna=True)

    return {
        'df': df,
        'value_count':value_counts,
        'distinct_count':unique_counts
    }

    