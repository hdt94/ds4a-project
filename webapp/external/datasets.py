import datetime
import glob
import os

import numpy as np
import pandas as pd

from core_ds4a_project import location
from core_ds4a_project.exploring import filter_cartera_last, filter_cartera_leaked

from external.cache import cache


DATASETS_DIR = os.environ.get("DATASETS_DIR", None)
if DATASETS_DIR is None:
    raise ValueError('Undefined DATASETS_DIR')

# initial files
files = {
    "cartera": glob.glob(os.path.join(DATASETS_DIR, '*CARTERA*'))[0],
    "clientes": glob.glob(os.path.join(DATASETS_DIR, '*CLIENTES*'))[0],
    "colocacion": glob.glob(os.path.join(DATASETS_DIR, '*COLOCACION*'))[0],
}


def filter_dataframe(df, col, offset_data):
    """filter dataframe based of offset dictionary compliant with pd.offsets.DateOffset()

        Example:

        filter_dataframe(df, col='FECHA_CIERRE', offset_data={years=2})
    """

    if (offset_data):
        max_date = df[col].max()
        offset = pd.offsets.DateOffset(**offset_data)
        cutoff = max_date - offset

        if (
            not isinstance(max_date, pd.Timestamp)
            and isinstance(max_date, datetime.date)
        ):
            cutoff = cutoff.date()

        df = df[df[col] > cutoff]

    return df


class Datasets(object):
    cartera = None
    clientes = None
    colocacion = None

    def concat_dataset(self, dataset, df):
        setattr(self, dataset, pd.concat([getattr(self, dataset), df]))

    def get_dataset(self, dataset, usecols=None):
        if getattr(self, dataset) is None:
            self.read_dataset(dataset)

        if usecols is None:
            return getattr(self, dataset)
        else:
            return getattr(self, dataset)[usecols]

    def get_max_datetime(self, dataset):
        if (dataset == 'cartera'):
            date_col = 'FECHA_CIERRE'
        elif (dataset == 'colocacion'):
            date_col = 'FECHA_DESEMBOLSO'
        else:
            raise ValueError('')

        df = self.get_dataset(dataset, usecols=[date_col])

        return df[date_col].max()

    def read_dataset(self, dataset, usecols=None):
        if (dataset == 'cartera'):
            usecols = list(set([
                'CLIENTE',
                'FECHA_CIERRE', 'CALIFICACION_CIERRE', 'SALDO', 'CALIFICACION_CIERRE', 'SUCURSAL_COD',
                'OBLIGACION', 'CUOTAS_PACTADAS', 'CUOTAS_PENDIENTES',
                'MUNICIPIO_LAT',
                'MUNICIPIO_LON',
                'MUNICIPIO_CLIENTE',
                'REGION',
            ]))
        df = pd.read_csv(files[dataset], usecols=usecols)

        if ('FECHA_CIERRE' in df.columns):
            df['FECHA_CIERRE'] = pd.to_datetime(
                df['FECHA_CIERRE'], format='%Y-%m-%d')

        if ('FECHA_DESEMBOLSO' in df.columns):
            df['FECHA_DESEMBOLSO'] = pd.to_datetime(
                df['FECHA_DESEMBOLSO'], format='%Y-%m-%d')
        if ('FECHA_SOLICITUD' in df.columns):
            df['FECHA_SOLICITUD'] = pd.to_datetime(
                df['FECHA_SOLICITUD'], format='%Y-%m-%d')

        if ('SUCURSAL_COD' in df.columns):
            df['SUCURSAL'] = (
                df['SUCURSAL_COD']
                .replace(location.SUCURSAL_COD_DICT)
            )

        setattr(self, dataset, df)


data = Datasets()


def add_dataset(dataset, df):
    data.concat_dataset(dataset, df)


@cache.memoize()
def get_cartera_memo(datemax, usecols):
    cartera_df = data.get_dataset('cartera', usecols)

    return cartera_df


@cache.memoize()
def get_clientes_memo(datemax, usecols):
    clientes_df = data.get_dataset('clientes', usecols)

    return clientes_df


@cache.memoize()
def get_cartera_cierre_values():
    df = get_cartera(usecols=['FECHA_CIERRE'])
    values = (
        df['FECHA_CIERRE']
        .dt.date
        .drop_duplicates()
        .sort_values(ascending=False)
        .astype(str)
        .to_list()
    )

    return values


@cache.memoize()
def get_cartera_last_memo(datemax):
    cartera_df = data.get_dataset('cartera')
    cartera_df = filter_cartera_last(cartera_df, sorted=False)
    return cartera_df


@cache.memoize()
def get_cartera_leaked_memo(datemax, usecols=None):
    df = get_cartera_last_memo(datemax)
    df = filter_cartera_leaked(df)

    if usecols is None:
        return df
    else:
        return df[usecols]


@cache.memoize()
def get_colocacion_memo(datemax, usecols=None):
    colocacion_df = data.get_dataset('colocacion', usecols)
    return colocacion_df


def get_cartera(usecols=None):
    datemax = data.get_max_datetime('cartera')

    return get_cartera_memo(datemax, usecols)


def get_cartera_last():
    datemax = data.get_max_datetime('cartera')

    return get_cartera_last_memo(datemax)


def get_cartera_leaked(usecols=None):
    datemax = data.get_max_datetime('cartera')

    return get_cartera_leaked_memo(datemax, usecols)


def get_clientes(usecols=None):
    datemax = data.get_max_datetime('colocacion')

    return get_clientes_memo(datemax, usecols)


def get_colocacion(usecols=None):
    datemax = data.get_max_datetime('colocacion')

    return get_colocacion_memo(datemax, usecols)


@cache.memoize()
def stats_cartera_leaking():
    df = get_cartera_leaked(usecols=['FECHA_CIERRE'])
    df['FECHA_CIERRE'] = (
        df['FECHA_CIERRE']
        .dt.to_period(freq='M')
        .dt.end_time
        .dt.date
    )
    df = (
        df['FECHA_CIERRE']
        .value_counts()
        .rename('NUM_FUGAS')
        .reset_index()
        .rename(columns={'index': 'FECHA_CIERRE'})
        .sort_values('FECHA_CIERRE')
    )
    df.iloc[-1]['NUM_FUGAS'] = np.nan

    return df


@cache.memoize()
def stats_cartera_porcentaje_calificacion_by_cierre():
    df = get_cartera(usecols=['FECHA_CIERRE', 'CALIFICACION_CIERRE'])
    totals_per_month = (
        df
        .groupby('FECHA_CIERRE')
        .size()
    )
    df = (
        df
        .groupby(['FECHA_CIERRE', 'CALIFICACION_CIERRE'])
        .size()
        .rename('NUM_CREDITOS')
        .reset_index('CALIFICACION_CIERRE')
    )
    df['PORCENTAJE_CREDITOS'] = (
        (df['NUM_CREDITOS'] / totals_per_month) * 100).round(2)
    df = df.reset_index()

    return df


@cache.memoize()
def stats_cierre(dataviz=True):
    cartera_df = get_cartera(
        usecols=[
            'CALIFICACION_CIERRE',
            'FECHA_CIERRE',
            'OBLIGACION',
            'SALDO',
        ])
    colocacion_df = get_colocacion(
        usecols=['FECHA_DESEMBOLSO', 'VALOR_DESEMBOLSADO'])

    ind_a = cartera_df['CALIFICACION_CIERRE'] == 'A'
    saldos = (
        cartera_df
        [['FECHA_CIERRE', 'SALDO']]
        .assign(
            SALDO_AL_DIA=cartera_df['SALDO'].where(ind_a, 0),
            SALDO_VENCIDO=cartera_df['SALDO'].mask(ind_a, 0),
        )
        .groupby(['FECHA_CIERRE'])
        .sum()
    )
    saldos /= 1e9
    saldos['PORCENTAJE_AL_DIA'] = (
        saldos['SALDO_AL_DIA'] / saldos['SALDO']) * 100
    saldos['PORCENTAJE_VENCIDO'] = (
        saldos['SALDO_VENCIDO'] / saldos['SALDO']) * 100

    colocaciones = (
        colocacion_df
        .assign(
            FECHA_CIERRE=(
                colocacion_df['FECHA_DESEMBOLSO'] + pd.offsets.MonthEnd(0))
        )
        .groupby(['FECHA_CIERRE'])
        .agg({'FECHA_DESEMBOLSO': 'size', 'VALOR_DESEMBOLSADO': 'sum'})
        .rename(columns={'FECHA_DESEMBOLSO': 'NUM_COLOCACIONES'})
    )
    colocaciones['VALOR_DESEMBOLSADO'] /= 1e9

    df = (
        pd.concat([saldos, colocaciones], axis=1)
        .reset_index()
        .sort_values('FECHA_CIERRE', ascending=False)
    )

    if dataviz:
        df['FECHA_CIERRE'] = df['FECHA_CIERRE'].dt.date
        for col in ['PORCENTAJE_AL_DIA', 'PORCENTAJE_VENCIDO']:
            df[col] = df[col].round(2)
        for col in ['SALDO', 'SALDO_AL_DIA', 'SALDO_VENCIDO', 'VALOR_DESEMBOLSADO']:
            df[col] = df[col].round(3)

    return df


@cache.memoize()
def stats_cartera_saldo():
    df = stats_cierre()
    df = (
        df[['FECHA_CIERRE', 'SALDO']]
        .rename(columns={'SALDO': 'SALDO (MILES DE MILLONES)'})
        .sort_values('FECHA_CIERRE')
    )

    return df


@cache.memoize()
def stats_cartera_saldo_by_calificacion():
    df = get_cartera(
        usecols=['CALIFICACION_CIERRE', 'FECHA_CIERRE', 'SALDO'])
    df = (
        df
        .groupby(['FECHA_CIERRE', 'CALIFICACION_CIERRE'])
        .sum()
        .eval('SALDO = SALDO / 1e9')
        .rename(columns={'SALDO': 'SALDO (MILES DE MILLONES)'})
        .reset_index()
        .sort_values(['FECHA_CIERRE', 'CALIFICACION_CIERRE'])
    )

    return df


@cache.memoize()
def stats_cartera_saldo_by_sucursal():
    df = get_cartera(
        usecols=['FECHA_CIERRE', 'SALDO', 'SUCURSAL_COD', 'SUCURSAL'])
    y = 'SALDO (MILES DE MILLONES)'
    df = (
        df
        .drop(columns=['SUCURSAL_COD'])
        .groupby(['FECHA_CIERRE', 'SUCURSAL'])
        .sum()
        .eval('SALDO = SALDO / 1e9')
        .rename(columns={'SALDO': y})
        .reset_index()
        .sort_values('FECHA_CIERRE')
    )

    return df


@cache.memoize()
def stats_colocacion_counts():
    df = get_colocacion(usecols=['FECHA_DESEMBOLSO'])
    df['FECHA_CIERRE'] = df['FECHA_DESEMBOLSO'] + pd.offsets.MonthEnd(0)
    df = (
        df['FECHA_CIERRE']
        .value_counts()
        .rename('NUM_CREDITOS')
        .reset_index()
        .rename(columns={'index': 'FECHA_CIERRE'})
        .sort_values('FECHA_CIERRE')
    )

    return df


@cache.memoize()
def stats_localizacion_colocaciones():
    cartera_df = get_cartera(usecols=[
        'CLIENTE',
        'FECHA_CIERRE',
        'MUNICIPIO_CLIENTE',
        'MUNICIPIO_LAT',
        'MUNICIPIO_LON',
        'OBLIGACION',
    ])
    colocacion_df = get_colocacion(usecols=[
        'OBLIGACION',
        'VALOR_DESEMBOLSADO',
    ])
    df = (
        cartera_df
        .merge(colocacion_df, on='OBLIGACION')
        .groupby(['FECHA_CIERRE', 'MUNICIPIO_LAT', 'MUNICIPIO_LON', 'MUNICIPIO_CLIENTE'])
        .agg({'CLIENTE': 'size', 'VALOR_DESEMBOLSADO': 'sum'})
        .reset_index()
    )
    return df


@cache.memoize()
def stats_crecimiento_colocaciones():
    regiones = ["REGION NORTE", "REGION CENTRO",
                "REGION SUR", "REGION VILLAVICENCIO",
                ]
    cartera_df = (
        get_cartera(
            usecols=[
                'CLIENTE',
                'MUNICIPIO_CLIENTE',
                'OBLIGACION',
                'REGION',
            ])
        .query('REGION.isin(@regiones)')
    )
    colocacion_df = get_colocacion(usecols=[
        'FECHA_DESEMBOLSO',
        'OBLIGACION',
        'VALOR_DESEMBOLSADO',
    ])
    df = (
        colocacion_df
        .merge(cartera_df, on='OBLIGACION')
    )
    df = (
        df
        .assign(FECHA_CIERRE=df['FECHA_DESEMBOLSO'] + pd.offsets.MonthEnd(0))
        .drop(columns=['FECHA_DESEMBOLSO'])
        .groupby(['REGION', 'MUNICIPIO_CLIENTE', 'FECHA_CIERRE'])
        .agg({'OBLIGACION': 'size', 'CLIENTE': 'size', 'VALOR_DESEMBOLSADO': 'sum'})
        .rename(columns={
            'CLIENTE': 'NUM_CLIENTES',
            'OBLIGACION': 'NUM_OBLIGACIONES',
        })
        .reset_index()
        .sort_values('FECHA_CIERRE')
    )

    return df


def update_cache():
    #  = data.get_max_datetime('cartera')
    stats_localizacion_colocaciones()
    stats_crecimiento_colocaciones()
    stats_cierre()
    stats_cartera_leaking()
    stats_cartera_porcentaje_calificacion_by_cierre()
    stats_cartera_saldo()
    stats_cartera_saldo_by_calificacion()
    stats_cartera_saldo_by_sucursal()
    stats_colocacion_counts()

    get_cartera_cierre_values()
