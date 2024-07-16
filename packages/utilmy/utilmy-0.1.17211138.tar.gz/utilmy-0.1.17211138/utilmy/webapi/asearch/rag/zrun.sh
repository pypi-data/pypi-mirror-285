#!/bin/bash
USAGE=$(
      cat <<-END

       ####  Running the benchmark
        rag/zrun.sh bench   ./ztmp/bench/ag_news     /kg_questions/common_test_questions.parquet


       #### start the qdrant, neo4j DB
        ./rag/zrun.sh start_db 


END
)




#### Global Config. #################################
# set -x  # Output commands being run.
set -e # Exit on error.å

#### Global vars ###################################
FUNAME=$(basename "$0")
YMD=$(date '+%Y%m%d')
this_file_dir="$(dirname "$0")"

#### Import utils relative path  #################################
source "$this_file_dir/zshorcuts.sh"



### Input Params and Defaults ##################################
[ $# -eq 0 ] && echo -e "$USAGE" && exit ###  No input print doc
task=$1 && [ -z $1 ] && task="size"      ###  print folder size
dir0=$2 && [ -z $2 ] && dir0="$PWD"    ###  current path as default





### Core #####################################################
if [[ "$task" = bench ]]; then
      queryfile=$3 && [ -z $3 ] && queryfile="kg_questions/common_test_questions.parquet"
      topk=$4      && [ -z $4 ] && topk=5


    echo -e "\n\n####### Benchmark Results " >> rag/zlogs.md
    echo '```bash ' 

    echo -e '\n########## sparse run' >> rag/zlogs.md 
    pybench bench_v1_sparse_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md


    echo -e '\n########## dense run' >> rag/zlogs.md 
    pybench bench_v1_dense_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md
    echo '```' >> rag/zlogs.md

    echo -e '\n########## neo4j run' >> rag/zlogs.md 
    pybench bench_v1_neo4j_run --dirquery "$dir0/kg_questions/common_test_questions.parquet" --topk 5 >> rag/zlogs.md













########################################################################
exit 0
elif [[ "$task" = start_db ]]; then
      # ssize=$3 && [ -z $3 ] && ssize=20
      ###  ./rag/zrun.sh start_db


      echo -e "\n Starting Qdrant on port 6333"
      echo  "qdrant on  http://localhost:6333/dashboard"
        # ./ztmp/bins/qdrant --config-path ./rag/qdrant_config.yaml &
         sudo docker run -d -p 6333:6333     -v  ./ztmp/db//qdrant_storage:/qdrant/storage:     qdrant/qdrant   



      echo -e "\nStarting neo4j"
      echo -e "\n neo4j UI on http://localhost:7474/browser"
          sudo /opt/neo4j/bin/neo4j start    &








exit 0
elif [[ "$task" = task3 ]]; then
      ### recent file modified files + created
      ssize=$3 && [ -z $3 ] && ssize=20







exit 0
else
      echo $USAGE
fi









