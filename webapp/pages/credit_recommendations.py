import uuid

import dash_bootstrap_components as dbc
import pandas as pd

from dash import callback, dcc, html, no_update, register_page
from dash.dependencies import Input, Output, State

from components.input.upload_credit_recomm import UploadInputCreditRecomm
from components.tables.recomm import RecommTable
from content.pages_constants import PAGE_NAME_CREDIT_RECOMM, PAGE_TITLE_COMPLEMENT


register_page(
    __name__,
    path="/credit-recommendations",
    name=PAGE_NAME_CREDIT_RECOMM,
    title=PAGE_NAME_CREDIT_RECOMM + PAGE_TITLE_COMPLEMENT
)


recomm_table = RecommTable(id='recommend-feedback')
recomm_table_table_component = recomm_table.display()
(outputs, update_fn) = recomm_table.get_outputs_n_update_fn()

layout = html.Div(
    children=[
        html.Div(id="session_identifier"),
        UploadInputCreditRecomm(
            id_suffix='credit-recommendations',
            outputs=outputs,
            update_fn=update_fn,
        ).display(),
        recomm_table_table_component,
    ],
    style=dict(
        display='flex',
        flexDirection='column',
        gap='1rem',
    ))
