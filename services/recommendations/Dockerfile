FROM tiangolo/uvicorn-gunicorn:python3.8

WORKDIR /app/

COPY ./requirements.*.txt ./
RUN pip install \
    --no-cache-dir \
    --upgrade \
    -r ./requirements.common.txt \
    -r ./requirements.prod.txt

COPY ./ /app/app
