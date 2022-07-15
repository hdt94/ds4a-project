from dash import callback, dcc, dash_table, html, no_update
from dash.dependencies import Input, Output, State


class RecommTable():
    def __init__(
        self,
        id=None,
        sort_action=None,
    ):
        self.id = id
        self.sort_action = sort_action

    def display(self):
        table_args = {
            'export_format': 'csv',
            'export_headers': 'ids',
            'style_table': {'overflow': 'auto'},
        }
        if (self.id):
            table_args['id'] = self.id
        if (self.sort_action):
            table_args['sort_action'] = self.sort_action

        self.layout = dash_table.DataTable(**table_args)

        return self.layout

    def get_outputs_n_update_fn(self):
        outputs = [
            Output(self.layout, 'columns'),
            Output(self.layout, 'data'),
        ]
        update_fn = self.update_recomm_table

        return (outputs, update_fn)

    def update_recomm_table(self, df=None):
        if df is None:
            return (no_update, no_update)

        df = (
            df
            .replace({
                'DEFAULTING': {
                    0: 'Otorgar crédito',
                    1: 'No otogar crédito',
                }
            })
            .rename(columns={
                'DEFAULTING': 'RECOMENDACIÓN'
            })
        )
        columns = [{'name': i, 'id': i, } for i in df.columns]
        data = df.to_dict('records')

        return (columns, data)
