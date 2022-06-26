## Cleaning - DS4A Capstone Project - Team 60

We did an extensive cleaning of data considering the multiple issues of the raw data provided by entity, who exported datasets from two source information systems comitting some bad practices that lead to inconsistencies and required especial focusing.

Thinking in future improvement for entity, the following are some recommendations to fix such bad practices along with examples of what we found in raw datasets:
- Avoid distributing sensitive data such as document identity number (e.g. CEDULA, CODEUDOR) and personal contact information (e.g. CELULAR, CORREO).
- Preserve normalization in data.
- Usage of a single naming convention of columns. For example:
    - Some datasets prefix date columns names with "FEC" while others with "FECHA".
    - Some datasets were exported keeping spaces in columns names while others using underscores replacing spaces.
- Usage of a single convention for money values. For example, there are money values where thousands are indicated with commas while other values do not use thousands character.
- Provide a data dictionary to specify meaning of variables and all possible value forms, especialy, for those of variable values with multiple information. For instance, CODEUDOR column in COLOCACION dataset required to be pre-processed to extract useful information, considering also that such column contains sensitive data.
- If data manipulation is required, keep consistent such modifications. For instance, records in CARTERA from FECHA_CIERRE=2019-12 had TASA_ANUAL and TASA_PERIODICA values mulitplied by 100 regarding the order of all other values.


## Renaming columns

We need to rename columns from all datasets considering there are spacing characters such as tabs and new lines in some columns' names, and there are typos that lead to different column names in multiple files containing the same variable.

Optionally, you can try directly using renaming

```python
with open(f'{ROOT_DATA_PATH}/dict-renaming-raw-columns.json', 'r') as f:
    renaming_dict = json.load(f)

for df in dfs:
    df.columns = pd.Series(df.columns).replace(renaming_dict)

df = pd.concat(dfs)
df.shape
```


## PENDING

```python
import json

with open(f'{ROOT_DATA_PATH}/dict-valid-relations-identifiers.json', 'r') as f:
    ids = json.load(f)

list(ids.keys())
```

```python
import core

RelationsFilter.load
```