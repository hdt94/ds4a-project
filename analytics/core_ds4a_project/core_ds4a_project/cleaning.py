import pandas as pd

from core_ds4a_project import columns as project_columns


def cast_dates_in_place(df, format='%d/%m/%Y', exclude=[]):
    date_cols = (
        df
        .columns[df.columns.str.contains('^FECHA_')]
        .drop(exclude)
    )
    dates_df = pd.DataFrame()

    for col in date_cols:
        dates_df[col] = pd.to_datetime(df[col], format=format)

    df[date_cols] = dates_df


def cast_float_to_int_in_place(df, columns, int_type=int):
    float_df = df[columns].copy()
    df[columns] = df[columns].round().astype(int_type)
    all_int = (float_df == df[columns]).all().all()

    assert all_int == True, "There are casting errors"


def clean_tipo_vivienda(series):
    cat_type = pd.api.types.CategoricalDtype(
        categories=project_columns.TIPO_VIVIENDA_CATEGORIES)

    return (
        series
        .replace('Inmueble con Hipoteca', 'hipoteca')
        .str.upper()
        # Replace " - ", ". ", " ", and "." for "_"
        .str.replace("(\s-\s)|(\.\s)|\s|\.", "_", regex=True)
        .str.replace('\W', '', regex=True)
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .astype(cat_type)
    )


def compare_dataframes(d1, d2, sort_by):
    cols = d1.columns.sort_values()
    if (not cols.equals(d2.columns.sort_values())):
        return False

    return (
        d1[cols]
        .sort_values(by=sort_by)
        .reset_index(drop=True)
        .equals(
            d2[cols]
            .sort_values(by=sort_by)
            .reset_index(drop=True)
        )
    )


def compare_series(df, col1, col2):
    s1 = df[col1]
    s2 = df[col2]
    i_eq_with_na = s1 == s2
    i_na_s1 = s1.isna()
    i_na_s2 = s2.isna()

    i_na_any = i_na_s1 | i_na_s2
    i_eq = i_eq_with_na & (~i_na_any)
    i_diff = (~i_eq) & (~i_na_any)

    i_na_both = i_na_s1 & i_na_s2
    i_na_single = (i_na_s1 & ~i_na_s2) | (~i_na_s1 & i_na_s2)

    indices_dict = {
        "eq": i_eq,
        "diff": i_diff,
        "na_any": i_na_any,
        "na_both": i_na_both,
        "na_single": i_na_single
    }

    return indices_dict


def normalize_columns_name(columns):
    cols = (pd.Series(columns)
            .str.strip()
            .replace(project_columns.RENAMING_RAW_COLUMNS_DICT)
            .str.upper()
            .str.replace(':', '')
            # Replace " - ", ". ", " ", and "." for "_"
            .str.replace("(\s-\s)|(\.\s)|\s|\.", "_", regex=True)
            .str.normalize('NFKD')
            .str.encode('ascii', errors='ignore')
            .str.decode('utf-8')
            # Replace "FEC_" prefix for "FECHA_"
            .str.replace("^FEC_", "FECHA_", regex=True)
            )

    if isinstance(columns, list):
        return list(cols)

    return cols


def unique_columns_from_dataframes(dataframes, return_column_df=False, index=None):
    unique_columns = (pd.concat([pd.Series(df.columns) for df in dataframes])
                      .drop_duplicates()
                      .sort_values()
                      .reset_index(drop=True)
                      )

    if return_column_df == False:
        return unique_columns

    columns_df = pd.DataFrame(
        [unique_columns.isin(df.columns).values for df in dataframes],
        index=index,
        columns=unique_columns)

    return columns_df
