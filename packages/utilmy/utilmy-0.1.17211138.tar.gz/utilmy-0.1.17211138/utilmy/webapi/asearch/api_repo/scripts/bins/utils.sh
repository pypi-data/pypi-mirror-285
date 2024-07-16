#!/bin/bash

LINE_SEP="##############################################################################"
LINE_SEP2="######################################################"
LINE_SEP3="###########################"
LINE_END="\n\n\n#######################################################################"


function echo2 () {   
  if [[  $2 == ''  ]]; then
    echo -e $1  2>&1 | tee -a "${LOGFILE}"

  else :  ### Not append
    echo -e $1  2>&1 | tee   "${LOGFILE}"
  fi;

}


function echo3 () {   
  echo -e  $LINE_END  2>&1 | tee -a "${LOGFILE}"
  if [[  $2 == ''  ]]; then
    echo -e $1  2>&1 | tee -a "${LOGFILE}"

  else :  ### Not append
    echo -e $1  2>&1 | tee   "${LOGFILE}"
  fi;

}



function list_error() {
   ### Find Error msg in log file
   ## list_error ztmp/log//_log1.py    
   echo -e  "\n\n$LINE_END"  
   echo -e  "###### List of err-ors: ############" 
   echo -e  $1
   grep -Ehnr "error|Error" "$1"  | grep -ve "from_error"
   #grep -Ehnr "error|Error" "$1"  

}


function list_warning() {
   ### Find Error msg in log file
   ## list_error ztmp/log//_log1.py    
   echo -e  "\n\n$LINE_END"  
   echo -e  "###### List of warni-nings: ############" 
   echo -e  $1
   grep -Ehnr "warning|Warning" "$1"  | grep -ve "from_error"
   #grep -Ehnr "error|Error" "$1"  

}



function path_abs() {
  # $1 : relative filename
  if [ -d "$(dirname "$1")" ]; then
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
  fi
}


function git_push_bot() {
    git config user.name github-actions[bot]
    git config user.email 41898282+github-actions[bot]@users.noreply.github.com
    git add --all &&  git commit -m "${1}" 
    git pull --all     
    git push --all -f  
}



function timeout2() {
    # First argument: PID
    # Second argument: Timeout
    # Get process start time (Field 22) to check for PID recycling
    start_time="$(cut -d ' ' -f 22 /proc/$1/stat)"

    sleep "$2"

    # Make sure that PID was not reused by another process
    # that started at a later time
    if [ "$(cut -d ' ' -f 22 /proc/$1/stat)" = "$start_time" ]; then
        # Kill process with SIGTERM
        kill -9 "$1"
    fi
}


function kill_sub_process() {
    local pid="$1"
    local and_self="${2:-false}"
    if children="$(pgrep -P "$pid")"; then
        for child in $children; do
            kill_sub_process "$child" true
        done
    fi
    if [[ "$and_self" == true ]]; then
        kill -9 "$pid"
    fi
}




export_allenv() {
  # Export all environment variables to a file in a format that can be sourced
  # export_allenv "env2.txt"
  while IFS='=' read -r name value; do

      if [[ $string1 == *"image_tag"* ]]; then
         printf 'export %s="%q"\n' "$name" "${value}"
      else
        echo ""
      fi

      printf 'export %s="%q"\n' "$name" "${value}"
  done < <(printenv) > $1
}



function str_exists_infile {
    ### exist_str "error"  myfile.py 
    if grep -iq "$1" $2; then
        echo "$1 exists !"
        return 1
    else
        echo "$1 not exists !"
        return 0
    fi
}



function print_envars(){ 
  python -c "import os, pprint; pprint.pprint(dict(os.environ))"  
}


echo "bin/utils.sh loaded"



