import re

from dash import no_update
from dash.dependencies import Output

from components.input.upload import UploadInput
from external.datasets import add_dataset


def render_unknown_dataset(upload):
    pass

def render_upload_error(e, upload):
    pass

def upload_files(uploads):
    names = ':'.join([u.file_name for u in uploads]).lower()
    cartera_output = True if 'cartera' in names else no_update
    colocacion_output = True if 'colocacion' in names else no_update

    datasets = []
    for u in uploads:
        match = re.search('(cartera|colocacion)', u.file_name.lower())
        if match is None:
            return (render_unknown_dataset(u), no_update, no_update)

        dataset = match.group()
        datasets.append(dataset)

    try:
        for (d, u) in zip(datasets, uploads):
            add_dataset(d, u.df)

    except Exception as e:
        return (render_upload_error(e, u), no_update, no_update)

    return (None, cartera_output, colocacion_output)


class UploadInputDatasets(UploadInput):
    def __init__(self, id_suffix, cartera_signal, colocacion_signal):
        super().__init__(
            id_suffix=id_suffix,
            outputs=[
                Output(cartera_signal, 'data'),
                Output(colocacion_signal, 'data'),
            ],
            upload_fn=upload_files
        )


# UploadInput = UploadInput(
#     id_suffix='stats',
#     # content_fn = lambda x: True,
#     # validate_fn=lambda x: True,
#     # extra_callbacks=[upload_files],
#     # extra_states=[State(sig_new_colocacion, 'data')],
#     outputs=[
#         Output(sig_new_cartera, 'data'),
#         Output(sig_new_colocacion, 'data'),
#     ],
#     rendering_uploads=True,
#     upload_fn=upload_files,
# ).display()
