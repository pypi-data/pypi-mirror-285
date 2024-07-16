# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def api_middleware(app: FastAPI):
    """A middleware function that adds CORS (Cross-Origin Resource Sharing) middleware to FastAPI application.
       Goal is to filter requests origin:  Now, setup to any origin.

    Args:
    - app: FastAPI application to which CORS middleware will be added.

    TODO: Add more origin filtering if needed.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
