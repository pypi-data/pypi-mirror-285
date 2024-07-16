# Collection of bash scripts
```bash

### Install in USAGE mode.
    pip install utilmy
    which python

    #### Print the path:  PATH_BASHMY
        mybashdirtmp=$(python -c 'import utilmy;s=str(utilmy).split("__init")[0].split("from ")[1][1:];print(s+"tools/bash_my/mybash" ) ')
        echo $mybashdirtmp ### copy this below


    #### Add this to your ~/.zhrc or ~/.bashrc
        export mybashdir=PATH_BASHMY_COPY_PASTE_above
        export PATH="$mybashdir:$PATH"
        chmod -R 777 $mybashdir                    ### exec
        source "$mybashdir/__init/init_all.sh"       ##### Init all the alias


#### Install in DEV mode.
    1) Copy the folder mybash/ where you want
        git clone https://github.com/arita37/myutil.git
        cd myutil
        git checkout devtorch
        echo $pwd  ### copy this below


    2) in your bashrc or zshrc,  add those lines
        export mybashdir=YOURFOLDER/myutil/utilmy/tools/mybash/mybash/
        export PATH="$mybashdir:$PATH"
        chmod -R 777 $mybashdir                    ### exec
        source $mybashdir/__init/init_all.sh       ##### Init all the alias






#### Example
    #### Top file folder for cleanup
     folder size        ./             #### Print folder size in Gb
     folder topfile     ./    20       #### Print 20 biggest size files
     folder recentifle  ./    10       #### Print recently modified files   


     ### Backup easily
        bbackup all "*.txt" backup_all_files.tar.gz

        bbackup recentfile ~/Documents/ recent_backup.tar.gz -10         # past 10 days

        bbackup smallfile ~/Documents/ small_backup.tar.gz -10 1M       ### past 10 days

        bbackup dotfile ~/ dotfiles_backup.tar.gz 

        bbackup folderonly ~/ ~/zbackup/folder_structure 2   ## Depth





  4) you can debug bash script online here
     https://www.onlinegdb.com/online_bash_shell



```



## Template of all scripts
```bash
#!/bin/bash
USAGE=$(cat <<-END

         SOME USAGE DOCS

     

END
)

#### Global Config. #################################
# set -x  # Output commands being run.
set -e  # Exit on error.


#### Global vars ###################################
FUNAME=`basename "$0"`
YMD=$(date '+%Y%m%d')
THIS_FILE_PATH=$(dirname "$0")


### Input Params and Defaults ##################################
[ $# -eq 0 ] &&    echo -e "$USAGE" && exit       ###  No input print doc
task=$1    &&  [ -z $1 ] && task="size"           ###  print folder size
ppath=$2   &&  [ -z $2 ] && ppath="$PWD"          ###  current path as default



### Core ###########################################
if [[ "$task" = taskXXXx ]]; then

       ### DO SOMTHING







exit 0
elif [[ "$task" = taskYYY ]]; then


       ### DO SOMETHING



exit 0
elif [[ "$task" =  taskZZZZ ]]; then


       ### DO SOMETHING






exit 0
else
   echo -e $USAGE
fi





```



## TODO
```bash 


1) make mybash/folder script bug free and add new tasks






```



#### Helpers
```bash


https://github.com/maxwell-bland/copilot-in-the-terminal




cconfig="$1"
if [[ -z $1 ]]; then 
   cconfig="config/prd/config_prd_real.yaml"
fi 






grepall () {
grep -r "$1" .
}


countlines () {
wc -l "$1"
}


countwords () {
wc -w "$1"
}


countcharacters () {
wc -c "$1"
}


modified24hrs () {
find . -mtime 0
}


replaceall () {
grep -rl "$1" . | xargs sed -i "s/$1/$2/g"
}


largerthan100mb () {
find . -type f -size +100M
}


```