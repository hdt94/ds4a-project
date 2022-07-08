


## Production

PENDING

## Development

Runtime:
> Note: unix-like system is encouraged for compatibility with libraries such as scikit-learn.
```bash
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.common.txt -r requirements.dev.txt
uvicorn main:app --reload
```

Alternative custom options:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Environment variables in `.env` or `envvars`:
```

```

Optionally, include:
```
MODELS_DIR=
HOST=
PORT=
> Note: HOST and PORT environment variables are meant to be used for debugging from VSCode or similar
```





## Testing


Service only support CSV files encoded as utf-8

```
import requests


```



Monto
        # model_lin = sm.ols(formula = formula_lin, data = df_train.query('SUELDO_BASICO > 0')).fit()
        # print(model_lin.summary())