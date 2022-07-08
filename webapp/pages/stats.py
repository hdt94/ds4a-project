import dash_bootstrap_components as dbc

from dash import html, dcc, register_page

from components.tables.cierre import CierreTable
from components.graphs import cartera
from components.graphs import colocacion
from components.input.cartera import CierreInput
from components.input.history import TimeOffset
from components.input.upload_datasets import UploadInputDatasets

from content.pages_constants import PAGE_NAME_STATS, PAGE_TITLE_COMPLEMENT


register_page(
    __name__,
    path="/stats",
    name=PAGE_NAME_STATS,
    title=PAGE_NAME_STATS + PAGE_TITLE_COMPLEMENT
)

cartera_signal = dcc.Store(id='signal_new_cartera', data='')
colocacion_signal = dcc.Store(id='signal_new_colocacion', data=1)

cierre_dropdown_id = 'cartera-cierre-dropdown'
cierre_hist_id = 'cierre-hist-table'
offset_store_id = 'time-offset-id'


def render_graphs_row(graphs, col_kwargs={}):
    return dbc.Row([
        dbc.Col(graph.display(), **col_kwargs)
        for graph in graphs
    ])


UploadInput = UploadInputDatasets(
    id_suffix='stats',
    cartera_signal=cartera_signal,
    colocacion_signal=colocacion_signal,
).display()

s1 = html.Section(
    children=[
        html.H2('Estadísticas de cierre'),
        CierreInput(cartera_signal, cierre_dropdown_id).display(),
        CierreTable(
            cartera_signal,
            cierre_id=cierre_dropdown_id,
        ).display(),
        html.Ul([
            html.Li('Cifras en miles de millones'),
            html.Li([
                'Al final de la página se encuentra un ',
                html.A('comparativo histórico de cierre',
                       href=f'#{cierre_hist_id}')
            ]),
        ]),
        render_graphs_row(
            graphs=[
                colocacion.ColocacionLocalizacion(
                    colocacion_signal, cierre_dropdown_id), ],
            col_kwargs={"md": 12}
        ),
    ],
    style={
        'display': 'flex',
        'flex-direction': 'column',
        'gap': '1rem',
    }
)


s2 = html.Section([
    html.H2('Estadísticas históricas'),
    TimeOffset(offset_store_id).display(),
    render_graphs_row(
        graphs=[
            colocacion.ColocacionHistorico(colocacion_signal, offset_store_id),
            cartera.Fugas(cartera_signal, offset_store_id),
        ],
        col_kwargs={"md": 6}
    ),
    render_graphs_row(
        graphs=[
            cartera.Saldo(cartera_signal, offset_store_id),
            cartera.SaldoLocacion(cartera_signal, offset_store_id),
        ],
        col_kwargs={"md": 6}
    ),
    render_graphs_row(
        graphs=[
            cartera.SaldoCalificacion(cartera_signal, offset_store_id),
            cartera.Calificaciones(cartera_signal, offset_store_id),
        ],
        col_kwargs={"md": 6}
    ),
    html.Div(
        [
            html.P('Comparativo histórico de cierre:'),
            html.Ul([
                html.Li('Cifras en miles de millones'),
            ]),
            CierreTable(
                cartera_signal,
                offset_store_id=offset_store_id,
                sort_action='native',
            ).display(),
        ],
        id=cierre_hist_id,
    ),
    render_graphs_row(
        graphs=[
            colocacion.ColocacionCrecimiento(
                colocacion_signal, offset_store_id),
        ],
    ),

])

layout = html.Div([
    cartera_signal,
    colocacion_signal,
    UploadInput,
    s1,
    s2,
])
