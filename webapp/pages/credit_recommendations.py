import uuid

import dash_bootstrap_components as dbc
import pandas as pd

from dash import callback, dcc, html, no_update, register_page
from dash.dependencies import Input, Output, State

from components.input.upload import UploadInput
from content.pages_constants import PAGE_NAME_CREDIT_RECOMM, PAGE_TITLE_COMPLEMENT
from external.recommendations import request_recommendations


register_page(
    __name__,
    path="/credit-recommendations",
    name=PAGE_NAME_CREDIT_RECOMM,
    title=PAGE_NAME_CREDIT_RECOMM + PAGE_TITLE_COMPLEMENT
)


def render_recommendations(recommendations):

    return recommendations['columns']


def render_upload_error(message):
    error_layout = html.P(
            html.Strong(message),
            className='alert alert-danger',
        )

    return error_layout


def upload_fn(uploads):
    if len(uploads) != 1:
        error_layout = render_upload_error(
            'Debe subir un único archivo para recomendaciones')

        return (error_layout, no_update)

    (error, recomm) = request_recommendations(uploads[0])
    if (error):
        error_layout = render_upload_error(
            f'Error subiendo el archivo: "{error}"')
        
        return (error_layout, no_update)

    recomm_layout = render_recommendations(recomm)

    return (None, recomm_layout)


recommend_id = 'recommend-feedback'
session_uuid_id = str(uuid.uuid4())

layout = html.Div([
    dcc.Store(data=session_uuid_id, id='session-id'),
    dcc.Store(data='', id='bull'),
    html.Div(id="session_identifier"),
    UploadInput(
        id_suffix='credit-recommendations',
        upload_fn=upload_fn,
        outputs=[Output(recommend_id, 'children')],
    ).display(),
    html.Div(id=recommend_id),
])

@callback(
    Output('session_identifier', 'children'),
    Input('session-id', 'data'),
)
def update_session_message(session):
    return f"your session is {session}"
