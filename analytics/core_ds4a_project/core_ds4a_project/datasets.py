import glob
import json
import os

import numpy as np
import pandas as pd

from core_ds4a_project import cleaning
from core_ds4a_project import columns as project_columns
from core_ds4a_project import location
from core_ds4a_project.cleaning import normalize_columns_name


class RelationsFilter(object):
    _DEFAULT_FILE_NAME = 'dict-valid-relations-identifiers.json'

    def __init__(self, valid_cliente_ids, valid_obligacion_ids):
        self.cids = valid_cliente_ids
        self.oids = valid_obligacion_ids

    def filter_dataframe(self, dataset, dataframe):
        valid_cliente_ids = self.cids
        valid_obligacion_ids = self.oids

        cliente_query = 'CLIENTE.isin(@valid_cliente_ids)'
        obligacion_query = 'OBLIGACION.isin(@valid_obligacion_ids)'
        dataset_query_dict = {
            "cartera": f'{cliente_query} & {obligacion_query}',
            "castigo": obligacion_query,
            "colocacion": obligacion_query,
            "contacto": cliente_query,
            "negocio": cliente_query,
        }

        dataframe = dataframe.query(dataset_query_dict[dataset])

        return dataframe

    def save(self, dir_path, file_name=None):
        file_name = file_name or RelationsFilter._DEFAULT_FILE_NAME
        data = {
            "valid_cliente_ids": self.cids,
            "valid_obligacion_ids": self.oids,
        }

        with open(f'{dir_path}/{file_name}', 'w') as f:
            json.dump(data, f, ensure_ascii=False)

    @staticmethod
    def load(dir_path, file_name=None):
        file_name = file_name or RelationsFilter._DEFAULT_FILE_NAME

        with open(f'{dir_path}/{file_name}', 'r') as f:
            valid_ids_dict = json.load(f)

        relations_filter = RelationsFilter(**valid_ids_dict)

        return relations_filter


def extract_cartera_date_cierre(cartera_files):
    month_digit_dict = {
        'ENERO': 1,
        'FEBRERO': 2,
        'MARZO': 3,
        'ABRIL': 4,
        'MAYO': 5,
        'JUNIO': 6,
        'JULIO': 7,
        'AGOSTO': 8,
        'SEPTIEMBRE': 9,
        'OCTUBRE': 10,
        'NOVIEMBRE': 11,
        'DICIEMBRE': 12
    }
    re_pattern = r'.*CARTERA\s(?P<MONTH>\w+)\s(?P<YEAR>\d{4}).csv'

    try:
        dates_series = (
            pd.Series(cartera_files)
            .str.extract(re_pattern)
            .apply(lambda x: f"{x['YEAR']}-{month_digit_dict[x['MONTH']]}", axis=1)
        )
    except Exception as exc:
        dates_df = (
            pd.Series(cartera_files)
            .str.extract(re_pattern)
        )
        if (dates_df.isna().any(axis=1).any()):
            raise ValueError(f'Files not matching pattern: {re_pattern}')

        raise exc

    cierre = (
        pd.to_datetime(dates_series, format='%Y-%m')
        + pd.tseries.offsets.MonthEnd(1)
    )

    return cierre


def get_valid_relations_ids(cartera_df, colocacion_df, contacto_df, negocio_df):
    colocacion_obligacion_ids = (colocacion_df
                                 ['OBLIGACION']
                                 .dropna()
                                 .drop_duplicates()
                                 )
    cliente_obligacion_df = (cartera_df
                             [['CLIENTE', 'OBLIGACION']]
                             .dropna()
                             .drop_duplicates()
                             .query('OBLIGACION.isin(@colocacion_obligacion_ids)')
                             )

    cliente_ids = (cliente_obligacion_df
                   ['CLIENTE']
                   .drop_duplicates()
                   .reset_index(drop=True)
                   )
    index_clientes_in_contacto_n_negocio = (
        cliente_ids.isin(contacto_df['CLIENTE'])
        & cliente_ids.isin(negocio_df['CLIENTE'])
    )
    valid_cliente_ids = cliente_ids[index_clientes_in_contacto_n_negocio]

    cliente_obligacion_df = (cliente_obligacion_df
                             .query('CLIENTE.isin(@valid_cliente_ids)'))
    valid_obligacion_ids = cliente_obligacion_df['OBLIGACION']

    return (valid_cliente_ids, valid_obligacion_ids)


def read_csv(file, nrows=None, include=[], low_memory=True, raw=True):
    df = pd.read_csv(file, sep=';',
                     encoding="ISO-8859-1", nrows=nrows,
                     low_memory=low_memory
                     )

    if raw:
        if (len(include) > 0):
            df = df[include]

        return df

    df.columns = normalize_columns_name(df.columns)
    if (len(include) > 0):
        df = df[include]

    return df


def read_cartera(
    dir_path,
    raw=False,
    relations_filter=None,
    clean_all=False,
    clean_ids=False,
    include=[],

):
    """
    read_cartera(dir_path)
    read_cartera(dir_path, raw=True)
    read_cartera(dir_path, relations_filter=)
    read_cartera(dir_path, clean_all=True)
    read_cartera(dir_path, clean_ids=True)
    read_cartera(dir_path, relations_filter=, clean_all=True)
    """

    # multiple files dataset
    files = glob.glob(f'{dir_path}/*CARTERA*.csv')

    if raw:
        dfs = [read_csv(f, include=include, raw=raw) for f in files]
        df = pd.concat(dfs).reset_index(drop=True)

        return df.reset_index(drop=True)

    dates_cierre = extract_cartera_date_cierre(files)
    dfs = []
    for (file, date_cierre) in zip(files, dates_cierre):
        df = read_csv(file, include=include, raw=raw)
        df['FECHA_CIERRE'] = date_cierre
        dfs.append(df)

    df = pd.concat(dfs).reset_index(drop=True)

    if clean_ids or clean_all:
        # OBLIGACION
        ind = df['OBLIGACION'].isna()
        df = df[~ind]
        cleaning.cast_float_to_int_in_place(df, columns=['OBLIGACION'])

        counts_obligacion_per_cierre = df.groupby(by=['FECHA_CIERRE', 'OBLIGACION']).size()
        one_obligacion_per_cierre = (counts_obligacion_per_cierre == 1).all()
        assert one_obligacion_per_cierre, "There are multiple OBLIGACION per FECHA_CIERRE"

        # Dropping inconsistent records
        ind_porcentaje_pago_na = df['PORCENTAJE_PAGO'].isna()
        df = (
            df[~ind_porcentaje_pago_na]
            .query('~((CLIENTE == "FA8913") & (OBLIGACION == 178000341))')    
        )

        # CLIENTE
        ind = df['CLIENTE'].str.match('#N/D').fillna(False)
        df.loc[ind, 'CLIENTE'] = np.nan

        cliente_obligacion_df = df[['CLIENTE', 'OBLIGACION']].drop_duplicates()

        obligacion_size_ss = (
            cliente_obligacion_df
            .dropna()
            .groupby('OBLIGACION')
            .size()
        )
        one_cliente_per_obligacion = (obligacion_size_ss == 1).all()
        assert one_cliente_per_obligacion, "There are multiple CLIENT for single OBLIGACION"

        obligacion_size_ss = (
            cliente_obligacion_df
            .groupby('OBLIGACION')
            .size()
        )
        assert obligacion_size_ss.max() == 2, "There are more than two CLIENT per OBLIGACION"
        obligacion_ids = obligacion_size_ss[obligacion_size_ss == 2].index
        cliente_obligacion_ss = (
            cliente_obligacion_df
            .set_index('OBLIGACION')
            ['CLIENTE']
            .loc[obligacion_ids]
        )
        ind = cliente_obligacion_ss.isna()
        defs_ss = cliente_obligacion_ss[~ind]

        ind_na = df['CLIENTE'].isna()
        ind_in_definition = df['OBLIGACION'].isin(defs_ss.index)
        ind = ind_na & ind_in_definition
        df.loc[ind, 'CLIENTE'] = defs_ss.loc[df.loc[ind, 'OBLIGACION']].values
        df = df.dropna(subset='CLIENTE')

    if bool(relations_filter):
        df = relations_filter.filter_dataframe('cartera', df)

    if clean_all == False:
        return df

    df = (
        df
        .drop(columns=project_columns.CARTERA_DISCARDED_COLUMNS)
        .drop(columns=project_columns.CARTERA_USELESS_COLUMNS)
        .assign(
            MONTO=(df['MONTO']
                   .str.strip()
                   .str.replace(',', '')
                   .astype('int64')),
            SALDO=(df['SALDO']
                   .str.replace(',', '')
                   .astype('int64')),
        )
    )

    ind_numeric = df['FECHA_ULT_PAGO'].str.match(r'^\d+$').fillna(False)
    df.loc[ind_numeric, 'FECHA_ULT_PAGO'] = np.nan
    cleaning.cast_dates_in_place(df, exclude=['FECHA_CIERRE'])

    cleaning.cast_float_to_int_in_place(
        df, columns=['CUOTAS_PACTADAS', 'CUOTAS_PENDIENTES'])

    cleaning.cast_float_to_int_in_place(df, columns=['DIAS_VENCIDO'])

    replace_dict = {
        'FIRABITOBA': 'FIRAVITOBA',
        'NUCHIA': 'NUNCHIA',
        'Default': np.nan,
    }
    df['MUNICIPIO_CLIENTE'] = (
        df['MUNICIPIO_CLIENTE']
        .replace(replace_dict)
        .astype('category')
    )
    df = df.merge(location.coords_df, how='left', on='MUNICIPIO_CLIENTE')

    df['PERIODICIDAD_PAGO'] = df['PERIODICIDAD_PAGO'].astype('category')

    df['PORCENTAJE_PAGO'] = df['PORCENTAJE_PAGO'].str.strip()
    ind = df['PORCENTAJE_PAGO'].str.match('^\.\d{1,2}$').fillna(False)
    df.loc[ind, 'PORCENTAJE_PAGO'] = (
        df.loc[ind, 'PORCENTAJE_PAGO']
        .str.replace(r'^.', '', regex=True)
        .astype(int)
    )
    df['PORCENTAJE_PAGO'] = (
        df['PORCENTAJE_PAGO']
        .replace('######', 100)
        .astype(float)
    )

    df['SUCURSAL_COD'] = (
        df['SUCURSAL_COD']
        .replace('#N/D', np.nan)
    )
    ind_str = df['SUCURSAL_COD'].apply(lambda x: isinstance(x, str))
    all_str_numeric = (
        df
        .loc[ind_str, 'SUCURSAL_COD']
        .str.match(r'\d+')
        .all()
    )
    assert all_str_numeric, "There are non-numeric SUCURSAL_COD"
    df.loc[ind_str, 'SUCURSAL_COD'] = (
        df.loc[ind_str, 'SUCURSAL_COD']
        .astype(int)
    )
    df['SUCURSAL_COD'] = df['SUCURSAL_COD'].astype('category')

    ind = df['FECHA_CIERRE'] == "2019-12-31"
    df.loc[ind, ['TASA_ANUAL', 'TASA_PERIODICA']] /= 100

    df['TIPO_CREDITO'] = df['TIPO_CREDITO'].replace('SIN PERFIL', 'SIN_PERFIL')

    return df.sort_values(by=['FECHA_CIERRE', 'OBLIGACION'])


def read_castigada_xlsx(dir_path, raw=False, clean=True):
    # single file dataset
    file = glob.glob(f'{dir_path}/*CASTIGADA*.xlsx')[0]
    df = pd.read_excel(file, skiprows=6, usecols='A:O')

    if raw:
        return df

    df.columns = normalize_columns_name(df.columns)

    if clean == False:
        return df

    ind_na = df['OBLIGACION'].isna()
    df = df[~ind_na]
    cleaning.cast_float_to_int_in_place(df, columns=['OBLIGACION'])

    df['FECHA_CASTIGO'] = pd.to_datetime(
        df['FECHA_CASTIGO'], format='%d/%m/%Y')

    return df


def read_colocacion_csv(
    dir_path,
    raw=False
):
    # single file dataset
    file = glob.glob(f'{dir_path}/*COLOCACION*.csv')[0]

    df = read_csv(file, raw=raw, low_memory=False)

    return df


def read_colocacion_xlsx(
    dir_path,
    raw=False,
    relations_filter=None,
    clean=False,
):
    # single file dataset
    file = glob.glob(f'{dir_path}/*COLOCACION*.xlsx')[0]
    df = pd.read_excel(file, parse_dates=False)

    if raw:
        return df

    df.columns = normalize_columns_name(df.columns)

    # shift row 879
    df.iloc[879, 23] = \
        df.iloc[879, 23] + df.iloc[879, 24]
    df.iloc[879, 24:] = df.iloc[879, 24:].shift(-1)
    df = df.iloc[:, :-1]

    if bool(relations_filter):
        df = relations_filter.filter_dataframe('colocacion', df)

    if clean == False:
        return df

    df = (
        df
        .drop(columns=project_columns.COLOCACION_DISCARDED_COLUMNS)
        .drop(columns=project_columns.COLOCACION_LOCATION_COLUMNS)
    )

    CALIFICATIONS = set(['A', 'B', 'C', 'D', 'E'])

    def format_codeudor_no_cal(x):
        return f'COUDEUDOR_{len(x)}'

    def format_codeudor_cal(x):
        valid_cals = CALIFICATIONS.intersection(x)
        if len(valid_cals) == 0:
            return format_codeudor_no_cal(x)

        return f'CODEUDOR_{min(CALIFICATIONS.intersection(x))}'

    i_cosign_cal = df['CODEUDOR'].str.contains('CALIFICACION')
    i_no_cosign = df['CODEUDOR'].str.match('SIN CODEUDORES')
    i_cosign_no_cal = ~i_no_cosign & ~i_cosign_cal

    df.loc[i_no_cosign, 'CODEUDOR'] = 'SIN_CODEUDOR'
    df.loc[i_cosign_no_cal, 'CODEUDOR'] = (
        df
        .loc[i_cosign_no_cal, 'CODEUDOR']
        .str.findall('\d+')
        .apply(format_codeudor_no_cal)
    )
    df.loc[i_cosign_cal, 'CODEUDOR'] = (
        df
        .loc[i_cosign_cal, 'CODEUDOR']
        .str.findall(r'(?:CALIFICACION:\s)(?P<calificacion>\w)')
        .apply(format_codeudor_cal)
    )

    df['EDAD'] = df['EDAD'].astype(int)
    df['FECHA_NACIMIENTO'] = pd.to_datetime(df['FECHA_NACIMIENTO'])

    DATE_COLS = df.columns[df.columns.str.match('^FECHA_')]
    exclude = df[DATE_COLS].select_dtypes('datetime64').columns
    cleaning.cast_dates_in_place(df, exclude=exclude)

    df['TIPO_VIVIENDA'] = cleaning.clean_tipo_vivienda(df['TIPO_VIVIENDA'])

    return df


def read_contacto(dir_path, raw=False, relations_filter=None, clean=False):
    """
    read_contacto(dir_path)
    read_contacto(dir_path, raw=True)
    read_contacto(dir_path, relations_filter=)
    read_contacto(dir_path, clean=True)
    read_contacto(dir_path, relations_filter=, clean=True)
    """

    # single file dataset
    file = glob.glob(f'{dir_path}/*CONTACTO*.csv')[0]
    df = read_csv(file, raw=raw, low_memory=False)

    if raw:
        return df

    if bool(relations_filter):
        df = relations_filter.filter_dataframe('contacto', df)

    if clean == False:
        return df

    fix_typos_dict = {
        '25/08/0977': '25/08/1977',
        '08/09/1798': '08/09/1978',
        '20/05/1071': '20/05/1971',
        '23/10/1057': '23/10/1957',
        '21/06/1772': '21/06/1972',
        '28/06/1885': '28/06/1985',
        '19/01/1074': '19/01/1974',
        '06/09/0965': '06/09/1965',
        '27/10/1058': '27/10/1958',
        '01/03/1194': '01/03/1994',
    }

    RE_NOMEN_PATT = r'\s\|.*$'
    RE_CODE_PATT = r'^.*\s\|'

    df = (
        df
        .drop(columns=project_columns.CONTACTO_DISCARDED_COLUMNS)
        .assign(
            ESTADO_CIVIL=(
                df['ESTADO_CIVIL']
                .str.replace(RE_NOMEN_PATT, '', regex=True)
                .astype('category')
            ),
            ESTADO_CIVIL_COD=(
                df['ESTADO_CIVIL']
                .str.replace(RE_CODE_PATT, '', regex=True)
                .astype('category')
            ),
            FECHA_NACIMIENTO=pd.to_datetime(
                df['FECHA_NACIMIENTO'].replace(fix_typos_dict),
                format='%d/%m/%Y'
            ),
            GENERO=(
                df['GENERO']
                .str.replace(RE_NOMEN_PATT, '', regex=True)
                .astype('category')
            ),
            GENERO_COD=(
                df['GENERO']
                .str.replace(RE_CODE_PATT, '', regex=True)
                .astype('category')
            ),
            MUJER_CABEZA=(
                df['MUJER_CABEZA']
                .astype('category')
            ),
            NIVEL_ESTUDIOS=(
                df['NIVEL_ESTUDIOS']
                .str.replace(RE_NOMEN_PATT, '', regex=True)
                .astype('category')
            ),
            NIVEL_ESTUDIOS_COD=(
                df['NIVEL_ESTUDIOS']
                .str.replace(RE_CODE_PATT, '', regex=True)
                .astype('category')
            ),
            PROFESION=(
                df['PROFESION']
                .str.replace(RE_NOMEN_PATT, '', regex=True)
                .astype('category')
            ),
            PROFESION_COD=(
                df['PROFESION']
                .str.replace(RE_CODE_PATT, '', regex=True)
                .astype('category')
            ),
            RESPONSABLE_DE_HOGAR=(
                df['RESPONSABLE_DE_HOGAR']
                .astype('category')
            ),
            TIPO_DE_CLIENTE=(
                df['TIPO_DE_CLIENTE']
                .str.replace(r'\s\|.*', '', regex=True)
                .astype('category')
            ),
            TIPO_UBICACION=(
                df['TIPO_UBICACION']
                .str.replace(RE_NOMEN_PATT, '', regex=True)
                .astype('category')
            ),
            TIPO_UBICACION_COD=(
                df['TIPO_UBICACION']
                .str.replace(RE_CODE_PATT, '', regex=True)
                .astype('category')
            ),
            TIPO_VIVIENDA=cleaning.clean_tipo_vivienda(
                df['TIPO_VIVIENDA']
                .str.replace(RE_NOMEN_PATT, '', regex=True)
            ),
            TIPO_VIVIENDA_COD=(
                df['TIPO_VIVIENDA']
                .str.replace(RE_CODE_PATT, '', regex=True)
                .astype('category')
            ),
        )
    )

    return df


def read_negocio(dir_path, raw=False, relations_filter=None, clean=False):
    """
    read_negocio(dir_path)
    read_negocio(dir_path, raw=True)
    read_negocio(dir_path, relations_filter=)
    read_negocio(dir_path, clean=True)
    read_negocio(dir_path, relations_filter=, clean=True)
    """

    # single file dataset
    file = glob.glob(f'{dir_path}/*NEGOCIO*.csv')[0]
    df = read_csv(file, raw=raw, low_memory=False)

    if raw:
        return df

    if bool(relations_filter):
        df = relations_filter.filter_dataframe('negocio', df)

    if clean == False:
        return df

    ind = df['CLIENTE'].duplicated(keep=False)
    df = df[~ind]

    df = (
        df

        # Remove all " | CODE"
        .assign(TIPO=df['TIPO'].str.replace(r'\s\|.*$', '', regex=True))
    )

    return df


def read_joining_datasets(dir_path):
    """Detailed explanation in cleaning/joining_datasets.ipynb"""

    cartera_df = read_cartera(dir_path, clean_all=True)
    castigo_df = read_castigada_xlsx(dir_path, clean=True)
    colocacion_df = read_colocacion_xlsx(dir_path, clean=True)
    contacto_df = read_contacto(dir_path, clean=True)
    negocio_df = read_negocio(dir_path, clean=True)

    (cids, oids) = get_valid_relations_ids(
        cartera_df, colocacion_df, contacto_df, negocio_df)

    rel_filt = RelationsFilter(cids, oids)
    cartera_df = rel_filt.filter_dataframe('cartera', cartera_df)
    castigo_df = rel_filt.filter_dataframe('castigo', castigo_df)
    colocacion_df = rel_filt.filter_dataframe('colocacion', colocacion_df)
    contacto_df = rel_filt.filter_dataframe('contacto', contacto_df)
    negocio_df = rel_filt.filter_dataframe('negocio', negocio_df)

    cliente_obligacion_df = (
        cartera_df
        [['CLIENTE', 'OBLIGACION']]
        .drop_duplicates()
    )

    cols = project_columns.COLOCACION_CLIENT_COLUMNS
    clientes_df = (
        cliente_obligacion_df
        .merge(
            colocacion_df[['OBLIGACION', *cols]],
            on='OBLIGACION'
        )
        .drop(columns='OBLIGACION')
        .drop_duplicates()
    )

    any_duplicate = clientes_df['CLIENTE'].duplicated().any()
    assert any_duplicate == False, 'There are multiple values for CLIENTE column'

    # Merging CONTACTO
    clientes_df = (
        clientes_df
        .merge(contacto_df, how='left', on='CLIENTE', suffixes=('_COLOCACION', '_CONTACTO'))
    )

    profesion_df = clientes_df[['PROFESION_COLOCACION', 'PROFESION_CONTACTO']]
    index_na = profesion_df.isna()
    index_desconocida = profesion_df[[
        'PROFESION_COLOCACION', 'PROFESION_CONTACTO']] == 'DESCONOCIDA'
    index_2 = (
        index_desconocida['PROFESION_COLOCACION']
        & ~index_desconocida['PROFESION_CONTACTO']
        & ~(index_na['PROFESION_CONTACTO'])
    )
    profesion_series = profesion_df['PROFESION_COLOCACION'].copy()
    profesion_series[index_2] = profesion_df.loc[index_2, 'PROFESION_CONTACTO']
    profesion_series = profesion_series.replace({
        'DESCONOCIDA': np.nan,
        'SIN PROFESION': np.nan
    })
    clientes_df['PROFESION'] = profesion_series

    index_cols = colocacion_df.columns.isin(contacto_df.columns)
    common_cols = colocacion_df.columns[index_cols]
    for col in common_cols[common_cols != 'PROFESION']:
        clientes_df[col] = clientes_df[f'{col}_COLOCACION']

        indices = cleaning.compare_series(
            clientes_df, f'{col}_COLOCACION',  f'{col}_CONTACTO')
        ind_eq = indices['eq']
        clientes_df.loc[~ind_eq, col] = np.nan

    re_columns_pattern = fr"({'|'.join(common_cols)})_(COLOCACION|CONTACTO)"
    index_cols = clientes_df.columns.str.match(re_columns_pattern)
    dropping_cols = clientes_df.columns[index_cols]
    clientes_df = clientes_df.drop(columns=dropping_cols)

    # Merging NEGOCIO
    cols = project_columns.NEGOCIO_CLIENT_COLUMNS
    any_common_col = clientes_df.columns.isin(cols).any()
    assert any_common_col == False, "There are duplicated columns"

    clientes_df = (
        clientes_df
        .merge(negocio_df[['CLIENTE', *cols]], how='left', on='CLIENTE')
    )

    # Updating CARTERA
    index_cols = cartera_df.columns.isin(clientes_df.columns)
    dropping_cols = pd.Series([
        *cartera_df.columns[index_cols],
        *project_columns.CARTERA_COLOCACION_COLUMNS,
    ]).drop_duplicates()
    dropping_cols = dropping_cols[dropping_cols != 'CLIENTE']
    cartera_df = cartera_df.drop(columns=dropping_cols)

    # Updating COLOCACION
    index_cols = colocacion_df.columns.isin(clientes_df.columns)
    dropping_cols = colocacion_df.columns[index_cols]
    castigo_df = (
        castigo_df[['OBLIGACION']]
        .assign(DEFAULT=True)
    )
    colocacion_df = (
        colocacion_df
        .drop(columns=dropping_cols)
        .merge(cliente_obligacion_df, on='OBLIGACION')
        .merge(castigo_df, on='OBLIGACION', how='left')
    )

    return (cartera_df, clientes_df, colocacion_df)
