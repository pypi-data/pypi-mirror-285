# -*- coding: utf-8 -*-
"""
    #### Install
        cd myutil 
        cd utilmy/webapi/asearch/
        pip install -r pip/py39_full.txt
        pip install fastembed==0.2.6 loguru --no-deps


    #### ENV variables
        export HF_TOKEN=


    ##### Usage : 
            cd utilmy/webapi/asearch/
            mkdir -p ./ztmp/hf_data/

            python data_pd.py fetchnorm_agnews       --diroot  "./ztmp/hf_data/"   
            python data_pd.py fetchnorm_big_patent   --diroot  "./ztmp/hf_data/"   


    #### Data Folder structure
       cd aseearch
       mkdir -p ztmp/hf_dataset/      ### already in gitignore, never be commited. 

      ztmp/hf_data/
             ashraq_financial_news_articles / raw / train / df_50k.parquet
             ashraq_financial_news_articles /norm / train / df_50k.parquet


            meta/ 
               ashraq_financial_news_articles.json
               agnews.json

    
    ##### Flow
        HFace Or Kaggle --> dataset in RAM--> parquet (ie same columns)  -->  parquet new columns (final)
        Example :   
             huggingface.co/datasets/valurank/News_Articles_Categorization
             {name}-{dataset_name}

              ### MetaData JSON saved here
                       ---> ztmp/hf_data/meta/valurank-News_Articles_Categorization.json"

              ### Data saved here:
                       ---> ztmp/hf_data/data/valurank-News_Articles_Categorization/train/df.parquet"
                       ---> ztmp/hf_data/data/valurank-News_Articles_Categorization/test/df.parquet"



       Target Schema is  SCHEMA_GLOBAL_v1 



    #### Dataset TODO:

        https://huggingface.co/datasets/ashraq/financial-news-articles

        https://huggingface.co/datasets/big_patent

        https://huggingface.co/datasets/cnn_dailymail


    #### Dataset Done in Google Drtice
       https://drive.google.com/drive/folders/1Ggzl--7v8xUhxr8a8zpRtgh2fI9EXxoG?usp=sharing



    ##### Infos
        https://huggingface.co/datasets/big_patent/tree/refs%2Fconvert%2Fparquet/a/partial-train

        https://zenn.dev/kun432/scraps/1356729a3608d6



    ### Tools: Annotation tool
        https://doccano.github.io/doccano/

        https://github.com/argilla-io/argilla   

        https://diffgram.readme.io/docs/conversational-annotation

        Prodigy: A scriptable annotation tool from creators of spaCy, designed for efficient, active learning-based annotation. It supports various data types including text, images, and audio 2.
        brat (Browser-Based Rapid Annotation Tool): A free, web-based tool for collaborative text annotation, supporting complex configurations and integration with external resources 2.
        tagtog: An easy-to-use, web-based text annotation tool that supports manual and automatic annotation, with features for training models and importing/exporting annotated data 2.
        LightTag: Offers a browser-based platform with AI-driven suggestions for text labeling and features for managing annotation projects and quality control 2.
        TagEditor: A desktop application that integrates with spaCy for annotating text, supporting various annotation types and data export options for model training 2.



"""
import warnings
warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback, copy, json, zipfile
from box import (Box, BoxList,  )
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
import pandas as pd, numpy as np, torch, requests

import datasets
from datasets import (DatasetDict, Dataset)


from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob,
       json_load, json_save)
from utilmy import log, log2

### local repo
from utils.util_hf import (np_str, hash_textid, hash_text_minhash, hf_ds_to_disk)

######################################################################################
#### All dataset has normalized columns : simplify training
SCHEMA_GLOBAL_v1 = [
    ("dataset_id",  "str",   "URL of dataset"),
    ("dataset_cat", "str",   "Category tags : cat1/cat2, english/news/"),

    ("doc_id",   "str",  "Document where text is extracted, doc_id = text_id, if full text"),
    ("doc_cat",  "str",  "Document types:  cat1/cat2/cat3"),

    ("text_id",  "int64", "global unique ID for text"),
    ("text_id2", "int64", "text_id from original dataset"),
    ("dt", "float64", "Unix timestamps"),

    ("title",   "str",    " Title "),
    ("summary", "str",    " Summary "),
    ("text",    "str",    " Core text "),
    ("info_json", "str",  " Extra info in JSON string format "),

    ### you can new colum if needed,.... 


    ("cat1", "str", " Category 1 or label "),
    ("cat2", "str", " Category 2 or label "),
    ("cat3", "str", " Category 3 or label "),
    ("cat4", "str", " Category 4 or label "),
    ("cat5", "str", " Category 5 or label "),


    ("ner_list", "list", """ List of triplets: 
                              format1:   (str_idx_start, str_idx_end, ner_tag, ner_type) 
                              formtat2:  {"start": str_idx_start, "end": str_idx_end, "label": ner_tag, "entity": ner_type}
                             
                             """),

]



#### JSON saved on in  dirdata_meta/
meta_json =Box({
  "name"             : "str",
  "name_unique"      : "str",
  "url"              : "str",
  "nrows"            : "int64",
  "columns"          : "list",
  "columns_computed" : "list",  ### Computed columns from original
  "lang"             : "list",  ## list of languages
  "description_full" : "str",
  "description_short": "str",
  "tasks"            : "list",  ## List of tasks
  "info_json"        : "str",   ## JSON String to store more infos
  "dt_update"        : "int64", ## unix

})


###########################################################################################
###########################################################################################


def ner_model_input_validate_columns(df):
    assert df[["text", "ner_list" ]].shape
    rowset = df[ "ner_list"].values[0][0]

    if isinstance(rowset, dict) : 
       assert set(rowset.keys()) == {"start", "end", "type", "tag"}, f"error {rowset}"
       
    elif isinstance(rowset, list) : 
       assert len(rowset) >= 3 , f"error {rowset}"



###########################################################################################
###########################################################################################
def hf_metadata_save(ds:DatasetDict, name=None, cols=None, dirout=None) -> None:

    from .utils.util_hf import hf_ds_meta

    name2 = name.replace("/", "_").replace("-", "_")  

    cc = Box( {})
    cc.name = name
    cc.name2 = name2
    cc.meta = hf_ds_meta(ds, meta=None, dirout=None)
    cc.dt_update = date_now(fmt="%Y%m%d %H:%M:%S",  returnval="str")
    cc.url       = f"https://huggingface.co/datasets/{name}"
    ## cc.nrows     = nrows
    cc.columns   = cols
    cc2 = box_to_dict(cc)
    log(cc2)

    ### Common Meta Folder
    json_save(cc2, f"{dirout}/meta/{name2}.json")

    ### Common Folder
    json_save(cc2, f"{dirout}/data/{name2}/meta.json")


def pd_add_default_cols_v1(df, name, colid=None):

    cols = list(df.columns)
    dtymd = date_now(fmt="%Y%M%D",  returnval="str")
    url   = f"https://huggingface.co/datasets/{name}"

    df["dataset_id"] = url
    df["dt"]         = dtymd
    df["text_id"]    = df["text"].apply(lambda x: hash_textid(x)) 

    #### Fill Missing columns with empty
    df = pd_add_missing_cols_v1(df)

    return df 


def pd_add_missing_cols_v1(df)->pd.DataFrame:

    cols = list(df.columns)
    #### Fill Missing columns with empty
    for coli, dtype, desc in SCHEMA_GLOBAL_v1:
        if coli not in cols:              
            if "str"   in  dtype : df[coli] = "" 
            if "int"   in  dtype : df[coli] = -1 
            if "float" in  dtype : df[coli] = 0.0

    cols1 = [x[0] for x in  SCHEMA_GLOBAL_v1 ] 
    df = df[cols1]
    return df 





###########################################################################################
######## Dataset Converter Classification data ############################################
def fetchnorm_cnn_dailymail(name="cnn_dailymail", version=None, dirout="./ztmp/hf_data/") :
    """ Convert  https://huggingface.co/datasets/cnn_dailymail
    Docs:    
        rows: 312k , size: 2.5 GB
        article:  str, article
        highlights: str, highlights
        id: str, id
    
    """
    cols0   = ["article", "highlights", "id"]

    dataset = datasets.load_dataset(name, version,  streaming=False) 
    hf_metadata_save(dataset, name, cols= cols0) 
    name2 = name.replace("/", "_").replace("-", "_")  

    for split in dataset.keys() :
        df = dataset[split]

        ###### Custom mapping ###########################
        df["title"]     = ""
        df["summary"]   = df["highlights"]; del df["highlights"]
        df["text"]      = df["article"]  ;  del df["article"]

        ### Other data columns not includeds
        # df["info_json"] = df.apply(lambda x: json.dumps({}), axis=1)
        # df["cat1"]      = ""
        # df["cat2"]      = ""

        df = pd_add_default_cols_v1(df, name)

        diroutk = f"{dirout}/{name2}/norm/{split}/df.parquet"
        pd_to_file(df, diroutk, show=1)



def fetchnorm_agnews(name="agnews", version=None, dirout="./ztmp/hf_data/") :
    """ Convert  https://huggingface.co/datasets/ag_news
    Docs:
        rows: 127k , size: 20 MB
        text:  str, text
        label: str, class label
    
    """
    cols0 = ["text", "label"]

    dataset = datasets.load_dataset(name, version,  streaming=False) 
    hf_metadata_save(dataset, name, cols= cols0) 
    name2 = name.replace("/", "_").replace("-", "_")  

    for split in dataset.keys() :
        df = dataset[split]

        ###### Custom mapping ###########################
        df["title"]     = ""
        df["text"]      = df["text"]
        df["cat1"]      = df["label"] ; del df["label"]

        ### Other data columns not includeds
        #df["info_json"] = df.apply(lambda x: json.dumps({}), axis=1)
        # df["cat2"]      = ""

        df = pd_add_default_cols_v1(df, name)

        diroutk = f"{dirout}/{name2}/norm/{split}/df.parquet"
        pd_to_file(df, diroutk, show=1)



def fetchnorm_big_patent(name="big_patent", version=None, dirout="./ztmp/hf_data/") :
    """ Convert  https://huggingface.co/datasets/big_patent
    Docs:    
        rows: 173k , size: 17.9 GB
        description:  str, description
        abstract: str, abstract
    
    """
    cols0 = ["description", "abstract"]

    dataset = datasets.load_dataset(name, version,  streaming=False) 
    hf_metadata_save(dataset, name, cols= cols0) 
    name2 = name.replace("/", "_").replace("-", "_")  

    for split in dataset.keys() :
        df = dataset[split]

        ###### Custom mapping ###########################
        df["title"]     = ""
        df["summary"]   = df["abstract"];      del df["abstract"]
        df["text"]      = df["description"]  ; del df["description"]

        ### Other data columns not includeds
        #df["info_json"] = df.apply(lambda x: json.dumps({}), axis=1)
        # df["cat2"]      = ""

        df = pd_add_default_cols_v1(df, name)

        diroutk = f"{dirout}/{name2}/norm/{split}/df.parquet"
        pd_to_file(df, diroutk, show=1)



def fetchnorm_ashraq_financial_news_articles(name="ashraq/financial-news-articles", version=None, dirout="./ztmp/hf_data/") :
    """ Convert        https://huggingface.co/datasets/ashraq/financial-news-articles
    Docs:    
        rows: 306k , size: 492 MB
        title:  str, title
        text: str, text
        url: str, url
    
    """
    cols0 = ["title", "text", "url"]

    dataset = datasets.load_dataset(name, version,  streaming=False) 
    hf_metadata_save(dataset, name, cols= cols0) 
    name2 = name.replace("/", "_").replace("-", "_")  

    for split in dataset.keys() :
        df = dataset[split]

        ###### Custom mapping ###########################
        df["title"]     = df["title"]
        df["summary"]   = ""
        df["text"]      = df["text"]  ; 
        df["info_json"] = df.apply(lambda x: json.dumps({"url": x["url"]}), axis=1)

        ### Other data columns not includeds
        # df["cat2"]      = ""

        df = pd_add_default_cols_v1(df, name)

        diroutk = f"{dirout}/{name2}/norm/{split}/df.parquet"
        pd_to_file(df, diroutk, show=1)









###########################################################################################
######## Dataset Converter NER for Gliner  ############################################

def data_converter_collnll2003(dirout="./ztmp/data/ner/conll2003",  nrows=100000000):
   """Convert raw data to NER Parquet format.
      NER_COLSTARGET       = ["dataset_id", "dataset_cat1", "text_id",  "text", "ner_list",  "info_json" ]

      pip install fire utilmy

      python data_pd.py data_converter_collnll2003  

   
       ### Initial Format
        id, tokens, , pos_tags, chunk_tags,  ner_tags, 0	
                [ "EU", "rejects", "German", "call", "to", "boycott", "British", "lamb", "." ]	
                [ 22, 42, 16, 21, 35, 37, 16, 21, 7 ]	
                [ 11, 21, 11, 12, 21, 22, 11, 12, 0 ]	
                [ 3, 0, 7, 0, 0, 0, 7, 0, 0 ]

       ### Target Format
          NER_COLSTARGET       = ["dataset_id", "dataset_cat1",   "text_id"  "text", "ner_list", "info_json" ]
           "text" :     Full text concatenated as string.
           "ner_list" : [ ( str_idx_start, str_idx_end, ner_tag),   ( idx_start, idx_end, ner_tag),   .... ( idx_start, idx_end, ner_tag),      ]


       Custom tokenizer    
       
   """
   dataset  = "conll2003"
   version = None
   dataset_cat = "english/news"

   url = "https://huggingface.co/datasets/" + dataset 
   ds0 = datasets.load_dataset(dataset,)  ### option to donwload in disk only

   ds0.save_to_disk(dirout +"/raw/")

   def ner_merge_BOI_to_triplet_v1(tokens:list, ner_tags:list): 
      """Converts NER tags and tokens into triplets based on specified conditions.
       # {'O': 0, 'B-PER': 1, 'I-PER': 2, 'B-ORG': 3, 'I-ORG': 4, 'B-LOC': 5, 'I-LOC': 6, 'B-MISC': 7, 'I-MISC': 8}
       # Merge B-PER, I-PER as PER, similarly for ORG, LOC, MISC

        

       Target format is : 
          "ner_list" : [ ( string_idx_start, string_idx_end, ner_tag),   ( idx_start, idx_end, ner_tag),   .... ( idx_start, idx_end, ner_tag),      ]
           idx_start: position of string.  

    
      ### Issue with list of triplet --> when saving as parquet file.
           Triplet has to be All strings, even indices, for parquet
      """
      map_custom = {'O': 0, 'B-PER': 1, 'I-PER': 2, 'B-ORG': 3, 'I-ORG': 4, 'B-LOC': 5, 
                    'I-LOC': 6, 'B-MISC': 7, 'I-MISC': 8}
      ### Zero are exclude : no meaning
      ner_list  = []
      start_idx = -1
      ner_tag   = -1
      for i, _ in enumerate(tokens):

         ### Start of NER :   B-   token
         if ner_tags[i] in [1, 3, 5, 7]:   
            if start_idx != -1:
                ### 
                ner_list.append([ start_idx, i - 1, str(ner_tag) ])
            start_idx = i
            ner_tag   = ner_tags[i]


         ## End  :  when current tag is 0 : enpty NER
         elif ner_tags[i] == 0 and start_idx != -1:
            ner_list.append([ start_idx, i - 1, str(ner_tag) ])
            start_idx = -1

      ### Last NER 
      if start_idx != -1:
         ner_list.append([ start_idx, len(tokens) - 1, str(ner_tag) ])


      ### Convert token_id  to string_idx (str_start, str_end)
      token_len =[ len(tokens[0]) ]
      i= 1
      onespace = 1
      for tok in tokens[1:]:  ### cumulative length, One space separator 
         token_len.append( token_len[i-1] + len(tok) + onespace)
         i += 1

      ner_list2 = []
      for (i0, i1, tag) in ner_list:
         idx0 = 1+token_len[i0-1] if i0>1 else 0
         idx1 = token_len[i1]
         ner_list2.append( (str(idx0), str(idx1), tag))

      return ner_list2


   ### dtype: "train", "test"
   for dtype in ds0.keys():  
        log("#### Converting", dtype)  
        ds = ds0[dtype]  ### ds is custom Object, not dataframe.
        ds = ds.filter(lambda _, idx: idx < nrows, with_indices=True)  # reduce number of rows

        log("#### Convert/Normalize to Standard Format  ################################")
        df2        = pd.DataFrame(columns=NER_COLSTARGET) 

        ### ["dataset_id", "text_id",  "text", "ner_list", "cat1", "info_json" ]
        df2["dataset_id"]   = url
        df2["dataset_cat1"] = dataset_cat
        df2["info_json"]    = ""  


        #### Text: 1 row : Concetanate all tokens merged into one string  (because of BOI tokenizer).
        df2["text"]      = list(map(lambda x: " ".join(x), ds["tokens"])) 

        #### NER_list : [ ( string_idx_start, string_idx_end, ner_tag),   ( idx_start, idx_end, ner_tag),   .... ( idx_start, idx_end, ner_tag),      ]
        #### idx_start: position of string.  
        df2["ner_list"]  = list(map(lambda x: ner_merge_BOI_to_triplet_v1(x[0], x[1]), zip(ds["tokens"], ds["ner_tags"])))

        ### Use text to generate unique hash
        df2["text_id"]      =  df2["text"].apply(lambda x : hash_textid(x) )


        log("#### Save to parquet  ################################")
        pd_to_file(df2[ NER_COLSTARGET ], dirout + f"/norm/{dtype}/df.parquet", show=1)






def data_converter_DFKI_few_nerd(dirout="ztmp/data/ner/few_nerd/",  nrows=100000000):
    # -*- coding: utf-8 -*-
    """fewnerd_data.ipynb

    Automatically generated by Colab.

    Original file is located at
        https://colab.research.google.com/drive/1QnkW3ZGl1Un__hOn8-gVsJf_1Z3kIpda
    """
    # Read text file
    with open('./ztmp/data/DFKI-SLT few-nerd/test.txt', 'r') as file:
        lines = file.readlines()

    # Initialize variables
    sentences = []
    sentence_id = 1

    # Loop through lines to create sentences and assign sentence_id
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespaces
        if line:  # If line is not blank
            word, label = line.split('\t')  # Assuming each line has format "word\tlabel"
            sentences.append({'Word': word, 'Label': label, 'Sentence_id': sentence_id})
        else:  # If a blank line is encountered, increment sentence_id
            sentence_id += 1

    # Create DataFrame
    df = pd.DataFrame(sentences)


    NER_COLSTARGET = ["dataset_id", "text_id", "text", "ner_list", "dataset_cat1", "info_json"]
    NER_COLSTARGET_TYPES = ["str", "int64", "str", "list", "str", "str"]

    df2 = df.groupby('Sentence_id').agg({'Word': list, 'Label': list}).reset_index()

    type(df2['Word'][0])

    def tags_to_ner_list(words, tags):
        ner_list = []
        start_idx = 0
        for word, tag in zip(words, tags):
            if tag != 'O':
                end_idx = start_idx + len(str(word))
                ner_list.append((str(start_idx), str(end_idx), tag))
            start_idx += len(str(word)) + 1  # Add 1 for space after each word
        return ner_list

    df2['ner_list'] = df2.apply(lambda x: tags_to_ner_list(x['Word'], x['Label']), axis=1)
    type(df2['ner_list'][0])


    df2['dataset_id'] = 'https://huggingface.co/datasets/DFKI-SLT/few-nerd'
    df2['text_id'] = df2.index
    # df2['text'] = df2['Word'].apply(lambda x: ''.join(str(x)))
    df2['text'] = df2['Word'].apply(lambda x: ' '.join(str(word) for word in x))
    df2['cat1'] = 'english/news'
    df2['info_json'] = 'test'
    df2.head()

    df2 = df2[NER_COLSTARGET]
    df2.head()


    df2['dataset_id'] = df2['dataset_id'].astype(str)
    df2['text_id'] = df2['text_id'].astype(int)
    df2['text'] = df2['text'].astype(str)
    df2['cat1'] = df2['cat1'].astype(str)
    df2['info_json'] = df2['info_json'].astype(str)

    pd_to_file(df2, './ztmp/data/ner/norm/DFKI-SLT/few-nerd/few_nerd-test.parquet')
























################################################################################################
########## NER Dataset Converter ###############################################################
# NER_COLSTARGET       = ["dataset_id", "text_id", "text", "ner_list", "dataset_cat", "info_json"]
# NER_COLSTARGET_TYPES = ["str", "int64", "str", "list", "str", "str"]

NER_COLSTARGET       = [x[0] for x in SCHEMA_GLOBAL_v1]
NER_COLSTARGET_TYPES = [x[1] for x in SCHEMA_GLOBAL_v1]


def pd_add_default_cols_v2(df, url, category, info):

    #### Add default columns
    df['dataset_id']  = url
    df['dataset_cat'] = category

    df['text']       = df['Word'].apply(lambda x: ' '.join(str(word) for word in x))
    df['text_id']    = df['text'].apply(lambda x: hash_textid(x) ) 

    df['ner_list']   = df.apply(lambda x: ner_tags_to_ner_list(x['Word'], x['Tag']), axis=1)
    df['info_json']  = info

    #### Fill Missing columns with empty
    df = pd_add_missing_cols_v1(df)

    #### Convert all columns to correct types
    COLS  = [x[0] for x in SCHEMA_GLOBAL_v1]
    DTYPE = [x[1] for x in SCHEMA_GLOBAL_v1]
    
    df = df[COLS]    
    for i, coli in enumerate(COLS):
        dtype = DTYPE[i]
        if "int" not in dtype and "float" not in dtype and "str" not in dtype :
            continue
        df[coli] = df[coli].astype(dtype)

    return df



######################################################################################
def download_re3d(output_dir: str = "./ztmp/re3d") -> None:
    file_urls = [
        'https://raw.githubusercontent.com/juand-r/entity-recognition-datasets/master/data/re3d/CONLL-format/data/train/re3d-train.conll',
        'https://raw.githubusercontent.com/juand-r/entity-recognition-datasets/master/data/re3d/CONLL-format/data/test/re3d-test.conll'
    ]
    save_paths = [
        os.path.join(output_dir, 're3d_train.txt'),
        os.path.join(output_dir, 're3d_test.txt')
    ]
    for url, path in zip(file_urls, save_paths):
        response = requests.get(url)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as file:
            file.write(response.content)


def download_gum(output_dir: str = "./ztmp/gum") -> None:
    file_urls = [
        'https://raw.githubusercontent.com/juand-r/entity-recognition-datasets/master/data/GUM/CONLL-format/data/train/gum-train.conll',
        'https://raw.githubusercontent.com/juand-r/entity-recognition-datasets/master/data/GUM/CONLL-format/data/test/gum-test.conll'
    ]
    save_paths = [
        os.path.join(output_dir, 'gum_train.txt'),
        os.path.join(output_dir, 'gum_test.txt')
    ]
    for url, path in zip(file_urls, save_paths):
        response = requests.get(url)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as file:
            file.write(response.content)


def download_debasis(output_dir="./ztmp/debasis"):
    url = 'https://media.githubusercontent.com/media/neavepaul/NER-Datasets/main/ner_data.csv'
    os.makedirs(output_dir, exist_ok=True)    
    response = requests.get(url)

    with open(os.path.join(output_dir, 'debasis_ner.csv'), "wb") as file:
        file.write(response.content)


def download_fewnerd(output_dir="./ztmp/fewnerd"):
    """
    Download and unzip few-nerd datasets from specified URLs and save them to output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    subsets = {
        'supervised': 'https://cloud.tsinghua.edu.cn/f/c1f71c011d6b461786bc/?dl=1',
        'inter': 'https://cloud.tsinghua.edu.cn/f/3d84d34dc5d845a2bed2/?dl=1',
        'intra': 'https://cloud.tsinghua.edu.cn/f/a176a4870f0a4f8ba0db/?dl=1',
    }

    for subset, url in subsets.items():
        zip_path = os.path.join(output_dir, f"{subset}.zip")
        extract_path = output_dir

        print(f"Downloading {subset} dataset...")
        download_file(url, zip_path)
        print(f"Unzipping {subset} dataset...")
        zip_unzip(zip_path, extract_path)
        os.remove(zip_path)
        print(f"Finished processing {subset} dataset.")


def download_ewnertc(output_dir="./ztmp/ewnertc"):
    url = 'https://github.com/neavepaul/NER-Datasets/raw/main/EWNERTC.csv'
    os.makedirs(output_dir, exist_ok=True)    
    response = requests.get(url)

    with open(os.path.join(output_dir, 'ewnertc_ner.csv'), "wb") as file:
        file.write(response.content)



def fetchnorm_debasis(dirfile="./ztmp/debasis/debasis_ner.csv",  dirout="./ztmp/debasis/debasis_ner.parquet"):
    url="https://www.kaggle.com/datasets/debasisdotcom/name-entity-recognition-ner-dataset"
    category="english/news"
    info=""
    df               = pd.read_csv(dirfile, encoding='utf8')
    df['Sentence #'] = df['Sentence #'].ffill()
    dfg              = df.groupby('Sentence #').agg({'Word': list, 'Tag': list}).reset_index()
    # dfg['ner_list']  = dfg.apply(lambda x: ner_tags_to_ner_list(x['Word'], x['Tag']), axis=1)
    dfg              = pd_add_default_cols_v2(dfg, url, category, info)
    pd_to_file(dfg,  dirout, show=1)



def fetchnorm_fewnerd(input_dir="./ztmp/fewnerd", output_dir="./ztmp/fewnerd"):
    """
    Normalize all files in subdirectories of input_dir and save them as Parquet files in corresponding output_dir subdirectories.
    """
    url = "https://github.com/thunlp/Few-NERD"
    category = "english/general"
    info = ""

    for subset in ["supervised", "inter", "intra"]:
        subset_dir = os.path.join(input_dir, subset)
        if not os.path.exists(subset_dir):
            continue
        
        for filename in os.listdir(subset_dir):
            if filename.endswith(".txt"):
                txt_file        = os.path.join(subset_dir, filename)
                df              = read_format_to_df(txt_file)
                df              = df.rename(columns={'Label': 'Tag'})
                dfg             = df.groupby('Sentence_id').agg({'Word': list, 'Label': list}).reset_index()
                # dfg['ner_list'] = dfg.apply(lambda x: ner_tags_to_ner_list(x['Word'], x['Tag']), axis=1)
                dfg             = pd_add_default_cols_v2(dfg, url, category, info)
                output_file     = os.path.join(output_dir, subset, filename.replace('.txt', '.parquet'))
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                pd_to_file(dfg, output_file, show=1)



def fetchnorm_gum(input_dir="./ztmp/gum", output_dir="./ztmp/gum"):
    """
    Dowload files using util function download_gum() then run this converter passing file path.
    """
    url="https://gucorpling.org/gum/"
    category="english/general"
    info=""
    file_list = os.listdir(input_dir)
    for file_name in file_list:
        input_file      = os.path.join(input_dir, file_name)
        output_file     = os.path.join(output_dir, file_name.replace(".txt", ".parquet"))
        df              = read_format_to_df(input_file)
        df              = df.rename(columns={'Label': 'Tag'})
        dfg             = df.groupby('Sentence_id').agg({'Word': list, 'Tag': list}).reset_index()
        # dfg['ner_list'] = dfg.apply(lambda x: ner_tags_to_ner_list(x['Word'], x['Tag']), axis=1)
        dfg             = pd_add_default_cols_v2(dfg, url, category, info)
        pd_to_file(dfg, output_file, show=1)




def fetchnorm_re3d(input_dir="./ztmp/re3d", output_dir="./ztmp/re3d"):
    """
    Dowload files using util function download_re3d() then run this converter passing input directory.
    """
    url="https://github.com/dstl/re3d"
    category="english/news"
    info=""
    file_list = os.listdir(input_dir)
    for file_name in file_list:
        input_file      = os.path.join(input_dir, file_name)
        output_file     = os.path.join(output_dir, file_name.replace(".txt", ".parquet"))
        df              = read_format_to_df(input_file)
        df              = df.rename(columns={'Label': 'Tag'})
        dfg             = df.groupby('Sentence_id').agg({'Word': list, 'Tag': list}).reset_index()
        # dfg['ner_list'] = dfg.apply(lambda x: ner_tags_to_ner_list(x['Word'], x['Tag']), axis=1)
        dfg             = pd_add_default_cols_v2(dfg, url, category, info)
        pd_to_file(dfg, output_file, show=1)



def fetchnorm_ewnertc(dirfile="./ztmp/ewnertc/ewnertc_ner.csv",  dirout="./ztmp/ewnertc/ewnertc_ner.parquet"):
    """
    Dowload file from kaggle from link below. then run this converter passing file path
    """

    url="https://www.kaggle.com/datasets/akshay235/ewnertc-ner-dataset"
    category="english/general"
    info=""
    # Less RAM workaround
    # df = pd.read_csv(dirfile, encoding='utf8', nrows=10000000)

    df = pd.read_csv(dirfile, encoding='utf8')
    df.fillna('', inplace=True)
    df['Tags'] = df['Tags'].str.replace("'", "").str.replace("[", "").str.replace("]", "").str.replace(",", "")
    df['Sentences'] = df['Sentences'].str.replace("'", "").str.replace("[", "").str.replace("]", "").str.replace(",", "")
    df.loc[df['Sentences']=='', 'Sentences'] = ','
    sentence_id = 1
    sentence_ids = []
    for sentence in df['Sentences']:
        if ".\\n" in sentence:
            sentence_id += 1
        sentence_ids.append(sentence_id)
        
    df['Sentence_id']  = sentence_ids
    df['Sentence_id']  = df['Sentence_id'].ffill()
    df                 = df.rename(columns={'Sentences': 'Word', 'Tags': 'Tag'})
    dfg                = df.groupby('Sentence_id').agg({'Word': list, 'Tag': list}).reset_index()
    # dfg['ner_list']    = dfg.apply(lambda x: ner_tags_to_ner_list(x['Sentences'], x['Tag']), axis=1)
    dfg                = pd_add_default_cols_v2(dfg, url, category, info)
    dfg                = dfg[NER_COLSTARGET]
    dfg                = dfg.iloc[:-1]
    dfg.loc[0, 'text'] = "XX Radawa is a village in administrative district of Gmina Wizownica , within Jarosaw County , Subcarpathian Voivodeship , in south eastern Poland"
    pd_to_file(dfg,  dirout, show=1)









########################################################################################################
######### NER Dataset utils#############################################################################
def ner_tags_to_ner_list(words, tags):
    ner_list = []
    start_idx = 0
    for word, tag in zip(words, tags):
        if tag != 'O':
            end_idx = start_idx + len(str(word))
            ner_list.append((str(start_idx), str(end_idx), tag))
        start_idx += len(str(word)) + 1
    return ner_list


def open_readlines(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()
    

def read_format_to_df(file_path):
    with open(file_path, 'r') as file:
        lines= file.readlines()

    sentences = []
    sentence_id = 1
    for line in lines:
        line = line.strip()
        if line:
            word, label = line.split('\t')
            sentences.append({'Word': word, 'Label': label, 'Sentence_id': sentence_id})
        else:
            sentence_id += 1
    return pd.DataFrame(sentences)







#######################################################################################
######## HF utils  ####################################################################
def hf_ds_to_disk_batch(dataset:DatasetDict, dirout: str = "./ztmp/hf_online/agnews", 
        batch_size: int = 50000, kmax:int=10000):

    log("\n###### Save dataset on disk ")
    for key in dataset.keys():
        len_df  = len(dataset[key])
        n_batch = (len_df + batch_size - 1) // batch_size  
        
        for k in range(0, n_batch):
            if k > kmax : break
            data_k = dataset[key][k * batch_size: (k + 1) * batch_size]
            
            dfk = pd.DataFrame(data_k)
            dirout = f"{dirout}/{key}/df_{k}.parquet"
            pd_to_file(dfk, dirout, show=1) 



def hf_dataset_meta_todict(dataset=None, metadata=None):
   metadata = { "split": [] } 
   for split in dataset.keys():  ### Train
      ##### Convert metadata to dictionary
      mdict = {key: value for key, value in dataset[split].info.__dict__.items()}
      metadata[split] = mdict
      metadata["split"].append(split)

   return metadata   



def dataset_kaggle_to_parquet(name, dirout: str = "kaggle_datasets", mapping: dict = None, overwrite=False):
    """Converts a Kaggle dataset to a Parquet file.
    Args:
        dataset_name (str):  name of  dataset.
        dirout (str):   dirout directory.
        mapping (dict):  mapping of  column names. Defaults to None.
        overwrite (bool, optional):  whether to overwrite existing files. Defaults to False.
    """
    import kaggle
    # download dataset and decompress
    kaggle.api.dataset_download_files(name, path=dirout, unzip=True)

    df = pd_read_file(dirout + "/**/*.csv", npool=4)
    if mapping is not None:
        df = df.rename(columns=mapping)

    pd_to_file(df, dirout + f"/{name}/parquet/df.parquet")




#######################################################################################
######## Pandas utils  ################################################################
def pd_check_ram_usage(df):
    # Determine proper batch size
    min_batch_size = 1000
    max_batch_size = 100000
    test_df = df.iloc[:10, :]
    test_memory_mb = test_df.memory_usage(deep=True).sum() / (1024 * 1024)
    log("first 10 rows memory size: ", test_memory_mb)
    batch_size = min (max( int(1024 * 10 // test_memory_mb // 1000 * 1000 ), min_batch_size ), max_batch_size)


def pd_text_normalize_clean(df: pd.DataFrame) -> pd.DataFrame:
    # Combine title and text columns
    import re
    df['content'] = df['title'] + " " + df['text']

    # Remove special characters, punctuation, and extra whitespaces
    df['content'] = df['content'].apply(lambda x: re.sub(r'\s+', ' ', x))  # Remove extra whitespaces
    df['content'] = df['content'].apply(lambda x: re.sub(r'[^\w\s]', '', x))  # Remove special characters
    df['content'] = df['content'].apply(lambda x: x.lower())  # Convert text to lowercase

    # Drop unnecessary columns
    #df.drop(columns=['title', 'text', 'url'], inplace=True)

    return df


def pd_to_file_split(df, dirout, ksize=1000):
    kmax = int(len(df) // ksize) + 1
    for k in range(0, kmax):
        log(k, ksize)
        dirout = f"{dirout}/df_{k}.parquet"
        pd_to_file(df.iloc[k * ksize : (k + 1) * ksize, :], dirout, show=0)


def pd_fake_data(nrows=1000, dirout=None, overwrite=False, reuse=True) -> pd.DataFrame:
    from faker import Faker

    if os.path.exists(str(dirout)) and reuse:
        log("Loading from disk")
        df = pd_read_file(dirout)
        return df

    fake = Faker()
    dtunix = date_now(returnval="unix")
    df = pd.DataFrame()

    ##### id is integer64bits
    df["id"] = [i for i in range(nrows)]
    df["dt"] = [int(dtunix) for i in range(nrows)]

    df["title"] = [fake.name() for i in range(nrows)]
    df["text"] = [fake.text() for i in range(nrows)]
    df["cat1"] = np_str(np.random.randint(0, 10, nrows))
    df["cat2"] = np_str(np.random.randint(0, 50, nrows))
    df["cat3"] = np_str(np.random.randint(0, 100, nrows))
    df["cat4"] = np_str(np.random.randint(0, 200, nrows))
    df["cat5"] = np_str(np.random.randint(0, 500, nrows))

    if dirout is not None:
        if not os.path.exists(dirout) or overwrite:
            pd_to_file(df, dirout, show=1)

    log(df.head(1), df.shape)
    return df


def pd_fake_data_batch(nrows=1000, dirout=None, nfile=1, overwrite=False) -> None:
    """Generate a batch of fake data and save it to Parquet files.

    python engine.py  pd_fake_data_batch --nrows 100000  dirout='ztmp/files/'  --nfile 10

    """

    for i in range(0, nfile):
        dirouti = f"{dirout}/df_text_{i}.parquet"
        pd_fake_data(nrows=nrows, dirout=dirouti, overwrite=overwrite)





#######################################################################################
########## utils   ####################################################################
def download_file(url, output_path):
    """
    Download a file from a URL to a local path.
    """
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded to {output_path}")


def zip_unzip(zip_path, extract_path):
    """
    Unzip a file to a specified directory.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if not member.startswith('__MACOSX'):
                zip_ref.extract(member, extract_path)
    print(f"Extracted to {extract_path}")



def box_to_dict(box_obj):

    from box import (Box, BoxList,  )
    if isinstance(box_obj, Box):
        box_obj = {k: box_to_dict(v) for k, v in box_obj.items()}

    elif isinstance(box_obj, dict):
        return {k: box_to_dict(v) for k, v in box_obj.items()}
    elif isinstance(box_obj, list):
        return [box_to_dict(v) for v in box_obj]

    return str(box_obj) 


def np_str(v):
    return np.array([str(xi) for xi in v])




###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()















def zzz_run_convert(name="ag_news", diroot: str = "./ztmp/hf_datasets", 
                splits: list = None, schema_fun: str = None,
                batch_size: int = 50000,
                kmax:int=1
):
    """Converts a Hugging Face dataset to a Normalized Parquet file + JSON metadata.

    Args
            dataset_name (str):  name of  dataset.
            dirout (str):   dirout directory.

        python data.py run_convert --name "ag_news"  --diroot  "./ztmp/hf_datasets/"   


      dirfile: 
         DatasetDict({
            train: Dataset({  features: ['text', 'label'],  num_rows: 120000  })
            test: Dataset({ features: ['text', 'label'], num_rows: 7600 })})

       dirout: parquet with those columns
            SCHEMA_GLOBAL_v1
                ("text_id",  "int64", "global unique ID for text"),
                ("text_id2", "int64", "text_id from original dataset"),

                ("dataset_id", "str",   "URL of dataset"),
                ("dt", "float64", "Unix timestamps"),

                ("title", "str", " Title "),
                ("summary", "str", " Summary "),
                ("text", "str", " Core text "),
                ("info_json", "str", " Extra info in JSON string format "),


                ("cat1", "str", " Category 1 or label "),
                ("cat2", "str", " Category 2 or label "),
                ("cat3", "str", " Category 3 or label "),
                ("cat4", "str", " Category 4 or label "),
                ("cat5", "str", " Category 5 or label "),

    """
    cc = Box( copy.deepcopy(meta_json))
    name2 = name.replace("/","_").replace("-","_")
    cc.name        = name
    cc.name_unique = name2


    ### "ashraq/financial-news-articles"  -->  "ashraq_financial_news_articles"
    log("\n##### Schema function loader ") 
    if schema_fun is None: 
        schema_fun_name  = f"schema_{name2}"
    
    convert_fun = globals()[ schema_fun_name ]  #load_function_uri(f"data.py:{schema_fun}")
    log(convert_fun) ### check
    
  
    log("\n######  Version ")
    version = None
    if name == "cnn_dailymail":  version =  "3.0.0"



    log("\n######  Loading dataset ")
    dataset = datasets.load_dataset(name, version,  streaming=False) 
    splits      = [ key for key in dataset.keys() ] 

    log("\n###### Convert dataset into ", diroot)
    nrows=0    
    for key in splits:
        len_df  = len(dataset[key])
        n_batch = (len_df + batch_size - 1) // batch_size  
        
        for k in range(0, n_batch):
            if k > kmax : break
            data_k = dataset[key][k * batch_size: (k + 1) * batch_size]
            
            dfk = pd.DataFrame(data_k)
            dfk = convert_fun(dfk, meta_dict=cc)  # Assuming convert_fun is defined in file

            log(list(dfk.columns), dfk.shape)
            nrows += len(dfk)
            dirout = f"{diroot}/data/{name2}/{key}/df_{k}.parquet"
            pd_to_file(dfk, dirout, show=1) 


    log("\n##### meta.json  ")
    hf_metadata_save(dataset, name)

