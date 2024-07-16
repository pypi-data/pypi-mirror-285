from dataclasses import dataclass
from typing import Any, Dict, Optional, List

import pandas as pd

@dataclass
class TableDescription:
    df: pd.DataFrame
    dataset_statistics: Dict
    correlation: pd.DataFrame
    alerts: List
    variable_types: Dict
    variables: Optional[Dict] = None
    comparison: Dict = None
    shared_values: List[int] = None

@dataclass
class ComparisonDescription:
    df: List[pd.DataFrame]
    value_count: List[int]
    distinct_count: List[int]
    shared_values: List[int]