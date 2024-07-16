import pandas as pd
import numpy as np

from typing import Any, Dict, Optional, List

from xurpas_data_quality.data.descriptions import TableDescription



def get_table_stats(df: pd.DataFrame)->dict:
    """
    Get the overview statistics of the DataFrame.

    Args:
        df: the DataFrame object
    
    Retunr:
        dictionary object containing the table statistics
    """
    num_variables = len(df.columns)
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()

    dataset_stats = {
        "dataset_stats": {
            'num_variables': num_variables,
            'missing_cells': missing_cells,
            'missing_cells_perc' : (missing_cells/df.count().sum())*100,
            'duplicate_rows': duplicate_rows,
            'duplicate_rows_perc': (duplicate_rows/len(df))*100,
            'total_memory': df.memory_usage().sum(),
            'ave_memory': df.memory_usage().sum()/len(df)
            },
        'variable_types': {
            "numeric": df.select_dtypes(include=['int64', 'float64']).shape[1],
            "categorical": df.select_dtypes(include=['object']).shape[1]
        }
    }

    return dataset_stats

def get_correlations(df):
    corr_data = df.corr(numeric_only=True).round(3)
    return corr_data

def get_variable_info(column: pd.Series|pd.DataFrame):
    col_len = len(column)
    distinct = len(column.unique())
    missing = column.isnull().sum().sum()
    memory = column.memory_usage()
    infinite = column.isin([np.inf,-np.inf]).sum().sum()

    def _get_percentage(divisor,dividend=col_len):
        return (divisor/dividend)*100
    
    col_stats ={
        "distinct": distinct,
        "distinct_perc": _get_percentage(distinct),
        "missing": missing,
        "missing_perc": _get_percentage(missing),
        "memory": memory,
    }

    if column.dtype != 'object':
        zeros = column.value_counts().get(0, 0)
        col_stats.update({
            "infinite": infinite,
            "infinite_perc": _get_percentage(infinite),
            "mean": column.mean(),
            "minimum": column.min(),
            "maximum": column.max(),
            "zeros": zeros,
            "zero_perc": _get_percentage(zeros),
            
        })
    return col_stats

def get_variable_statistics(series: pd.Series) ->List[Dict]:
    if series.dtype=='float64' or series.dtype=='int64' or series.dtype=='int32':
        def get_MAD(df):
            med = df.median()
            med_list = [abs(item-med) for item in df]

            return pd.Series(med_list).median()

        def get_monotonicity(df):
            if df.is_monotonic_increasing:
                return "Is increasing"
            elif df.is_monotonic_decreasing:
                return "Is decreasing"
            else:
                return "Not Monotonic"
            
        minimum = series.min()
        fifth_percentile = series.quantile(0.05)
        q1 = series.quantile(0.25)
        median = series.quantile(0.5)
        q3 = series.quantile(0.75)
        ninety_fifth_percentile = series.quantile(0.95)
        maximum = series.max()
        stat_range = maximum - minimum
        interquartile_range = q3-q1
        standard_dev = series.std()
        mean = series.mean()
        cv = (standard_dev/mean)
        kurtosis= series.kurtosis()
        mad = get_MAD(series)
        skew = series.skew()
        total_sum = series.sum()
        variance = series.var()
        monotonicity = get_monotonicity(series)
        return [{
            'minimum': minimum,
            '5th_percentile': fifth_percentile,
            'Q1': q1,
            'median': median,
            'Q3': q3,
            '95th_percentile': ninety_fifth_percentile,
            'maximum': maximum,
            'range': stat_range,
            'IQR': interquartile_range,
        }, { 'std_dev': standard_dev,
            'mean': mean,
            'CV': cv,
            'kurtosis': kurtosis,
            'MAD': mad,
            'skew': skew,
            'sum': total_sum,
            'variance': variance,
            'monotonicity': monotonicity}]
    elif series.dtype == 'object':
        return [{
            'max_length': series.str.len().max()},
        {
            'min_length': series.str.len().min()
        }]

def get_extreme_values(data: pd.DataFrame) -> pd.DataFrame:
    data = data.dropna()
    minimum = data.sort_values(by='Value', ascending=True).head(10)
    maximum = data.sort_values(by='Value', ascending=False).head(10)

    return minimum, maximum

def get_variable_frequencies(series: pd.Series, num_rows: int = 10) -> pd.DataFrame:
    series_value_counts = series.value_counts()

    # Create a DataFrame from the value counts
    df_value_counts = pd.DataFrame({'Count': series_value_counts.values}, index=series_value_counts.index)

    # Calculate the frequency and add it to the DataFrame
    df_value_counts['Frequency (%)'] = (df_value_counts['Count'] / series_value_counts.sum()) * 100

    # Add a row for "Other values"
    if len(series_value_counts) > num_rows:
        other_values_count = sum(series_value_counts.values[num_rows:])
        other_values_freq = (other_values_count / series_value_counts.sum()) * 100
        other_values_df = pd.DataFrame({'Count': [other_values_count], 'Frequency (%)': [other_values_freq]}, index=['Other values (' + str(len(series_value_counts) - num_rows) + ')'])
        df_variable_frequencies = pd.concat([df_value_counts.head(num_rows), other_values_df])
    else:
        df_variable_frequencies = df_value_counts.head(num_rows)

    # Set the name of the index
    df_variable_frequencies.index.name='Value'
    df_value_counts.index.name='Value'

    min_val, max_val = get_extreme_values(df_value_counts)
    return df_variable_frequencies, min_val, max_val

def describe(df: pd.DataFrame) -> TableDescription:

    df_stats = get_table_stats(df)

    column_information = {}

    for column in df.columns:
        if df[column].dtype =='object':
            df[column] = df[column].astype(str)

        common, min_values, max_values = get_variable_frequencies(df[column])
        column_information.update({
            column: {"overview": get_variable_info(df[column]),
                     "details": get_variable_statistics(df[column]),
                     "common": common,
                     "min": min_values,
                     "max": max_values}
        })
    

    return TableDescription(df, df_stats['dataset_stats'], df_stats['variable_types'], column_information)

