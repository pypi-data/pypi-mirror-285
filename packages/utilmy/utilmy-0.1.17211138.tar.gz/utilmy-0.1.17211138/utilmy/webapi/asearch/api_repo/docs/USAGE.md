
## Usage

```

------------------------------------------------------------------------------
#### Docker Run          ##############################
    Pre-built docker (using Github Action):

    export dname="mldock:app_20240324_efbe4af"
    export script="scripts/dev/run_aservice_dev.sh"

    docker pull $dname

    ### Start the service on port 7919
    docker run -it -p 7919:7919  $dname  $script  "config/dev/config_dev.yaml"  "logging_info"

    ### config_dev.yaml setups the port to be 7919

   ### Open another terminal shell on the host
       cd repo
       scripts/local/test_client.sh 


   ###  In Browser, Doc available at http://localhost:7919/v1/docs


   Notes: Docker does not contain pytest,  pip_test.txt packages
          (to make it slimmer). 





------------------------------------------------------------------------------
### Build by CI/CD Github Actions  ###################################
        OS Level docker
              .github/worklows/docker_build_base/yaml 

              config/common/docker/docker_base.dockerfile



        App level docker (re-using OS level docker)
              .github/worklows/docker_build_app.yaml  

              config/common/docker/docker_app.dockerfile
        






------------------------------------------------------------------------------
### Local machine  ####################
### Install  
   Install Python 3.9 or higher with miniconda
   Check dockerfile: config/common/docker/docker_base.dockerfile
      

   cd repofolder   
   pip install -r config/common/pip/pip_app.txt 
   pip install -r config/common/pip/pip_test.txt 

   ## Tesseract install steps in
      config/common/docker/docker_base.dockerfile

   ## Check binary : which tesseract


### ENVS and PYTHONPATH 
   cd repofolder
   chmod -R 777 scripts/
   source scripts/bins/env.sh



#### Run Server in Local 

   ### Using pre-defined scripts
   scripts/dev/run_aservice_dev.sh   "config/dev/config_dev.yaml"  "logging_info"

   ## In Browser, Doc available at http://localhost:7919/docs


   ### Launch manually by python  requires ENV variable to be setup
      export config_fastapi="config/dev/config_dev.yaml"  
      source scripts/bins/env.sh

      python src/app.py run  







------------------------------------------------------------------------------
#### Client side check         #########################################
   ### (using other terminal)
   scripts/local/test_client.sh 



#### Client side : Basic Stress Tests   ###############################
     ### (using other terminal)

     source scripts/bins/env.sh
     export config_fastapi="config/dev/config_dev.yaml"  

     python tests/regressions/client.py  check1 

     python tests/regressions/client.py  check2 --nmax 5  --nclient 3

     python tests/regressions/client.py  check3 --nmax 5  --nclient 3




------------------------------------------------------------------------------
#### Running tests  ####################################

#### CI/CD  Github Actions at each commit   
    .github/worklows/
        app_run_pytest.yaml    : Linting, code check, pytest runs



#### Pytest Local 
    scripts/local/run_zpytest.sh

    pytest  -vv  --showlocals  --html=data/pytest_report.html --self-contained-html  tests/
          





------------------------------------------------------------------------------
#### Code/Check Formatting  ##################################
    isort --atomic src/
    black --line-length=100 --target-version=py39  src/

    isort --atomic tests/
    black --line-length=100 --target-version=py39  tests/


#### Code check      ####################################
    ruff check  src/ 





