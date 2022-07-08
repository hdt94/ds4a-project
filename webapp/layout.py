from urllib.parse import urljoin

import dash
import dash_bootstrap_components as dbc

from dash import dcc, html


def display_nav_links(path_prefix):
    modules = [
        "pages.home",
        "pages.stats",
        "pages.credit_recommendations",
    ]
    pages = [dash.page_registry[m] for m in modules]

    return html.Div(
        style={"display": "flex"},
        children=[
            dbc.NavItem(
                dbc.NavLink(
                    page["name"],
                    href=urljoin(path_prefix, page["path"])
                )
            )
            for page in pages
        ]
    )


def init_layout(app, path_prefix):
    navbar = dbc.Navbar(
        color='w',
        children=dbc.Container(
            fluid=True,
            children=[
                html.Img(src="/assets/logo.jpg", height="60px",),
                display_nav_links(path_prefix),
            ],
        ),
    )
    content = dbc.Container(
        children=dash.page_container,
        fluid=True,
        style={
            'padding': '0 1.5rem 2rem 1.5rem',
        }
    )

    app.layout = html.Div(
        [
            navbar,
            content
        ],
    )
