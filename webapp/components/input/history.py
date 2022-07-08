import re

import pandas as pd

from dash import html, dcc, callback, no_update
from dash.dependencies import Input, Output


class TimeOffsetRadios():
    DEFAULT_DATA = {'years': 2}
    DEFAULT_VALUE = 'years=2'

    def __init__(self, store_id):
        self.store_id = store_id

    def display(self):
        offset_store = dcc.Store(
            id=self.store_id,
            data=self.DEFAULT_DATA
        )
        self.radios = dcc.RadioItems(
            inline=True,
            inputClassName='form-check-input',
            labelClassName='form-check-label',
            options=[
                {'label': 'Histórico', 'value': 'all'},
                {'label': 'Últimos dos años', 'value': 'years=2'},
                {'label': 'Últimos seis meses', 'value': 'months=6'},
            ],
            value=self.DEFAULT_VALUE,
            style={
                'display': 'flex',
                'gap': '1rem',
            }
        )
        self.register_callbacks()

        return html.Div([
            offset_store,
            self.radios,
        ])

    def register_callbacks(self):
        @callback(
            Output(self.store_id, 'data'),
            Input(self.radios, 'value'),
            prevent_initial_call=True,
        )
        def callback_time_offset(value):
            match = re.match(r'(\w+)=(\d+)', value)
            if match is None:
                return None
            
            (key, val) = match.groups()
            offset_data = {key: int(val)}

            return offset_data


class TimeOffset():
    def __init__(self, offset_store_id):
        self.offset_store_id = offset_store_id

    def display(self):
        radios = TimeOffsetRadios(self.offset_store_id).display()

        return html.Div(
            children=[
                html.P('Periodo de visualización:'),
                radios,
            ],
            style={
                'display': 'flex',
                'gap': '1rem',
            }
        )
