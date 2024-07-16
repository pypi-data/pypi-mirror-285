#!/bin/bash

source "scripts/bins/utils.sh"
source "scripts/bins/env.sh"
source "scripts/bins/prod.sh"

########## LOGS directory ##########################################################
#export LOGDIR="ztmp/log/"
#mkdir -p $LOGDIR
#export LOGFILE="${LOGDIR}_log.log"


########## LOGS Global setuo #######################################################
logmode="$2"
if [[ -z $2 ]]; then 
   logmode="base"
fi 


# export log_verbosity=3
# export log_type="base"
# export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"
# export log_type="logging"
# export log_config="log_level:DEBUG"
source "scripts/bins/log.sh" $logmode



###################################################################################
cconfig="$1"
if [[ -z $1 ]]; then 
   cconfig="config/prd/config_prd.yaml"
fi 


###################################################################################
export config_fastapi="$cconfig"  ### required
python src/app.py run 









