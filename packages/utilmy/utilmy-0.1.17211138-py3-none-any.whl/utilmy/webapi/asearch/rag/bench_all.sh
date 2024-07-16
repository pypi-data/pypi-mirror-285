#!/bin/bash
export PYTHONPATH="$(pwd)"

echo "PYTHONPATH: $PYTHONPATH"

# set default values
dirquery="ztmp/bench/ag_news/kg_questions/common_test_questions_all.parquet"
topk=5

# generate help message

usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  --dirquery <dirquery>  directory for query file"
  echo "  --topk <topk>  number of results to be considered"
  echo "  --help  show this message and exit"
}
# process command line arguments if any

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --dirquery) dirquery="$2"; shift ;;
    --topk) topk="$2"; shift ;;
    --help) usage; exit 0 ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

echo dirquery: "$dirquery"
echo topk: "$topk"


shopt -s expand_aliases
#source ~/.bash_aliases

alias pybench="python rag/bench.py "
alias pykg="python rag/engine_kg.py "



echo "# All benchmarks - `date -I`" >> rag/zlogs.md
echo "\`\`\`" >> rag/zlogs.md

echo "## dense run" >> rag/zlogs.md
pybench bench_v1_dense_run --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:'>> rag/zlogs.md
echo -e "\n\n" >> rag/zlogs.md

echo "## sparse run" >> rag/zlogs.md
pybench bench_v1_sparse_run --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:'>> rag/zlogs.md
echo -e "\n\n" >> rag/zlogs.md

echo "## tantivy run" >> rag/zlogs.md
pybench bench_v1_tantivy_run --dirquery "$dirquery" --topk "$topk" >> rag/zlogs.md
echo -e "\n\n" >> rag/zlogs.md


echo "## neo4j run" >> rag/zlogs.md
pybench bench_v1_neo4j_run --dirquery "$dirquery" --topk "$topk" >> rag/zlogs.md
echo -e "\n\n" >> rag/zlogs.md

echo "## sparse+ neo4j run" >> rag/zlogs.md
pybench bench_v1_fusion_run --engine "sparse_neo4j" --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:' >> rag/zlogs.md
echo -e "\n\n" >> rag/zlogs.md

echo "## dense+ neo4j run" >> rag/zlogs.md
pybench bench_v1_fusion_run --engine "dense_neo4j" --dirquery "$dirquery" --topk "$topk" | grep -v 'HTTP Request:' >> rag/zlogs.md
echo -e "\n\n" >> rag/zlogs.md

echo "## tantivy+ neo4j run" >> rag/zlogs.md
pybench bench_v1_fusion_run --engine "tantivy_neo4j" --dirquery "$dirquery" --topk "$topk"  >> rag/zlogs.md
echo -e "\n\n" >> rag/zlogs.md

# generate text from metrics
pybench report_create_textsample --dirquery "$dirquery"
echo "\`\`\`" >> rag/zlogs.md
