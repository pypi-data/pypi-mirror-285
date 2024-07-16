```python

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
    ls  ./ztmp/

    ### Benchmark Folder 
        mkdir -p ./ztmp/bench/ag_news

        #### KG output   
           mkdir -p ./ztmp/bench/kg/model/
           mkdir -p ./ztmp/bench/kg/result/


    ### Training Expriment Folder:   in YYYYMMDD/HHMM format
        for model fine-tuning (rebel,... )
        mkdir -p ./ztmp/exp/202040512/150014/


    ### Data Folder with git LFS (large file) : ./ztmp/data/
        cd ./ztmp
        git clone https://github.com/arita37/data2.git
        cd data && git checkout text && cd .. 
        ls data/.


        #### Need to instal git Large Ffile
            brew install git-lfs
            sudo apt-get install git-lfs

            cd ./ztmp/data/
            git lfs install            
            # git lfs track "*.parquet"
            # git lfs track "*.csv"
            # git lfs track "*.zip"
            # git lfs track "*.json"
            # git lfs track "*.gz"

    #### Folder structure
    cats/ 
       ag_news/ : News Dataset
           train/df.parquet :   "text", "label"
           test/df.parquet  :    "text", "label"

       arxiv/
           raw/ :    raw file from itnernet
           train/ :  train split normalized
           val/:     val split normalized
           meta/meta.json:   Dict with encoding mapping for Label,s...

        "text_id": 
        "text" : str
        "labels":   "," separated labels







#########################################################################
#### Data  Global Schema, Naming  #######################################

  1 document --> Collection of chunk text_id, ordered by text_rank,
  Document doc_id --> chunking in text_id --> process per chunk. 

    Big Article  --> doc_id
         chunk into  text_id1, text_id2, text_id3

         Just consider 1 news article as 1 text_id  (dont worry about doc_id)

         text_id : Smallest unit of text/sentence.

    in Neo4j ---> (doc_id or ID)

       We only take care of text_id which is USER provided.
       Use "text_id" as name for ID column.




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







##### Dataset Merged Schema  ###########################################
mkdir -p ./ztmp/hf_data/


SCHEMA_GLOBAL_v1 = [
    ("dataset_id",  "str",   "URL of the dataset"),
    ("dataset_cat", "str",   "Category tags : cat1/cat2, english/news/"),

    ("doc_id",   "str",  "Document where text is extracted, doc_id = text_id, if full text"),
    ("doc_cat",  "str",  "Document types:  cat1/cat2/cat3"),

    ("text_id",  "int64", "global unique ID for the text"),
    ("text_id2", "int64", "text_id from original dataset"),
    ("dt", "float64", "Unix timestamps"),

    ("title",   "str",    " Title "),
    ("summary", "str",    " Summary "),
    ("text",    "str",    " Core text "),
    ("info_json", "str",  " Extra info in JSON string format "),


    ("cat1", "str", " Category 1 or label "),
    ("cat2", "str", " Category 2 or label "),
    ("cat3", "str", " Category 3 or label "),
    ("cat4", "str", " Category 4 or label "),
    ("cat5", "str", " Category 5 or label "),


    ("ner_list", "list", " List of triplets (str_idx_start, str_idx_end, ner_tag) "),

]






```

