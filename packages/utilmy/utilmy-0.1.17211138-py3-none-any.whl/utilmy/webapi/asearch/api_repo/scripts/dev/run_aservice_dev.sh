#!/bin/bash

########## SCRIPT #################################################
source "scripts/bins/utils.sh"
source "scripts/bins/env.sh"
source "scripts/bins/prod.sh"



########## LOGS ###################################################
logmode="$2"
if [[ -z $2 ]]; then 
   logmode="log_base"
fi 

# export log_verbosity=3
# export log_type="base"
# export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
# export log_type="logging"
# export log_config="log_level:DEBUG"

source "scripts/bins/log.sh" $logmode




########## CONFIG ##################################################
cconfig="$1"
if [[ -z $1 ]]; then 
   cconfig="config/dev/config_dev.yaml"
fi 




########### MAIN ##################################################
echo  -e "\n ###Start service \n  $cconfig" 

export config_fastapi="$cconfig"  ### required
python src/app.py run  










