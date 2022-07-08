FROM python:3.8

WORKDIR /app/

COPY requirements.*.txt ./
RUN pip install \
    --no-cache-dir \
    --upgrade \
    -r requirements.common.txt \
    -r requirements.prod.txt
COPY ./packages/ ./packages
RUN pip install ./packages/core_ds4a_project/

ENV ENV=production
ENV CONTENT_DIR=/app/content

COPY . ./

CMD gunicorn -b 0.0.0.0:80 app:app.server --workers 4
