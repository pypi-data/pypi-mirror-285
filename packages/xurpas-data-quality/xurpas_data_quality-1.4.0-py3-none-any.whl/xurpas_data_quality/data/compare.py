from typing import List

import pandas as pd

def get_compare(df: pd.DataFrame, shared_values:list):
    # for every df, get, number of unique values, number of values per table, what values exist in other tables
    
    volume_columns = df.columns[df.columns.str.contains('volume', case=False)]
    value_counts = len(df[volume_columns].index)
    unique_counts = df[volume_columns].nunique(dropna=True).iloc[0]
    unique_counts_perc = (unique_counts/value_counts)*100

    unshared_df = df[~df[volume_columns].isin(shared_values)]
    unshared_values_series = unshared_df[volume_columns].dropna()
    unshared_values = unshared_values_series.squeeze().to_list()  if isinstance(unshared_values_series.squeeze(), pd.Series) else unshared_values_series.squeeze()
    unshared_values_rows = unshared_df.dropna(subset=['volume']).index
    unshared_df = df.loc[unshared_values_rows]
    
    return {
        'df': df,
        'unshared_df':unshared_df,
        'value_count':value_counts,
        'distinct_count':unique_counts,
        'distinct_perc': unique_counts_perc,
        'unshared_values': unshared_values
    }