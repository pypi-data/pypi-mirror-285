import warnings

import pandas as pd

from xurpas_data_quality.data.dataframe import check_df,preprocess

@check_df.register
def check_df_pandas(df: pd.Dataframe) -> None:
    if not isinstance(df, pd.DataFrame):
        warnings.warm("df is not pandas.DataFrame type!")

@preprocess.register
def preprocess_pandas_df() -> None:
    pass