from typing import Literal, Optional, Union
import pandas as pd
from tabulate import tabulate


Format = Optional[Union[
    Literal['json'],
    Literal['csv'],
]]


def format_dataframe(df: pd.DataFrame, format: Format = None):
    if format == 'json':
        output = df.to_json(orient='index', indent=2)
    elif format == 'csv':
        output = df.to_csv()
    else:
        output = tabulate(df, headers=df.columns, tablefmt=format)
    return output
