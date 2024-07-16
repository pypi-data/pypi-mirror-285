#!/bin/bash

###  scripts/local/run_zpytest.sh

source "scripts/bins/utils.sh"
source "scripts/bins/env.sh"

########## LOGS ################################################
export LOGDIR="ztmp/pytest/"
mkdir -p $LOGDIR
export LOGFILE="${LOGDIR}/log_pytest.py"


########## LOGS ################################################
logmode="$2"
if [[ -z $2 ]]; then 
   logmode="base"
fi 

source "scripts/bins/log.sh" $logmode




###################################################################################
echo  -e "###Start\n" 2>&1 | tee  "${LOGFILE}"


  pytest  -vv      --showlocals  --html=ztmp/pytest/pytest_report.html --self-contained-html  tests/

  # pytest  -vv      --showlocals  --html=ztmp/pytest/pytest_report.html --self-contained-html  tests/test_app.py


echo -e $LINE_END  2>&1 | tee  -a "${LOGFILE}"
