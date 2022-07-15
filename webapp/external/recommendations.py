import os

from urllib.parse import urljoin

import pandas as pd
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
        recomm_df = pd.DataFrame(res.json())
        return (None, recomm_df)

    error = res.text
    return (error, None)
