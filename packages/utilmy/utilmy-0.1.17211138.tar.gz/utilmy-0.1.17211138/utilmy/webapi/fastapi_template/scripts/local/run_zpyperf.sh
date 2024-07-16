#!/bin/bash

source "scripts/bins/utils.sh"
source "scripts/bins/env.sh"
source "scripts/bins/prod.sh"




########## LOGS ########################################################
logmode="$2"
if [[ -z $2 ]]; then 
   logmode="base"
fi 
source "scripts/bins/log.sh" $logmode




cconfig="$1"
if [[ -z $1 ]]; then 
   cconfig="config/dev/config_dev.yaml"
fi 




########## START ######################################################
echo  -e "###Start\n" 

pyinstrument    --no-color src/app.py run  --config $cconfig  



