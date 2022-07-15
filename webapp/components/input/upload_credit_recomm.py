import re

from dash import callback, dcc, html, no_update, register_page
from dash.dependencies import Output

from components.input.upload import UploadInput
from external.recommendations import request_recommendations


def render_upload_error(message):
    error_layout = html.P(
            html.Strong(message),
            className='alert alert-danger',
        )

    return error_layout


class UploadInputCreditRecomm(UploadInput):
    def __init__(self, id_suffix, outputs, update_fn):
        self.update_fn = update_fn

        super().__init__(
            id_suffix=id_suffix,
            outputs=outputs,
            upload_fn=self.upload
        )

    def upload(self, uploads):
        if len(uploads) != 1:
            error_layout = render_upload_error(
                'Debe subir un único archivo para recomendaciones')

            return (error_layout,)

        (error, recomm_df) = request_recommendations(uploads[0])
        if (error):
            error_layout = render_upload_error(
                f'Error subiendo el archivo: "{error}"')
            
            return (error_layout,)

        try:
            error_layout = None
            output_values = self.update_fn(recomm_df)
        except Exception as ex:
            error_layout = render_upload_error(
                f'Error actualizando datos: "{ex}"')
            output_values = []

        return (error_layout, *output_values)
