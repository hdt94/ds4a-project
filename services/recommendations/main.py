import os

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, UploadFile

from recommending import Models
from utils.upload import UnsupportedContentType, UploadIO


ROOT_APP_DIR = os.path.dirname(os.path.abspath(__file__))

# environment
env_file = os.path.join(ROOT_APP_DIR, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

env_file = os.path.join(ROOT_APP_DIR, 'envvars')
if os.path.exists(env_file):
    load_dotenv(env_file)

MODELS_DIR = os.environ.get('MODELS_DIR', os.path.join(ROOT_APP_DIR, 'models'))


# models
recomm = Models()
recomm.load_models(MODELS_DIR)


# app
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/predict")
async def upload(file: UploadFile):
    upload = UploadIO(file)
    try:
        df = await upload.read()
    except UnsupportedContentType as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        detail = f'Unexpected exception: {str(e)}'
        raise HTTPException(status_code=422, detail=detail)

    (error, defaulting_df) = recomm.predict(df)
    if (error):
        raise HTTPException(status_code=422, detail=error)

    return defaulting_df.to_dict('records')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        debug=True,
        host=os.environ.get('HOST', '127.0.0.1'),
        log_level="debug",
        port=int(os.environ.get('PORT', '8000')),
        workers=1,
    )
