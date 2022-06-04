import pandas as pd


def normalize_columns_name(columns):
    cols = (pd.Series(columns)
            .str.upper()
            .str.replace('\s', '_', regex=True)
            )

    if isinstance(columns, list):
        return list(cols)

    return cols
