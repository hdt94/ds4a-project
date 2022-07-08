import dash_bootstrap_components as dbc

from dash import callback, dcc, html
from dash.dependencies import Input, Output

from external.datasets import get_cartera_cierre_values


class CierreInput():
    def __init__(self, signal_update, id):
        self.signal_update = signal_update
        self.id = id

    def display(self):
        self.layout = html.Div(
            children=[
                html.P('Fecha de cierre:'),
                dcc.Dropdown(
                    id=self.id,
                    style={'flex': '1', 'paddingLeft': '1em'},
                )
            ],
            style={'display': 'flex'}
        )
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        @callback(
            Output(self.id, 'options'),
            Output(self.id, 'value'),
            Input(self.signal_update, 'data'),
            prevent_initial_call=False,
        )
        def update_dropdown(_):
            options = get_cartera_cierre_values()
            value = options[0]

            return (options, value)
