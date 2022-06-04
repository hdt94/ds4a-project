import functools

import pandas as pd


def normalize_columns_name(columns):
    renaming_dict = {
        "Cod_modalidad": "MODALIDAD_COD",
        "Cod_tipoCliente": "TIPO_CLIENTE_COD",
        "Garntia_real": "GARANTIA_REAL",
        "Homologacion Documento de Identidad": "ID_CLIENTE",
        "Nom_tipoCliente": "TIPO_CLIENTE_NOM",
        "Sucurs": "SUCURSAL_COD",
        # "Sucursal Real": "SUCURSAL",
        # "Sucursal.1": "SUCURSAL",
        # "Sucursales": "SUCURSAL",
        "Ubicacio cliente": "UBICACION_CLIENTE",
        "ubicacio cliente": "UBICACION_CLIENTE",
        "ubicacio_cliente": "UBICACION_CLIENTE",
        "ï»¿Tipo": "TIPO",
    }
    cols = (pd.Series(columns)
            .str.strip()
            .replace(renaming_dict)
            .str.upper()
            # Replace " - ", " ", and "." for "_"
            .str.replace("(\s-\s)|\s|\.", "_", regex=True)
            .str.normalize('NFKD')
            .str.encode('ascii', errors='ignore')
            .str.decode('utf-8')
            )

    if isinstance(columns, list):
        return list(cols)

    return cols


def unique_columns_from_dataframes(dataframes, return_column_df=False, index=None):
    columns_2d = [df.columns.values for df in dataframes]
    columns = pd.Index(functools.reduce(
        lambda all, cols: all.union(set(cols)),
        columns_2d[1:],
        set(columns_2d[0])
    )).sort_values()

    if return_column_df == False:
        return columns


    columns_df = pd.DataFrame([columns.isin(cols) for cols in columns_2d],
                            index=index,
                            columns=columns)

    return columns_df


