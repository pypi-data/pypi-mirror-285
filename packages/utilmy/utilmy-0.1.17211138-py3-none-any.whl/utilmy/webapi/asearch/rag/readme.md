

```bash

##########################################################################
#### Install #############################################################
  git clone https://gihub.com/arita37/myutil.git 
  cd myutil && git checkout devtorch
  cd utilmy/webapi/asearch
  export PYTHONPATH=$(pwd)





##########################################################################
#### Data path   #########################################################

    #### All data are stored here:  webapi/asearch/ztmp  (under gitignore, never committed)
    cd websapi/asearch/
    mkdir -p ztmp      
    ls  .ztmp/

    ### Benchmark Folder 
        mkdir -p ./ztmp/bench/ag_news

        #### KG output   
           mkdir -p ./ztmp/bench/kg/model/
           mkdir -p ./ztmp/bench/kg/result/


    ### Training Expriment Folder:   in YYYYMMDD/HHMM format
        mkdir -p ./ztmp/exp/202040512/150014/


    ### Data Folder 
        cd ./ztmp
        git clone https://github.com/arita37/data2.git
        cd data && git checkout text && cd .. 
        ls data/.


        #### Need to instal git Large Ffile
            brew install git-lfs
            sudo apt-get install git-lfs

            cd ./ztmp/data/ && 
            git lfs install
            
            # git lfs track "*.parquet"
            # git lfs track "*.csv"
            # git lfs track "*.zip"
            # git lfs track "*.json"
            # git lfs track "*.gz"




##################################################################################
 #### Used Data Format: 
        question --> Human-like question,            query --> for LLM, other DB system
   RAG is done at the "text_id" level : smallest chunk of text.
       we do Sqlite query to fetch text_id --> parent doc_id (if needed during re-rank, extra context, )



   KG: 
       triplet storage :  df[["doc_id", "head", "type", "tail"]] 
       question storage : df[["doc_id", "head", "type", "tail", "question"]


   qdrant, Tantivy: 
        question storage : df[[,id,body,queries  ]  --->  [[ "text_id", "text", "question"  ]]




   ------------------------------------------------------------
   Refactor name in python code + parquet files
       "doc_id"  --->   "text_id"
       "body"    --->   "text"
       "queries" -->    "question"

      In database (neo4J, Qdrant, ...):    "id" ---> "text_id"
           in python client, --> rename in pytho code  "id"  --> "text_id"


    from utilmy import glob_glob
    flist = glob_glob("./ztmp/**/.parquet")
    for fi in flist : 
       dfi = pd_read_file(fi)

       colsnew = [] 
       for coli in dfi.columns: 
           col2 = coli
           if coli== "doc_id" : col2= "text_id"



           colsnew.append(col2)
       dfi.columns = colsnew


   2) TODO :

       0) Run benchmark using SAME questions than KG questions : (qdrant, sparse and dense) 

       1) more triplets using Colab

       2) Re-phrase the initial question : using LLM --> more related keywords for KG, qdrant search
            def query_rephrase_question(txt)
               #### Use Prompt 

               return questions_list


       3) Fusion Search : run the search engine in Parallel using await (parallism)
            To Check.


       4) Merge Fusion :  Sparse and KG (ie most proning) : not correlated results --> better result.
                                

       5) Engine retrieval XYZ new one :  integrate using SAME data format  --> run same bench/.
               Normalized data schema, flow : easier integration.
               GraphRAG 
               engine_graphrag.py --->

           ---> Meta-RAG systems : add new RAG by engine_XXX.py   Generic design, 







#########################################################################
#### Data  Global Schema, Naming  #######################################

  1 document --> Collection of text_id, ordered by text_rank,


  Document --> chunking in text_id --> process per chunk. 


  ### docs_structure
      doc_id:   Unique hash int document  =  HASH(document_content)   
      text_id : Unique hash int for text  =  HASH(text_content)
      text_rank : Ordering position of the "text_id" inside the document 0, 1, 3,
      text_tags  :  category tags of the text inside the DOCUMENT: "ttile", "end", ..
                    tags is relative to the DOCUMENT

      model_chunk_id :  str: ID of the model used for chunking.
      text :    block of text


  ## docs_master table
      doc_id
      url : "origin url"
      cat1,  : string separated category tags
      cat2,  : string separated category tags
      cat3,
      ...
      dtc: creation
      dtu: updated


  ## text_master  table
        text_id   : Unique Hash 
        text      : Actual text


  ##  text_class :   text classification results  tbale
      text_id
      model_id
      dt
      cat1, 
      cat2,
      cat3,


  ##  text_ner :    text NER results table
      model_id
      dt
      text_id
      ner_list1:  [("start", "end", "class", "value"), ..... 









#########################################################################
####  code naming pattern  ##############################################


 --> do not use "id"  --> "text_id" 
     for RAG : use "text_id"


```






### Script Command
```bash

   zscripts.md

```



