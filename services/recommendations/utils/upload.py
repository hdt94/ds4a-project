import io

import pandas as pd


CSV_CONTENT_TYPE = 'text/csv'
EXCEL_CONTENT_TYPES = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]


class UnsupportedContentType(ValueError):
    pass


class UploadIO():
    def __init__(self, file):
        self.content_type = file.content_type
        self.file = file

    def iscsv(self):
        return self.content_type == CSV_CONTENT_TYPE

    def isexcel(self):
        return self.content_type in EXCEL_CONTENT_TYPES

    async def read(self):
        decoded_bytes = await self.file.read()

        if self.iscsv():
            df = pd.read_csv(io.StringIO(decoded_bytes.decode('utf-8')))
        elif self.isexcel():
            df = pd.read_excel(io.BytesIO(decoded_bytes))
        else:
            raise UnsupportedContentType(
                f'Unsupported content type: "{self.content_type}"')

        return df

    def validate_support(self):
        return self.iscsv() or self.isexcel()
