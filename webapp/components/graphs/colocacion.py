import plotly.express as px

from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output, State

from external import datasets as data


class ColocacionCrecimiento(object):
    def __init__(self, colocacion_signal, time_offset):
        self.colocacion_signal = colocacion_signal
        self.time_offset = time_offset

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.colocacion_signal, 'data'),
            Input(self.time_offset, 'data'),
            prevent_initial_call=False,
        )
        def update_colocacion_crecimiento(_, offset_data):
            df = data.stats_crecimiento_colocaciones()
            df = data.filter_dataframe(
                df, 'FECHA_CIERRE', offset_data)

            # casted for compatibility with plotly
            df['FECHA_CIERRE'] = (
                df['FECHA_CIERRE']
                .dt.date
                .astype(str)
            )

            kwargs = {
                'data_frame': df,
                'x': "NUM_OBLIGACIONES",
                'y': "NUM_CLIENTES",
                'animation_frame': "FECHA_CIERRE",
                'animation_group': "MUNICIPIO_CLIENTE",
                'size': "VALOR_DESEMBOLSADO",
                'color': "REGION",
                'hover_name': "MUNICIPIO_CLIENTE",
                'facet_col': "REGION",
                'log_x': True,
                'size_max': 60,
                'range_x': [1, 5000],
                'range_y': [-500, 6000],
                'title': 'Animación de crecimiento de colocaciones',
            }

            try:
                fig = px.scatter(**kwargs)
            except ValueError:
                fig = px.scatter(**kwargs)

            return fig


class ColocacionHistorico(object):
    def __init__(self, colocacion_signal, time_offset):
        self.colocacion_signal = colocacion_signal
        self.time_offset = time_offset

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.colocacion_signal, 'data'),
            Input(self.time_offset, 'data'),
            prevent_initial_call=False,
        )
        def update_colocaciones(_, offset_data):
            df = data.stats_colocacion_counts()
            df = data.filter_dataframe(
                df, 'FECHA_CIERRE', offset_data)

            kwargs = {
                'data_frame': df,
                'x': 'FECHA_CIERRE',
                'y': 'NUM_CREDITOS',
                'markers': True,
                'title': 'Colocaciones mensuales (día 1 refiere el mismo mes)',
            }
            try:
                fig = px.line(**kwargs)
            except ValueError:
                fig = px.line(**kwargs)

            return fig


class ColocacionLocalizacion(object):
    def __init__(self, colocacion_signal, cierre_id):
        self.colocacion_signal = colocacion_signal
        self.cierre_id = cierre_id

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.colocacion_signal, 'data'),
            Input(self.cierre_id, 'value'),
            prevent_initial_call=False,
        )
        def update_colocacion_localizacion(_, cierre_date):
            if (cierre_date is None):
                return no_update

            df = data.stats_localizacion_colocaciones()
            df = df.query('FECHA_CIERRE == @cierre_date')

            kwargs = {
                'data_frame': df,
                'lat': "MUNICIPIO_LAT",
                'lon': "MUNICIPIO_LON",
                'color': "MUNICIPIO_CLIENTE",
                'size': "VALOR_DESEMBOLSADO",
                'title': f'Colocaciones por MUNICIPIO_CLIENTE (FECHA_CIERRE={cierre_date})',
                'color_continuous_scale': px.colors.cyclical.IceFire,
                'mapbox_style': "carto-positron",
                'size_max': 15,
                'zoom': 6,

            }

            try:
                fig = px.scatter_mapbox(**kwargs)
            except ValueError:
                fig = px.scatter_mapbox(**kwargs)

            return fig
