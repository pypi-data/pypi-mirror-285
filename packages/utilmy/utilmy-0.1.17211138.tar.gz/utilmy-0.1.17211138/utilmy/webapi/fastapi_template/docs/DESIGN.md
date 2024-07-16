
### Requirements comments : 
```

  No specs on max image width, height or byte size.
  No specs on traffic volume.
  No specs on imgeasync_get endpoint.
  No specs on backend storage : persistency.


```



### Repo features : 
```

API patterns : 
    Input Post  with DataClass
    Output Post with DataClass
    Authentification
    Input params validation
    Versioning of API Entry
    Middleware for origin filtering.

    Running scripts are included in the repo:  LOCAL,  DEV,  PRD

    API versionning:  
      Basic versionning pattern is used, using DataClass 
         (or router pattern or Sub-API pattern can be used).


Robustness:
   3rd party Storage : storage maxsize, TTL to prevent overflow.
   Storage client start/stop is dynmically managed by FastAPI. 
   Backgroung procesing task : Timelimit (done at task level), BUT not at queue level.
   Image size filtering.

Code: 
  Modular and composable structure
  Re-usable code (utils/)
  Docstring
  Type Hints
  Dataclass for in/out.


Deployment:
  Separate configuration folder for local, dev, std and prd : Prevent deployment issues.
  Separate scripts folder for local, dev, std and prd :       Prevent deployment issues.
  logging level configurable dynamically at deployment time (ie docker/kubernetes entry point).  
  App Docker can be investigated after launch: /bin/bash entrypoint.
  Separate OS level docker and app level docker to reduce deployment issues.


Logging:
   Config at global level : can include logging stream on 3rd party.
   logging is on stdout (logging): Not stored.


Server  Management :
   Dual dockerfile pattern  : Separate OS level and app level.
   Bash Entry Script to start.
   Global config :  only loaded once (cannot re-load after Server start).


Computation: 
   Separate engine computation :  Modular pattern
   Basic OCR compute with tessaract.
   Basic sentiment engine with huggingface in  engine/nlp/



Stress tests:
    Basic client for multi-thread stress testing of server:
       tests/regressions/client.py

```


### Repo structure
```
    config/ :  various configs + DockerFiles
      common/docker/ :  dockerfiles
      commont/pip    :  pip requirements
      prd/ : Prod configuration
      stg/ : STG  configuration
      dev/:  DEV  configuration
      local:  local and pytest configuration
  

    scripts/ :  Scripts
       local/ :   all scripts to run in local : pytest, linter, ...
       dev/   :   all scripts to run in DEV environnment.
       stg/   :   all scripts to run in STG environnment.
       prd/   :   all scripts to run in PRD environnment.


    src  :   main source
      app.py :  Server entrypoint
          Basic version management.
          Middleware interface.


      api/ :  API entry components
         authenticate.py : Template for authentification
         datamodels:       API dataclass In/Out
         errormodels:      Error model pattern.
         middleware.py :   Middleware for Inbound filtering
         validation.py :   Parameters validation


      engine/  : Specific compute
          ocr/ :  OCR engine
              tessaract/process.py  :  Code for tessaract engine.

          nlp/ :  NLP engine
              sentiment.py :  Code for sentiment analysis engine.  


      utils/   :  Utilities
        util_log.py    : Global logger, configurable at ENV variable
        util_config.py : Universal config loader (any config file)
        uti_image.py   : Image processing
        util_storage   : State management of Jobid, descrription.
        util_base.py   : Various utilities.

  
    testdata/ :  Some mock data
  
    tests/ :     main tests, structure follow sr/c/
  

```



#### Code 
```
   Formatted with Black, Isort.
   100 chars per line.
   Linting with Ruff
  
   black --line-length=100 --target-version=py39  src/
       All done! ✨ 🍰 ✨
       20 files left unchan


```





#### Design Choice
```

### API Versioning

   In FastAPI 3 main possibilities:
       Add prefix and using APIRouter()
           Common router part
   
       Use sub FastAPI() object and assign to main FastPI():
           Doc generation is cleaner.

       Custom solutions:


       We choose custom solution using dataclass naming model:
           - Flexibility
           - No overload of extra-object: like APIRouter() or sub fastAPI()
           - Minimal cost to update.
           - Easy to understand the pattern (ie datamodels)
           

### BackGroundTask

    We use FastAPI default backgroundtask queue object and time limit on teessaract
    to prevent overflow:
        - Most simple implementation in FastAPI
        - No, time limit at queue object, no much control on the queue overflow.

    More robust task queue is preferable  as TODO.     






```
