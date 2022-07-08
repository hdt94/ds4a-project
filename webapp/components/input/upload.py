import base64
import datetime

import dash_bootstrap_components as dbc

from dash import html, dcc, callback, dash_table, no_update
from dash.dependencies import Input, Output, State

from utils.upload import UploadIO


def render_reading_exception(upload, exc):
    file_name = upload.file_name
    error_name = exc.__class__.__name__
    error_message = str(exc)

    return html.P(
        className='alert alert-danger',
        children=[
            html.Strong(f'{file_name} - {error_name}'),
            f': {error_message}'
        ])


def render_unsupported_upload(u):
    return html.P(
        className='alert alert-danger',
        children=[
            html.Strong(f'{u.file_name} - Formato no soportado'),
            f': {u.content_type}'
        ])


def render_upload(upload):
    df = upload.df.head(10)

    return html.Div([
        html.H5(upload.file_name),
        html.H6(datetime.datetime.fromtimestamp(upload.modified_date)),
        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),
    ])


class UploadInput(object):
    def __init__(
        self,
        id_suffix,
        outputs,
        upload_fn,
        reading=True,
        rendering_uploads=False,
    ):
        self.upload_id = f'upload-data-{id_suffix}'
        self.output_id = f'output-upload-data-{id_suffix}'
        self.outputs = outputs
        self.reading = reading
        self.rendering_uploads = rendering_uploads
        self.upload_fn = upload_fn

    def display(self):
        layout = self.render_components()
        self.register_callbacks()

        return layout

    def register_callbacks(self):
        @callback(
            Output(self.output_id, 'children'),
            *self.outputs,
            Input(self.upload_id, 'contents'),
            State(self.upload_id, 'filename'),
            State(self.upload_id, 'last_modified'),
            prevent_initial_call=True,
        )
        def upload_main_callback(contents, filenames, dates):
            no_updates = [no_update for n in self.outputs]

            if contents is None:
                return ([], *no_updates)

            uploads = [
                UploadIO(c, n, d) for c, n, d in
                zip(contents, filenames, dates)
            ]

            unsupported = [u for u in uploads if u.validate_support() == False]
            if (len(unsupported) > 0):
                children = [render_unsupported_upload(u) for u in unsupported]
                return (children, *no_updates)

            if self.reading:
                for u in uploads:
                    try:
                        u.read()
                    except Exception as e:
                        children = render_reading_exception(u, e)
                        return (children, *no_updates)

            (error_layout, *values) = self.upload_fn(uploads)
            if (error_layout):
                return (error_layout, *no_updates)
            elif (self.rendering_uploads):
                children = [render_upload(u) for u in uploads]
                return (children, *values)
            else:
                return (no_update, *values)

    def render_components(self):
        return dbc.Container(
            [
                dcc.Upload(
                    id=self.upload_id,
                    children=html.Div([
                        'Agregar archivos\n(click o arrastre)',
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px',
                        'cursor': 'pointer',
                        'userSelect': 'none',
                    },
                    multiple=True
                ),
                html.Div(id=self.output_id),
            ]
        )
