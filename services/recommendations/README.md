# Recommendations service - DS4A Capstone Project - Team 60

## Production

```bash
docker build -t recomm .
docker run \
    --name recomm \
    -p 80:80 \
    recomm
```

> Notes: Dockerfile here is based on `tiangolo/uvicorn-gunicorn` image container ([link](https://github.com/tiangolo/uvicorn-gunicorn-docker)) for running multiple proceses in single container. Read carefully FastAPI docs regarding usage of container images, especially, for horizontal scaling using single-process containers: [https://fastapi.tiangolo.com/deployment/docker/](https://fastapi.tiangolo.com/deployment/docker/)

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

Environment variables in `.env` or `envvars` optionally including:
```
MODELS_DIR=
HOST=
PORT=
```
> Note: HOST and PORT environment variables are meant to be used for debugging from VSCode or similar


## Usage

Service only supports XLSX files and CSV files encoded as utf-8.

Example:

```python
import requests

URL = 'http://localhost:8080/predict'

file_name = 'X_test.csv'
files = {'file': (file_name, open(file_name, 'rb'), 'text/csv')}
res = requests.post(URL, files=files)
print(res.json())
```

Alternatively:

```bash
curl -v -F "file=@X_test.csv;type=text/csv" http://localhost:8080/predict
```

```bash
TYPE=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
curl -v -F "file=@X_test.xlsx;type=${TYPE}" http://localhost:8080/predict
```