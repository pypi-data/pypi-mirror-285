# -*- coding: utf-8 -*-
import os
import traceback

import fire
import uvicorn
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI

from src.api.authenticate import api_authenticate
from src.api.datamodels import (
    apiEntryURI_v1,
    apiSUCCESS,
    imgasyncGetOutput,
    imgasyncGetRequest,
    imgasyncOutput,
    imgasyncRequest,
    imgsyncOutput,
    imgsyncRequest,
)
from src.api.errormodels import exception_handler
from src.api.middleware import api_middleware
from src.api.process import api_imgasync_process, api_imgasyncget_process, api_imgsync_process
from src.api.validation import (
    api_imgasync_valid_params,
    api_imgasyncget_valid_params,
    api_imgsync_valid_params,
)
from src.utils.util_config import config_load
from src.utils.util_log import log, log_error
from src.utils.util_storage import Storage, storage_init

######################################################################################
######## Global API Class ############################################################
global app, cfg

app = FastAPI()
api_middleware(app)


###### Entrypoints version ###################
## Manage directly at datamodels.py level
##    apiEntryURI_v1


### Global config   #########################
def config_load_global():
    log("Global config loading......")
    cfgtmp = config_load(os.environ["config_fastapi"])
    log("Global config loaded Once")
    return cfgtmp


### Load only once at Start
cfg = config_load_global()


### Global storage  ########################
def storage_get():
    db = storage_init(cfg)
    try:
        yield db
    finally:
        db.close()


######################################################################################
######## API Entry ###################################################################
@app.post(apiEntryURI_v1.imgsync, response_model=imgsyncOutput)
def api_imgsync(
    request: imgsyncRequest,
):
    """Synchronous endpoint for image processing.
    Args:
        imgsyncRequest
            - image: str - image data to be synced, base64-encoded image
            - lang: str - optional language parameter
            - token: str - optional authentication token


    Returns:
    - dict: JSON response containing text extracted from image.

    Comments : 
         + Processing time: client cancel the request... ,  assume procesing below < 1sec : guarantee.
         
         API_thenatciate --> at the API gateway
               we dont need again the api_authenticate.
               Depends on the Endpoint requireemnts security : JWT token

    Params valid : per endpoint specific code ?
       In validation --> throws an error :  throw 400 HTTP  image is invalid

       If something happens in the process ---> Throws 500.

    How do you manage the parameters in the global config file ?
         Unit testing, I dont global variable in the function.

    Load the config, anywhere --> Config is immutable.
    when you wrtie function, it depends on some XXX global. extra dependencies defied Outside of the function.

       Middleware Implicit --> can create edge cases easily.
       Pros/Cons

      Re-usable template code for the endpoint.
        I can copy/paste  and 99%  only 2% of the parts.

    2) API versionning.
       just managed some dataclass/alias naming :  found simple and easy to check.

       In FastAPI : (standard way) : 
          Concept of router :  define URI in router, each router has one version....


   In the endpoint NAMING for client, you suggest this:
        POST /v1/imagesync          --> create job
        GET /v1/imagesync/{job_id}  --> retrieve job


   In the backend server code:             python side : unique name for each processing endpoint.
        POST /v1/imageasync          -->  imageasyncInput, imageasyncOutput, .... 

        GET /v1/imageasync/{jobid}   -->  imageasyncGetInput, imageasyncGetOutput, .... 

    For me (in my head): 
       different Input/Ouput format. ---> we need to have different path_names.
                                           thats why , I added get suffix (but not standard)

   In the response JSON, dod you add the API version ?
     header: 200 HTTP status : this HTTP request 

     body:   {

          "version":    # No, already specify inthe API,
          "status": for this jobid processing    # is ok or not.

        }

   GET --> synchronous processing since fetching ressources.

   POST --> a-synchrnous since CPU process something (timeout on client side)


   2) when you have task processing.....
        manage the queue inside the API server : NO ?
             Send to the input queue the job description and jobid


     src/api/v1/process.py
                     ...


     src/api/v2/process.py


     from src.api.v1...



    """
    try:
        global cfg
        lang, token = request.lang, request.token
        image_str: str = request.data

        ### Add in the middleware (per basis, )
        api_authenticate(cfg=cfg, token=token, name=apiEntryURI_v1.imgsync)
        api_imgsync_valid_params(cfg=cfg, image_str=image_str,lang=lang,)

        json_val = api_imgsync_process(cfg=cfg, image_str=image_str, lang=lang)

        # json_val.version = apiEntryURI_v1.imgsync
        json_val.status = apiSUCCESS
        return json_val

    except HTTPException as e:
        ### Internal logging: log_trace will manage to Log or NOT.  export log_verbose_level="trace"
        log_trace(traceback.format_exc())  
        
        ### HTTP error msg for client/customer.
        return http_exception_handler(e, msg= f"Error in api_imgsync")

    except Exception as e:
        log_trace(traceback.format_exc())  

        ### HTTP error msg for client/customer.
        return exception_handler(msg= f"Error in api_imgsync: {e}")



@app.post(apiEntryURI_v1.imgasync, response_model=imgasyncOutput)
async def api_imgasync(
    request: imgasyncRequest,
    background_tasks: BackgroundTasks,
    storage: Storage = Depends(storage_get),
):
    """Asynchronous endpoint for image processing.
    Args:
        imgasyncRequest
            - image (str): image data to be processed.
            - lang (str, optional): language for processing image data. Defaults to None.
            - token (str, optional): authentication token. Defaults to None.

    Returns:
        dict: JSON response containing running jobid.
    """
    try:
        global cfg
        lang, token = request.lang, request.token
        image_str: str = request.data

        api_authenticate(cfg=cfg, token=token, name=apiEntryURI_v1.imgasync)
        api_imgasync_valid_params(
            cfg=cfg,
            image_str=image_str,
            lang=lang,
        )

        json_val = api_imgasync_process(
            cfg=cfg,
            image_str=image_str,
            background_tasks=background_tasks,
            lang=lang,
            storage=storage,
        )

        json_val.version = apiEntryURI_v1.imgasync
        json_val.status = apiSUCCESS
        return json_val

    except Exception as e:
        trace = traceback.format_exc()
        log_error(trace)  ### internal only
        msg = f"Error in api_imgasync: {e}"
        return exception_handler(msg)


@app.post(apiEntryURI_v1.imgasyncget, response_model=imgasyncGetOutput)
def api_imgasyncget(request: imgasyncGetRequest, storage: Storage = Depends(storage_get)):
    """Retrieves an image text based on provided job ID and token.
    Args:
        imgasyncGetRequest
            - jobid (str): ID of job
            - token (str, optional): authentication token. Defaults to None.

    Returns:
        dict: JSON response containing text extracted from image.
    """
    try:
        global cfg
        jobid, token = request.jobid, request.token
        api_authenticate(cfg=cfg, token=token, name=apiEntryURI_v1.imgasyncget)
        api_imgasyncget_valid_params(
            cfg=cfg,
            jobid=jobid,
        )

        json_val = api_imgasyncget_process(jobid=jobid, storage=storage)

        json_val.version = apiEntryURI_v1.imgasyncget
        json_val.status = apiSUCCESS
        return json_val

    except Exception as e:
        trace = traceback.format_exc()
        log_error(trace)  ### internal only
        msg = f"Error in api_imgasyncget: {e}"
        return exception_handler(msg)


######################################################################################
######## API runtime #################################################################
def run():
    """Run application server.

          export config_fastapi="config/dev/config_dev.yaml"
          python src/app.py  run

    Returns:
        None

    TODO: Create nested dataclass for config validation or use python-box
    """
    global cfg, app
    cfgs = cfg["service"]

    host = str(cfgs.get("host", "0.0.0.0"))
    port = int(cfgs.get("port", 7919))
    debug = bool(cfgs.get("debug", True))
    workers = int(cfgs.get("workers", 1))
    doreload = int(cfgs.get("reload", True))

    log("API Service Started"). 
    ## 1) Uvicorn : Async HTTP handler. on top ---> Sync HTTP server
    ### Issue of Long running 5mins to run  ---> need to use Sync
    ##     2) ---> FastAPI (application layer). : app Object : does all the entrypoint
    uvicorn.run("app:app", host=host, port=port, reload=doreload, debug=debug, workers=workers)


####################################################################################
if __name__ == "__main__":
    fire.Fire()





"""
import sys

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from config import Config


CONFIG = None

@app.on_event("startup")
@repeat_every(seconds=5)
def reload_config():
    global CONFIG
    CONFIG_FILE_PATH = "/path/to/file"
    print("Reloading the config from {}".format(CONFIG_FILE_PATH))

    try:
        CONFIG = Config.from_json(open(CONFIG_FILE_PATH, "r").read())
    except:
        print("Error loading configuration file.")

    if CONFIG is None: # CONFIG is declared as None before first successful assignment
        sys.exit('No configuration, exiting application.')

"""