import json
import os
from turtle import up

from urllib.parse import urljoin

import requests

from utils.upload import UploadIO


RECOMMEND_URL = os.environ.get('RECOMMEND_URL', None)

if RECOMMEND_URL is None:
    raise ValueError('RECOMMEND_URL has not been defined')


def request_recommendations(upload):
    """Request recommendations uploading file as multipart form data
    
        Output parameteres:
            (error_text, recommendations)
    """

    assert isinstance(upload, UploadIO), 'Invalid upload argument'

    url = urljoin(RECOMMEND_URL, '/predict')
    body = {
        'file': (upload.file_name,  upload.decode(), upload.content_type)
    }
    res = requests.post(url, files=body)

    if res.ok:
        recommendations = json.loads(res.text)
        return (None, recommendations)

    error = res.text
    return (error, None)
