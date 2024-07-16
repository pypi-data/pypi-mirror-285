# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from src.utils.util_log import log, loge, logw

"""
2 ways :
     1) Add in the middleware: Same for all endpoints

    2) Custom ways : just add Try .... except 
          and return the specific JSON ERROR message

      Why ?
        More flexibility, for end endpoint
        if middleware is buggy (for some reasons). --> does not impact error return
          Loose coupling with middleware part.
            Only coupling with endpoint
            Only string processing....

         if somebody adds a new middleware stuff (XYZ) ---> it can broke the return error message 

       it will work at 99.99% time even if we change middleware,......  
       very independant code.


    How do you the HTTP error handling ?
       1) Base is to use the middleware : middleware code is copy/paste from another libraries

          2) if this endpoint has custom processing --> specific error handling...

Common error HTTP status codes include:
  400 Bad Request - This means that client-side input fails validation.     
  401 Unauthorized - This means the user isn't not authorized to access a resource. It usually returns when the user isn't authenticated.
     no need to log, to prevent too much loggging in database...

  500 Internal server error - This is a generic server error. It probably shouldn't be thrown explicitly.
     Add internal logg for check

420:  custom based on the App logic.
403 Forbidden.  - This means the user is authenticated, but it's not allowed to access a resource.
404 Not Found   - This indicates that a resource is not found.
502 Bad Gateway - This indicates an invalid response from an upstream server.
503 Service Unavailable - This indicates that something unexpected happened on server side (It can be anything like server overload, some parts of the system failed, etc.).



"""

#########################################################################################
######## Error Handling #################################################################
def http_exception_handler(exc: HTTPException, msg:str=""):
    jmsg = {"code": exc.status_code, "message": "Error", "detail":  str(msg) + "," +  exc.detail }
    loge(str(jmsg))
    return JSONResponse(status_code=exc.status_code, content=jmsg)


def value_error_handler(exc):
    jmsg = {"code": 400, "message": "Error", "detail": str(exc)}
    loge(str(jmsg))
    return JSONResponse(status_code=400, content=jmsg)


def exception_handler(exc):
    jmsg = {"code": 500, "message": "Error", "detail": str(exc)}
    loge(str(jmsg))
    return JSONResponse(status_code=500, content=jmsg)


def api_error_handler(app: FastAPI):
    """error handler for handling different types of exceptions in FastAPI application."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler_(request, exc: HTTPException):
        jmsg = {"code": exc.status_code, "message": "Error", "detail": exc.detail}
        loge(str(jmsg))
        return JSONResponse(status_code=exc.status_code, content=jmsg)

    @app.exception_handler(ValueError)
    async def value_error_handler_(request, exc):
        jmsg = {"code": 400, "message": "Error", "detail": str(exc)}
        loge(str(jmsg))
        return JSONResponse(status_code=400, content=jmsg)

    @app.exception_handler(Exception)
    async def exception_handler_(request, exc):
        jmsg = {"code": 500, "message": "Error", "detail": str(exc)}
        loge(str(jmsg))
        return JSONResponse(status_code=500, content=jmsg)
