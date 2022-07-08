import json
import os

import joblib
import pandas as pd


MONTO_COLUMNS = [
    'CREDITOS_VIGENTES',
    'EDAD',
    'ESPONSABLE_DE_HOGAR',
    'ESTADO_CIVIL',
    'ESTRATO',
    'MUNICIPIO_CLIENTE',
    'NIVEL_ESTUDIOS',
    'NRO_CUOTAS',
    'OCUPACION',
    'OFICIO',
    'SUELDO_BASICO',
    'TASA_ANUAL',
    'TIPO_UBICACION',
    'TIPO_VIVIENDA'
]


def compose_results_df(df, results_key, results_values):
    if 'ID' in df.columns:
        id_values = df['ID'].values
    else:
        id_values = list(range(df.shape[0]))
        
    results_df = pd.DataFrame({
        'ID': id_values,
        results_key: results_values,
    })

    return results_df


def format_unknowns_error(variable, unknowns):
    unique_unknowns = (
        unknowns
        .drop_duplicates()
        .sort_values()
    )
    cats = ', '.join([f'"{u}"' for u in unique_unknowns])
    return f'Unknown categories: variable "{variable}": categories: {cats}'


def validate_dataframe_cols(model_cols, data_cols):
    model_cols = pd.Series(model_cols)
    ind = model_cols.isin(data_cols)
    if (ind.all()):
        return None

    ind_missing = ~ind
    missings = ', '.join([f'"{col}"' for col in model_cols[ind_missing]])
    return f'Following columns are missing in data: {missings}'


class Models(object):
    def get_defaulting_cols(self):
        return self.model_defaulting.feature_names_in_

    def load_models(self, dir_path):
        self.model_defaulting = joblib.load(
            os.path.join(dir_path, 'model_defaulting'))
        self.model_monto = joblib.load(os.path.join(dir_path, 'model_monto'))

        file = os.path.join(
            dir_path, 'dict-defaulting-variable-category-code.json')
        with open(file, 'r') as f:
            self.catmap_defaulting = json.load(f)

    def predict(self, df):
        dcols = self.get_defaulting_cols()
        # mcols = self.model_monto.params.index

        cols = [*dcols]
        # cols = [*dcols, *mcols]
        error_message = validate_dataframe_cols(cols, df.columns)
        if (error_message):
            return (error_message, None)

        (error_message, defaulting_df) = self.predict_defaulting(df)
        if (error_message):
            return (error_message, None)

        return (None, defaulting_df)

    def predict_defaulting(self, df):
        df = df.copy()

        cmap = self.catmap_defaulting
        dcols = self.get_defaulting_cols()

        df = df.astype({'TIPO_UBICACION_COD': str})

        for c in dcols:
            if (df[c].isna().any()):
                df[c] = df[c].astype(str).replace('nan', 'NaN')

            ind_valid = df[c].isin(cmap[c].keys())
            if (ind_valid.all() == False):
                unknowns = df.loc[~ind_valid, c]
                error_message = format_unknowns_error(c, unknowns)
                return (error_message, None)

            df[c] = df[c].replace(cmap[c])

        try:
            error_message = None
            defaulting_values = self.model_defaulting.predict(df[dcols])
            defaulting_df = compose_results_df(df, 'DEFAULTING', defaulting_values)
        except Exception as e:
            error_message = f'Unexpected error predicting defaulting: "{e}"'
            defaulting_df = None

        return (error_message, defaulting_df)
