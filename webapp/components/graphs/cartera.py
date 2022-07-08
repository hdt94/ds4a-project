import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import html, dcc, callback
from dash.dependencies import Input, Output, State

from external import datasets


class Calificaciones(object):
    def __init__(self, signal_update, time_offset):
        self.signal_update = signal_update
        self.time_offset = time_offset

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.signal_update, "data"),
            Input(self.time_offset, "data"),
            prevent_initial_call=False,
        )
        def update_calificaciones(_, offset_data):
            df = datasets.stats_cartera_porcentaje_calificacion_by_cierre()
            df = datasets.filter_dataframe(
                df, 'FECHA_CIERRE', offset_data)

            kwargs = {
                'data_frame': df,
                'x': 'FECHA_CIERRE',
                'y': 'PORCENTAJE_CREDITOS',
                'color': 'CALIFICACION_CIERRE',
                'title': 'Porcentaje de créditos mensuales por calificación',
            }

            try:
                fig = px.bar(**kwargs)
            except ValueError:
                fig = px.bar(**kwargs)

            fig.update_layout(hovermode="x")
            return fig


class Fugas(object):
    def __init__(self, signal_update, time_offset):
        self.signal_update = signal_update
        self.time_offset = time_offset

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.signal_update, "data"),
            Input(self.time_offset, "data"),
            prevent_initial_call=False,
        )
        def update_fugas(_, offset_data):
            x = 'FECHA_CIERRE'
            y = 'NUM_FUGAS'

            df = datasets.stats_cartera_leaking()
            df = datasets.filter_dataframe(df, x, offset_data)

            max_date = df.iloc[-1][x]
            prev_value = df.iloc[-2][y]
            df = df.iloc[:-1]

            kwargs = {
                'data_frame': df,
                'x': x,
                'y': y,
                'markers': True,
                'title': 'Estimación de número mensual de fugas',
            }

            try:
                fig = px.line(**kwargs)
            except ValueError:
                fig = px.line(**kwargs)

            fig.add_trace(
                go.Scatter(
                    x=[max_date],
                    y=[prev_value],
                    showlegend=False,
                    name='',
                    text='ÚLTIMO MES NO ES POSIBLE ESTIMAR FUGAS',
                )
            )

            return fig


class Saldo(object):
    def __init__(self, signal_update, time_offset):
        self.signal_update = signal_update
        self.time_offset = time_offset

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.signal_update, "data"),
            Input(self.time_offset, "data"),
            prevent_initial_call=False,
        )
        def update_saldo(_, offset_data):
            df = datasets.stats_cartera_saldo()
            df = datasets.filter_dataframe(
                df, 'FECHA_CIERRE', offset_data)

            kwargs = {
                'data_frame': df,
                'x': 'FECHA_CIERRE',
                'y': 'SALDO (MILES DE MILLONES)',
                'markers': True,
                'title': 'Saldo mensual de cartera',
            }

            try:
                fig = px.line(**kwargs)
            except ValueError:
                fig = px.line(**kwargs)

            return fig


class SaldoCalificacion(object):
    def __init__(self, signal_update, time_offset):
        self.signal_update = signal_update
        self.time_offset = time_offset

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.signal_update, "data"),
            Input(self.time_offset, "data"),
            prevent_initial_call=False,
        )
        def update_saldo(_, offset_data):
            df = datasets.stats_cartera_saldo_by_calificacion()
            df = datasets.filter_dataframe(
                df, 'FECHA_CIERRE', offset_data)

            kwargs = {
                'data_frame': df,
                'x': 'FECHA_CIERRE',
                'y': 'SALDO (MILES DE MILLONES)',
                'color': 'CALIFICACION_CIERRE',
                'title': 'Saldo mensual de cartera por calificación',
            }

            try:
                fig = px.bar(**kwargs)
            except ValueError:
                fig = px.bar(**kwargs)

            fig.update_layout(hovermode="x")

            return fig


class SaldoLocacion(object):
    def __init__(self, signal_update, time_offset):
        self.signal_update = signal_update
        self.time_offset = time_offset

    def display(self):
        self.layout = dcc.Graph()
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.layout, 'figure'),
            Input(self.signal_update, "data"),
            Input(self.time_offset, "data"),
            prevent_initial_call=False,
        )
        def update_saldo_localizacion(_, offset_data):
            df = datasets.stats_cartera_saldo_by_sucursal()
            df = datasets.filter_dataframe(
                df, 'FECHA_CIERRE', offset_data)
            
            kwargs = {
                'data_frame': df,
                'x': 'FECHA_CIERRE',
                'y': 'SALDO (MILES DE MILLONES)',
                'color': 'SUCURSAL',
                'markers': True,
                'title': 'Saldo mensual de cartera por sucursal',
            }
            
            try:
                fig = px.line(**kwargs)
            except ValueError:
                fig = px.line(**kwargs)

            fig.update_layout(hovermode="x")

            return fig
