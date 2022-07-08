# Webapp DS4A Capstone Project - Team 60

## Up and running

### Production

```bash
ANALYTICS_DIR=$PROJECT_ROOT/analytics/
mkdir -p

mkdir -p packages/
cp $PROJECT_ROOT/requirements.common.txt $PROJECT_ROOT/requirements.production.txt packages/
cp -r ${ANALYTICS_DIR}/core_ds4a_project/ ./packages
cp -r $PROJECT_ROOT/analytics/core_ds4a_project packages/core_ds4a_project
docker run \
    --name dash-app \
    -p 80 \
    -e REDIS_URL=redis://localhost:6379 \
    .
```

### Development

Environment with `venv + pip` in Linux or macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

Environment with `venv + pip` in Windows:
```bash
python -m venv venv
./venv/Scripts/activate.bat
```

Dependencies:
> Note: syntax is compatible with GitBash on Windows.
```
ANALYTICS_DIR=$PROJECT_ROOT/analytics/
pip install \
    -r requirements.common.txt \
    -r requirements.dev.txt \
    -r "${ANALYTICS_DIR}/requirements.common.txt" \
    -r "${ANALYTICS_DIR}/requirements.jupyter.txt"
pip install -e "${ANALYTICS_DIR}/core_ds4a_project"
```

Example of environment variables in `.env` or `envvars` file:
```
ENV=development
CONTENT_DIR=${PWD}/content
DATASETS_DIR=$PROJECT_ROOT/data/clean
REDIS_URL=redis://localhost:6379
RECOMMEND_URL=http://localhost:8000
```

Running with integrated debugger from Dash:
```bash
debug=1 python app.py
```

Ignore `debug=1` if using Python debugger from VSCode or similar.

### Additionals

In Unix=like it may be required to install 

## Notes

### Stats - testing data

```python
import pandas as pd

CLEAN_DATA_PATH=

df = pd.read_csv(f'{CLEAN_DATA_PATH}\COLOCACION.csv')
df['FECHA_DESEMBOLSO'] = pd.to_datetime(df['FECHA_DESEMBOLSO'], format='%Y-%m-%d')

offset = pd.tseries.offsets.DateOffset(months=6)
cutoff = df['FECHA_DESEMBOLSO'].max() - offset
df_offset = df.query('FECHA_DESEMBOLSO > @cutoff')
df_offset['FECHA_DESEMBOLSO'] += offset

df_offset.to_csv(f'{CLEAN_DATA_PATH}\COLOCACION_OFFSET.csv', index=False)
```

### Unknown error `ValueError: Invalid value`

As of 2022-07-07 using `plotly==5.9.0`, there is a random `ValueError: Invalid value` from Plotly that is not consistent in ocurrence but that affects rendering of graphs.

It is solved in this app by duplicating graph code in exception handling as also indicated in: [https://community.plotly.com/t/inconsistent-callback-error-updating-scatter-plot/46754/8](https://community.plotly.com/t/inconsistent-callback-error-updating-scatter-plot/46754/8)

See also following references:
- [https://community.plotly.com/t/valueerror-invalid-value-in-basedatatypes-py/55993/7](https://community.plotly.com/t/valueerror-invalid-value-in-basedatatypes-py/55993/7)
- [https://github.com/plotly/plotly.py/issues/3441](https://github.com/plotly/plotly.py/issues/3441)
