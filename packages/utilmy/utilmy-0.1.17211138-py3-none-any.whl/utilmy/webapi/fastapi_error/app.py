from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import BaseModel, Field, ValidationError, validator
from requests.exceptions import ConnectionError
from fastapi import BackgroundTasks
import fastapi
from exception import PlaygroundError, handle_exception
from middleware import CustomMiddleware


def add_exception_handler(app):
    app.add_exception_handler(PlaygroundError, handle_exception)
    app.add_exception_handler(Exception, handle_exception)
    pass


app = FastAPI()
add_exception_handler(app)
app.add_middleware(CustomMiddleware)


async def background_task():
    raise PlaygroundError("custom error", 3000)


@app.get("/")
def index(bg: BackgroundTasks):
    bg.add_task(background_task)
    # raise PlaygroundError("custom error", 3000)
    return {"message": "Hello World"}


@app.post("/api/callback")
def callback(payload: dict):
    print(payload)
    return {"message": "Recieved callback"}