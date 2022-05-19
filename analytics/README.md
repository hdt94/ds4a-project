# Analytics DS4A Capstone Project - Team 60

Following directories are considered:
- `cleaning`: stuff related to cleaning data.
- `core_ds4a_project`: local package with definitions shared for analytics.
- `exploring`:
- `modeling`:

## Data

Download/Upload data from/to object storage service:

TODO setup object storage service

We've considering following directories of data:

- `RAW_DATA_PATH`: directory path with raw data files brought by client.
- `CLEAN_DATA_PATH`: directory path with data files after cleaning and wrangling.

We've adopted following optional convention based on a root directory of data for notebooks and scripts:

```python
ROOT_DATA_PATH = os.environ.get('ROOT_DATA_PATH')
RAW_DATA_PATH = os.environ.get('RAW_DATA_PATH') or f'{ROOT_DATA_PATH}/raw'
CLEAN_DATA_PATH = os.environ.get('CLEAN_DATA_PATH') or f'{ROOT_DATA_PATH}/clean'
```

So, you can setup a single root directory of data or setup custom locations. All through environment variables.

## Environment

### `.env` or `environment`

Use `.env` or `envvars` files to configure environment variables for scritps and notebooks.

> Note: notebooks load `envvars` file in the its same containing directory. Naming environment file as `envvars` instead of `.env` is because of `jupyterlab<3.2` doesn't show hidden files ([link](https://github.com/jupyterlab/jupyterlab/issues/2049)).

Examples of `envars`:

- Using convention of based on `ROOT_DATA_PATH`:
    ```
    ROOT_DATA_PATH=/ds4a-project/data
    ```

    ```
    ROOT_DATA_PATH=C:\ds4a-project\data
    ```

- Using custom paths:
    ```
    RAW_DATA_PATH=/custom-dir/rawdata/
    CLEAN_DATA_PATH=/custom-dir/cleandata/
    ```

    ```
    RAW_DATA_PATH=C:\custom-dir\rawdata\
    CLEAN_DATA_PATH=C:\custom-dir\cleandata\
    ```

### Exploration

Environment with `conda` (multiplatform):
```
conda create -n ds4a python=3.8
conda activate ds4a
conda install --file requirements.common.txt --file requirements.jupyter.txt
conda develop core_ds4a_project
```

Environment with `venv + pip` in Linux or macOS:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.common.txt -r requirements.jupyter.txt
pip install -e core_ds4a_project
```

Environment with `venv + pip` in Windows:
```
python -m venv venv
./venv/Scripts/activate.bat
pip install -r requirements.txt
pip install -e core_ds4a_project
```

### Production

Environment with `conda` (multiplatform):
```
conda create -n ds4a python=3.8
conda activate ds4a
conda install --file requirements.common.txt --file requirements.production.txt
```

Environment with `venv + pip` in Linux or macOS:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.common.txt -r requirements.production.txt
```


### Editor

Following are some values we use for VSCode JSON configuration file:
```json
{
    "notebook.output.textLineLimit": 150,
}
```

