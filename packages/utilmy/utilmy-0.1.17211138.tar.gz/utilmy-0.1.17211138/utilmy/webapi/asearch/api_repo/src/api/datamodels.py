# -*- coding: utf-8 -*-
from pydantic import BaseModel

apiSUCCESS = "success"
apiFAILURE = "failure"


#####################################################################
#### Entry points      ##############################################
class apiEntryURI_v1:
    #### Manage versionning of URI using specific dataclass name : flexibility
    imgsync = "/v1/imgsync"
    imgasync = "/v1/imgasync"
    imgasyncget = "/v1/imgasyncget". ## not good alias URI in API Design



#### imgsync Data Scheme ############################################
class imgsyncRequest(BaseModel):
    data: str
    lang: str = None
    token: str = None


class imgsyncOutput(BaseModel):
    text: str
    ts: float  ### unix timestamp
    version: str = ""
    status: str = ""


#### imgasync Data Scheme #########################################
class imgasyncRequest(BaseModel):
    data: str
    lang: str = None
    token: str = None


class imgasyncOutput(BaseModel):
    jobid: str
    ts: float  ### unix timestamp
    version: str = ""
    status: str = ""


#### imgasyncget Data Scheme ####################################
class imgasyncGetRequest(BaseModel):
    jobid: str
    token: str = None
    version: str = ""
    status: str = ""


class imgasyncGetOutput(BaseModel):
    jobid: str
    text: str
    status: str
    ts: float  ### unix timestamp
    version: str = ""
