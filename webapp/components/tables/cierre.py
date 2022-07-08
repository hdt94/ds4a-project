from datetime import datetime

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import callback, dcc, dash_table, html
from dash.dependencies import Input, Output, State

from external import datasets


class CierreTable():
    def __init__(
        self,
        signal_update,
        id=None,
        cierre_id=None,
        offset_store_id=None,
        sort_action=None,
    ):
        self.signal_update = signal_update
        self.id = id
        self.cierre_id = cierre_id
        self.offset_store_id = offset_store_id
        self.sort_action = sort_action

    def display(self):
        table_args = {
            'style_table': {'overflow': 'auto'},
        }
        if (self.id):
            table_args['id'] = self.id
        if (self.sort_action):
            table_args['sort_action'] = self.sort_action

        self.layout = dash_table.DataTable(**table_args)
        self.register_callbacks()

        return self.layout

    def register_callbacks(self):
        if (self.cierre_id):
            @callback(
                Output(self.layout, 'columns'),
                Output(self.layout, 'data'),
                Input(self.signal_update, 'data'),
                Input(self.cierre_id, 'value'),
                prevent_initial_call=False,
            )
            def update_table(_, cierre_date):
                df = datasets.stats_cierre(dataviz=True)

                cierre_date = datetime.strptime(cierre_date, '%Y-%m-%d').date()
                df = df.query('FECHA_CIERRE == @cierre_date')

                if (df.shape[0] == 0):
                    return ([], [])

                columns = [{'name': i, 'id': i} for i in df.columns]
                data = df.to_dict('records')

                return (columns, data)
        elif (self.offset_store_id):
            @callback(
                Output(self.layout, 'columns'),
                Output(self.layout, 'data'),
                Input(self.signal_update, 'data'),
                Input(self.offset_store_id, 'data'),
                prevent_initial_call=False,
            )
            def update_table(_, offset_data):
                df = datasets.stats_cierre(dataviz=True)
                df = datasets.filter_dataframe(
                    df, 'FECHA_CIERRE', offset_data)
                columns = [{'name': i, 'id': i, } for i in df.columns]
                data = df.to_dict('records')

                return (columns, data)
