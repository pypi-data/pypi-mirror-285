

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

          nlp/ :  NLP engine

          search/


      utils/   :  Utilities
        util_log.py    : Global logger, configurable at ENV variable
        util_config.py : Universal config loader (any config file)
        uti_image.py   : Image processing
        util_storage   : State management of Jobid, descrription.
        util_base.py   : Various utilities.

  
    testdata/ :  Some mock data
  
    tests/ :     main tests, structure follow sr/c/
  

```



