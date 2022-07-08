import base64
import io
import re

import pandas as pd


CSV_CONTENT_TYPE = 'text/csv'
EXCEL_CONTENT_TYPES = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]


class UploadIO(object):
    def __init__(self, contents, file_name, modified_date):
        full_content_type, content_string = contents.split(',')
        content_type = re.match('data:(.+);base64', full_content_type).group(1)

        self.content_string = content_string
        self.content_type = content_type
        self.df = None
        self.file_name = file_name
        self.modified_date = modified_date

    def iscsv(self):
        return self.content_type == CSV_CONTENT_TYPE

    def isexcel(self):
        return self.content_type in EXCEL_CONTENT_TYPES

    def decode(self):
        if self.iscsv():
            decoded_bytes = (
                base64
                .b64decode(self.content_string)
                .decode('utf-8')
            )
        elif self.isexcel():
            decoded_bytes = base64.b64decode(self.content_string)
        else:
            raise ValueError(
                f'Unsupported content type: "{self.content_type}"')

        return decoded_bytes

    def read(self, inplace=True):
        decoded_bytes = self.decode()

        if self.iscsv():
            df = pd.read_csv(io.StringIO(decoded_bytes))
        elif self.isexcel():
            df = pd.read_excel(io.BytesIO(decoded_bytes))
        else:
            raise ValueError(
                f'Unsupported content type: "{self.content_type}"')

        if (inplace):
            self.df = df
        else:
            return df

    def validate_support(self):
        return self.iscsv() or self.isexcel()
