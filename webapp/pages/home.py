import os

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from dash import html, dcc, callback, register_page
from dash.dependencies import Input, Output, State

from content.pages_constants import PAGE_NAME_HOME, PAGE_TITLE_COMPLEMENT


register_page(
    __name__,
    path="/",
    name=PAGE_NAME_HOME,
    title=PAGE_NAME_HOME + PAGE_TITLE_COMPLEMENT
)


def layout():
    CONTENT_DIR = os.environ.get('CONTENT_DIR')
    file_path = os.path.join(CONTENT_DIR, 'home.md')

    with open(file_path, 'r', encoding='utf-8') as f:
        markdown = f.read()

    return dbc.Container(
        fluid=True,
        children=dcc.Markdown(markdown)
    )
