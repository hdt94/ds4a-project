import os

from sys import gettrace as sys_gettrace

import dash
import dash_bootstrap_components as dbc

from dotenv import load_dotenv

from layout import init_layout


# environment
dir_path = os.path.dirname(os.path.realpath(__file__))

env_file = os.path.join(dir_path, 'envvars')
if os.path.exists(env_file):
    load_dotenv(env_file)

env_file = os.path.join(dir_path, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

DEBUG_DASH = os.environ.get('DEBUG', '').lower() in ['true', '1']
DEBUG_PYTHON = sys_gettrace() is not None
DEV = os.environ.get('ENV', 'production').lower() == 'development'

# app
request_path_prefix = '/'
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    requests_pathname_prefix=request_path_prefix,
    use_pages=True,
)
app.config.suppress_callback_exceptions = True
init_layout(app, request_path_prefix)

# Importing here prevents caching before app is instantiated
from external.datasets import update_cache
update_cache()

# Testing server, don't use in production
if (__name__ == '__main__'):
    if DEBUG_DASH or DEV:
        # `debug=True` for Dash debugger
        app.run(host='0.0.0.0', port=8050, debug=True)
    elif DEBUG_PYTHON:
        # `debug=False` for VSCode debugger
        app.run(host='0.0.0.0', port=8050, debug=False)
    else:
        raise ValueError('Unknown proper local configuration')
