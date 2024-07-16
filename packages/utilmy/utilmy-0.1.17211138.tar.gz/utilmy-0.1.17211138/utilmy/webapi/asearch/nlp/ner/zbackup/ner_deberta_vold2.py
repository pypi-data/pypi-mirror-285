# -*- coding: utf-8 -*-
"""NER Deberta

   ### Install
    https://colab.research.google.com/drive/1x-LlluSePdD1ekyItadNNQuvlOc65Qpz

    !pip install utilmy fire python-box
    !pip install -q -U bitsandbytes peft accelerate  transformers==4.37.2
    !pip install datasets transformers fastembed simsimd
    !pip install -q seqeval

    ### Do this step
        pip install --upgrade utilmy


    ### Dataset Download
    cd asearch
    mkdir -p ./ztmp/
    cd "./ztmp/"
    git clone https://github.com/arita37/data2.git   data
    cd data
    git checkout text

       #### Check Dataset
       cd ../../
       ls ./ztmp/data/ner/ner_geo/


    ### Usage:
       cd asearch
       export PYTHONPATH="$(pwd)"  ### Need for correct import

       export pyner="python nlp/ner/ner_deberta.py "

       pyner run_train  --dirout ztmp/exp   --cfg config/train.yaml --cfg_name ner_deberta_v1

       pyner run_infer  --dirmodel ztmp/exp  --dirdata


    ### Export ONNX model
       python onnx_export.py export --dirin ztmp/exp/20240101/173456/models/pytorch_model.bin  --dirout ztmp/latest/ner_deberta_v1/

       python onnx_export.py run -dirmodel ztmp/latest/ner_deberta_v1  --dirdata ztmp/data/ner/ner_geo/



   ### Input dataset:
        REQUIRED_SCHEMA_GLOBAL_v1 = [
            ("text_id",  "int64", "global unique ID for   text"),

            ("text", "str", " Core text "),

            ("ner_list", "list", " List of triplets (str_idx_start, str_idx_end, ner_tag) "),
                 str_idx_start : index start of tag inside   String.
                 str_idx_end:    index start of tag inside   String.
            ]



        OPTIONAL_SCHEMA_GLOBAL_v1 = [
            ("text_id",  "int64", "global unique ID for   text"),
            ("text_id2", "int64", "text_id from original dataset"),

            ("dataset_id",  "str",   "URL of   dataset"),
            ("dataset_cat", "str",   "Category tags : english/news/"),

            ("dt", "float64", "Unix timestamps"),

            ("title", "str", " Title "),
            ("summary", "str", " Summary "),
            ("info_json", "str", " Extra info in JSON string format "),


            ("cat1", "str", " Category 1 or label "),
            ("cat2", "str", " Category 2 or label "),
            ("cat3", "str", " Category 3 or label "),
            ("cat4", "str", " Category 4 or label "),
            ("cat5", "str", " Category 5 or label "),

        ]






"""

if "Import":
    import json,re, os, pandas as pd, numpy as np,copy
    from dataclasses import dataclass
    from typing import Optional, Union
    from box import Box

    from functools import partial
    import datasets 
    from datasets import Dataset, load_metric
    # If issue dataset: please restart session and run cell again
    from transformers import (
        TrainingArguments,
        Trainer,

        AutoTokenizer,
        AutoModelForTokenClassification,  #### NER Tasks

        ### LLM
    )
    # from transformers.models.qwen2.modeling_qwen2 import
    from transformers.tokenization_utils_base import PreTrainedTokenizerBase, PaddingStrategy

    import spacy, torch

    from utilmy import (date_now, date_now, pd_to_file, log, pd_read_file, json_save, config_load
                        )
    ### PTYHONPATH="$(pwd)"
    from utils.util_exp import (exp_create_exp_folder, exp_config_override, exp_get_filelist)


####################################################################################
####### Custom dataset XXX #########################################################
global NCLASS, L2I, I2L
NCLASS =0
L2I={}
I2L={}

def  dataXX_load_prepro():
    """ 
    Sample data:

            query	answer	answerfull	answer_fmt
        0	find kindergarten and tech startup in Crack...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Cracker Barrel Old Cou...
        1	This afternoon, I have an appointment to Mitsu...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Mitsuwa Marketplace',c...
        2	find train and embassy near by Brooklyn Bri...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Brooklyn Bridge Park S...
        3	This afternoon, I have an appointment to Nowhe...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Nowhere',city='New Yor...
        4	This afternoon, I have an appointment to Wawa....	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Wawa',country='US',loc...


    """
    dirout0='./ztmp/out/ner_geo'
    dt = date_now(fmt="%Y%m%d_%H%M%S")
    dirout= os.path.join(dirout0, dt)
    os.makedirs(dirout)


    ##### Load Data #################################################
    #cd ./ztmp/
    #git clone https://github.com/arita37/data2.git   data
    #cd data
    #git checkout text
    dirtrain = "./ztmp/data/ner/ner_geo/raw/df_10000_1521.parquet"
    dirtest  = "./ztmp/data/ner/ner_geo/raw/df_1000.parquet"

    df        = pd_read_file(dirtrain)#.sample(2000)
    log(df)
    df_test   = pd_read_file(dirtest)#.head(100)
    log(df_test)

    cols0 = [ "query",	"answer",	"answerfull",	"answer_fmt"]
    assert df[cols0].shape
    assert df_test[cols0].shape

    colsmap= {"query": "text",}
    df      = df.rename(columns= colsmap)
    df_test = df.rename(columns= colsmap)


    #### Data Enhancement ##########################################
    ex= []
    for i in range(200):
        r = df.sample(1).iloc[0].to_dict()
        query = r["text"]
        s = np.random.randint(len(query))
        if np.random.random()>0.5:
            query = query + f', around {s}km. '
        else:
            query = f'around {s} km. ' + query
        r["text"] = query
        ex.append(r)

    # query = query + ", around 8km."
    df  = pd.concat([df, pd.DataFrame(ex)])

    df["ner_list"]      = df.apply(dataXX_fun_prepro_text_predict, axis=1)
    df_test["ner_list"] = df_test.apply(dataXX_fun_prepro_text_predict, axis=1)
    log( df.head() )
    log( df_test.sample(1).to_dict())


    assert df[["text", "ner_list" ]].shape    
    assert df_test[["text", "ner_list" ]].shape    


   ################################################################ 
   ###### External validation ##################################### 
    nerdata_validate_dataframe(df)
    nerdata_validate_dataframe(df_test)

    return df, df_test


def dataXX_fun_prepro_text_predict(row):
    """
       # Location, address, city, country, location_type, type_exclude
       # Location_type=\[(.*?)\],location_type_exclude=\[(.*?)\]

    """
    text  = row['answer_fmt']
    query = row["text"]
    # location = re.findall(r"location='(.*?)'", p[0])
    pattern = r"location='(.*?)',"
    matches = re.findall(pattern, text)
    values = []
    if len(matches):
        assert len(matches) == 1, matches
        values.append(
            {
                'type':'location',
                'value': matches[0],
                'start': query.index(matches[0]),
                'end' : query.index(matches[0]) + len(matches[0])
            }
        )

    pattern = r"city='(.*?)',"
    matches = re.findall(pattern, text)
    if len(matches):
        assert len(matches) == 1, matches
        values.append(
            {
                'type':'city',
                'value': matches[0],
                'start': query.index(matches[0]),
                'end' : query.index(matches[0]) + len(matches[0])
            }
        )
    pattern = r"country='(.*?)',"
    matches = re.findall(pattern, text)
    if len(matches):
        assert len(matches) == 1, matches

        values.append(
            {
                'type':'country',
                'value': matches[0],
                'start': query.index(matches[0]),
                'end' : query.index(matches[0]) + len(matches[0])
            }
        )

    pattern = r"location_type=\[(.*?)\]"
    matches = re.findall(pattern, text)
    if len(matches):
        assert len(matches) == 1, matches
        if len(matches[0].strip()):
            for i in matches[0].split(","):
                x = i.strip()
                if x[0] == "'" and x[-1] == "'":
                    x=x[1:-1]
                if x not in query:
                    print(x, query)
                values.append(
                    {
                        'type':'location_type',
                        'value': x,
                        'start': query.index(x),
                        'end' : query.index(x) + len(x)
                    }
                )

    pattern = r"location_type_exclude=\[(.*?)\]"
    matches = re.findall(pattern, text)
    if len(matches):
        assert len(matches) == 1, matches
        if len(matches[0].strip()):
            for i in matches[0].split(","):
                x = i.strip()
                if x[0] == "'" and x[-1] == "'":
                    x=x[1:-1]
                values.append(
                    {
                    'type':'location_type_exclude',
                    'value': x,

                    'start': query.index(x),
                    'end' : query.index(x) + len(x)
                    }
                )
    return values


def dataXX_fun_extract_from_answer_full(row):
    """  
        #             address': '4700 Gilbert Ave',
        #    'city': 'Chicago',
        #    'country': 'United States',
        #    'location_type': 'hot dog stand and viewpoint',
        #    'location_type_exclude': [],
        #     query = row["text"]

    """
    dict_i4 = json.loads(row['answerfull'])['args']
    query = row["text"]
    values =[]
    for key, value in dict_i4.items():
        if key=='place_name':
            key='location'
        if key =='radius' or key=='navigation_style':continue
        if key =='location_type':
            value = value.split("and")
            value = [i.strip() for i in value]
            values.extend([{
                'type':key,
                'value': i,
                'start': query.index(i),
                'end': query.index(i) + len(i)
            } for i in value])
        elif key =='location_type_exclude':
            if isinstance(value, str):
                value = value.split("and")
                value = [i.strip() for i in value]
                values.extend([{
                    'type':key,
                    'value': i,
                    'start': query.index(i),
                    'end': query.index(i) + len(i)
                } for i in value])
            else:
                assert len(value) == 0
        else:
            if value.strip() not in query:
                print(value, 'x', query, 'x', key)
            values.append(
                {
                    'type': key,
                    'value': value.strip(),
                    'start': query.index(value.strip()),
                    'end': query.index(value.strip()) + len(value.strip())
                }
            )
    return values


def dataXX_create_label_mapper():
    
    global NCLASS, L2I, I2L
    NCLASS=5

    L2I = {
    }
    for index, c in enumerate(['location', 'city', 'country', 'location_type', 'location_type_exclude']):
        L2I[f'B-{c}'] = index
        L2I[f'I-{c}'] = index + NCLASS
    L2I['O'] = NCLASS*2
    L2I['Special'] = -100
    L2I

    I2L = {}
    for k, v in L2I.items():
        I2L[v] = k
    I2L[-100] = 'Special'

    I2L = dict(I2L)
    log(I2L)

    return L2I, I2L, NCLASS



################################################################################
########## Custom dataset XXX Eval  #############################################
def dataXX_predict_generate_text_fromtags(dfpred, dirout="./ztmp/metrics/"):
    """  Generate text from TAGS

    """
    if isinstance(dfpred, str):
       dfpred= pd_read_file(dfpred)
    assert dfpred[[ "ner_list", "pred_ner_list"  ]].shape


    def create_answer_from_tag(tag):
      # name=f'location={}'
      tag=sorted(tag, key=lambda x:x['start'])
      final_answer = ""
      list_location_type = []
      list_location_exclude = []
      for t in tag:
        text  =t.get('text') if 'text' in t else t.get("value")

        if t['type']not in ['location_type', 'location_type_exclude']:
          key = t['type']
          final_answer += f'{key}={text}\n'

        elif t['type'] == 'location_type':
          list_location_type.append(text)

        elif t['type'] == 'location_type_exclude':
          list_location_exclude.append(text)

      if len(list_location_type):
        text = " and ".join(list_location_type)
        final_answer += f'location_type={text}\n'

      if len(list_location_exclude):
        text = " and ".join(list_location_exclude)
        final_answer += f'list_location_exclude={text}\n'
      return final_answer

    #####  Generate nornalized answer from tag
    dfpred['text_true_str'] = dfpred["ner_list"].apply(create_answer_from_tag)
    dfpred['text_pred_str'] = dfpred["pred_ner_list"].apply(create_answer_from_tag)

    pd_to_file(dfpred, dirout + '/dfpred_text_generated.parquet', show=1)



def dataXX_fun_answer_clean(ss:str):
  ss = ss.replace("search_places(", "")
  return ss


######################################################################################




####################################################################################
####### Google colab ###############################################################
def init_googledrive(shortcut="phi2"):
    import os
    from google.colab import drive
    drive.mount('/content/drive')
    os.chdir(f"/content/drive/MyDrive/{shortcut}/")
    # ! ls .
    #! pwd
    #! ls ./traindata/
    #ls








########################################################################################
##################### Data Validator ################################################
def nerdata_validate_dataframe(df):
    assert df[["text", "ner_list" ]].shape
    rowset = set(df[ "ner_list"].values[0][0].keys())
    assert rowset == {"start", "end", "type", "value"}, f"error {rowset}"


def nerdata_validate_row(x:Union[list, dict], cols_ref=None):
    """Check format of NER records.
    Args:
        x (Union[list, dict]):     NER records to be checked. list of dict or a single dict.
        cols_ref (set, optional):  reference set of columns to check against. 

    Raises:
        AssertionError: If NER records do not contain all required columns.

    Returns:
        bool: True if format of NER records is valid.
    """

    cols_ref = {'start', 'value', 'type'} if cols_ref is None else set(cols_ref)

    if isinstance(x, list):
        ner_records = set(x[0].keys())
        assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

    elif isinstance(x, dict):
        ner_records = set(x.keys())
        assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

    return True


def test_nerdata():
    # Example usage of NERdata class

    # Define a list of tags
    tags = ['person', 'organization', 'location']

    # Create an instance of NERdata class
    ner_data = NERdata(tag_list=tags)
    log(ner_data.NCLASS, ner_data.N_BOI, ner_data.L2I, ner_data.I2L)
    data = {
        'text': ["John lives in New York.", "Google is based in California."],
        'pred_ner_list': [[0, 6, 6, 6, 6, 2, 5], [4, 6, 6, 6, 6, 5, 6]]
    }
    df = pd.DataFrame(data)

    # Example offset mapping
    offset_mapping = [
        [[(0, 4), (5, 10), (11, 13), (14, 17), (18, 20), (21, 22)]],
        [[(0, 6), (7, 9), (10, 12), (13, 15), (16, 18), (19, 29), (29, 29)]]
    ]
    # Convert predicted classes into span records for NER
    ner_records = ner_data.pd_convert_ner_to_records(df, offset_mapping)
    df['ner_list'] = ner_records
    log((ner_records))

    # Validate DataFrame
    ner_data.nerdata_validate_dataframe(df)

    # Validate a single row
    ner_data.nerdata_validate_row(ner_records[0])


    # Get class name from class index
    class_name = ner_data.get_class(1)
    print(f"Class name for index 1: {class_name}")

    # Create mapping dictionaries
    print(f"Label to Index mapping: {ner_data.L2I}")
    print(f"Index to Label mapping: {ner_data.I2L}")

    # Convert predictions to span records for a single row
    row_df = {
        'text': "John lives in New York.",
        'offset_mapping': [[(0, 4), (5, 10), (11, 13), (14, 17), (18, 21), (22, 24), (25, 28), (29, 33)]]
    }
    pred_list = [0, 1, 2, 0, 0, 0, 3, 0]
    span_record = ner_data.pred2span(pred_list, row_df)
    print(f"Span record: {span_record}")


class NERdata(object):
    def __init__(self, tag_list, token_BOI=None):
        """ Utils to normalize NER data for pandas dataframe


            Args:
                tag_list (list): A list of tags. If not provided, a default list of tags is used.
                token_BOI (list): A list of token BOI values. If not provided, a default list of token BOI values is used.
            Info:

                    - text (str): text.
                    - ner_list (list): List of named entity records. Each named entity record is a dictionary with following keys:
                        - type (str)            : type of named entity.
                        - predictionstring (str): predicted string for named entity.
                        - start (int)           : start position of named entity.
                        - end (int)             : end position of named entity.
                        - text (str)            : text of named entity.
            Append dix;
                    - default list of tags is: ['location', 'city', 'country', 'location_type', 'location_type_exclude']
        """
        #### Class
        tags0 = ['location', 'city', 'country', 'location_type', 'location_type_exclude']
        
        #### We will logging warnning for user when they're using default tag list 
        if tag_list is None:
            log(f"You're using default tag list inside NERdata.", tags0)
         
        self.tag_list = tag_list if tag_list is not None else tags0


        # self.NCLASS       = len(self.tag) # Gpy40 make a mistake here 
        self.NCLASS       = len(self.tag_list)

        #### B-token am I-token, "other" as NA field
        #### We should make sure client provide exactly token_BOI with size 3.
        #### First for begin of words, second for inside and last for other-word.
        token_BOI   = ["B", "I", "Other"]         if token_BOI is None else token_BOI
        if len(token_BOI) != 3:
            log(f"Please use exactly name of token POI with size 3 for Begin, Inside and other word")
            self.token_BOI = ["B", "I", "Other"] 
            
        self.token_BOI = token_BOI
        self.N_BOI  = len(token_BOI) - 1

        ### Number of classes for model : B-token, I-token, O-End, + "Other"
        self.NCLASS_BOI = self.NCLASS * self.N_BOI + 1

        ### Dict mapping ############################### 
        self.L2I = {}      ## Label to Index
        self.I2L = {}      ## Index to Label

        L2I, I2L, NCLASS = self.create_map_dict()


        ### NER record template for data validation
        self.ner_dataframe_cols = ['text', 'ner_list']
        self.ner_fields = ["start", "end", "type", "value"]


    def create_map_dict(self,):        
        NCLASS= self.NCLASS

        begin_of_word = self.token_BOI[0]
        inside_of_word = self.token_BOI[1]
        other_word = self.token_BOI[2]
        ### Dict mapping: Label --> Index        
        L2I = {}
        for index, c in enumerate(self.tag_list):
            L2I[f'{begin_of_word}-{c}'] = index
            L2I[f'{inside_of_word}-{c}'] = index + NCLASS
        L2I[other_word] = NCLASS*2
        L2I['Special'] = -100
        L2I

        ### Dict mapping: Index ---> Label       
        I2L = {}
        for k, v in L2I.items():
            I2L[v] = k
        I2L[-100] = 'Special'

        I2L = dict(I2L)
        log(I2L)

        self.L2I = L2I
        self.I2L = I2L

        return L2I, I2L, NCLASS


    def get_class(self, class_idx:int):
        if class_idx == self.NCLASS_BOI - 1: 
            return self.token_BOI[2]
        else: 
            # Gpt4o make a mistake here: I2L --> self.I2L
            return self.I2L[class_idx].replace(self.token_BOI[0], "").replace(self.token_BOI[1], "").replace("-", "")


    def pred2span(self, pred_list, row_df, test=False):

        n_tokens = len(row_df['offset_mapping'][0])
        classes = []
        all_span = []
        log(row_df, pred_list, len(pred_list), n_tokens)
        # Gpt4o make a mistake here: pred_list is a list or numpy array 
        pred_list = pred_list.tolist() if hasattr(pred_list, "tolist") else pred_list

        for i, c in enumerate(pred_list):
            if i == n_tokens:
                # If we go to end of sentence but for another reason maybe padding, etc so pred_list 
                # often longger than n_tokens
                break
            if i == 0:
                cur_span = list(row_df['offset_mapping'][0][i])
                classes.append(self.get_class(c))
            elif i > 0 and c-self.NCLASS == pred_list[i-1]:
                # We will go to next-token for current span: B-, I-, I-, I- 
                # Note: index_of_inside_word - NCLASS ===  index_of_begin_word 
                cur_span[1] = row_df['offset_mapping'][0][i][1]
            else:
                all_span.append(cur_span)
                cur_span = list(row_df['offset_mapping'][0][i])
                classes.append(self.get_class(c))
        all_span.append(cur_span)

        text = row_df["text"]
        
        # map token ids to word (whitespace) token ids
        predstrings = []
        for span in all_span:
            span_start  = span[0]
            span_end    = span[1]
            before      = text[:span_start]
            token_start = len(before.split())
            if len(before) == 0:    token_start = 0
            elif before[-1] != ' ': token_start -= 1

            num_tkns   = len(text[span_start:span_end+1].split())
            tkns       = [str(x) for x in range(token_start, token_start+num_tkns)]
            predstring = ' '.join(tkns)
            predstrings.append(predstring)

        #### Generate Record format 
        row   = {  "text": text, "ner_list": []}
        llist = []
        for ner_type, span, predstring in zip(classes, all_span, predstrings):
            if ner_type!=self.token_BOI[2]: # token_BOI[2] == 'Other word'
              e = {
                'type' : ner_type,
                'value': predstring,
                'start': span[0],
                'end'  : span[1],
                'text' : text[span[0]:span[1]]
              }
              llist.append(e)
        row["ner_list"] = llist
    
        return row


    def pd_convert_ner_to_records(self, df_val:pd.DataFrame, offset_mapping: list,
                                col_nerlist="pred_ner_list", col_text="text")->pd.DataFrame:
        """Convert predicted classes into span records for NER.
        Args:
            df_val (pd.DataFrame): DataFrame containing input data. It should have following columns:
                - col_nerlist (str): Column name for predicted classes.
                - col_text (str): Column name for text.
            offset_mapping (list): List of offset mappings.

        Returns:
            list: List of span records for NER. Each span record is a dictionary with following keys:
                - text (str): text.
                - ner_list (list): List of named entity records. Each named entity record is a dictionary with following keys:
                    - type (str)            : type of named entity.
                    - predictionstring (str): predicted string for named entity.
                    - start (int)           : start position of named entity.
                    - end (int)             : end position of named entity.
                    - text (str)            : text of named entity.

        """
        #### Convert
        pred_class = df_val[col_nerlist].values
        valid      = df_val[[col_text]]
        valid['offset_mapping'] = offset_mapping
        valid = valid.to_dict(orient="records")

        ### pred_class : tuple(start, end, string)
        predicts= [self.pred2span(pred_class[i], valid[i]) for i in range(len(valid))]

        # df_val["ner_list_records"] = [row['ner_list'] for row in predicts]
        
        return [row['ner_list'] for row in predicts]


    def nerdata_validate_dataframe(self, df):
        assert df[["text", "ner_list" ]].shape
        rowset = set(df[ "ner_list"].values[0][0].keys())
        assert rowset.issuperset({"start", "end", "type", "value"}), f"error {rowset}"


    def nerdata_validate_row(self, x:Union[list, dict], cols_ref=None):
        """Check format of NER records.
        Args:
            x (Union[list, dict]):     NER records to be checked. list of dict or a single dict.
            cols_ref (set, optional):  reference set of columns to check against. 
        """

        cols_ref = {'start', 'value', 'type'} if cols_ref is None else set(cols_ref)

        if isinstance(x, list):
            ner_records = set(x[0].keys())
            assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

        elif isinstance(x, dict):
            ner_records = set(x.keys())
            assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

        return True










########################################################################################
##################### Tokenizer helper ################################################
def token_fix_beginnings(labels, NCLASS):
    """Fix   beginning of a list of labels by adjusting   labels based on certain conditions.
    Args:
        labels (list): A list of labels.        
    # tokenize and add labels    
    """
    for i in range(1,len(labels)):
        curr_lab = labels[i]
        prev_lab = labels[i-1]
        if curr_lab in range(NCLASS,NCLASS*2):
            if prev_lab != curr_lab and prev_lab != curr_lab - NCLASS:
                labels[i] = curr_lab -NCLASS
    return labels



def tokenize_and_align_labels(examples:dict, tokenizer,  L2I:dict, token_BOI: list):
    """Tokenizes  given examples and aligns  labels.
    Args:
        examples (dict): A dictionary containing  examples to be tokenized and labeled.
            - "text" (str):  query string to be tokenized.
            - "ner_list" (list): A list of dictionaries representing  entity tags.
                Each dictionary should have  following keys:
                - 'start' (int):  start position of  entity tag.
                - 'end' (int):  end position of  entity tag.
                - 'type' (str):  type of  entity tag.

    Returns:
        dict: A dictionary containing  tokenized and labeled examples.
            It has  following keys:
            - 'input_ids' (list): A list of input ids.
            - 'attention_mask' (list): A list of attention masks.
            - 'labels' (list): A list of labels.
            - 'token_type_ids' (list, optional): A list of token type ids. Only present if 'token_type_ids' is present in  input dictionary.
    """

    o = tokenizer(examples["text"],
                  return_offsets_mapping=True,
                  return_overflowing_tokens=True)
    offset_mapping = o["offset_mapping"]
    o["labels"] = []
    NCLASS = (len(L2I) - 1) // 2
    for i in range(len(offset_mapping)):
        labels = [L2I[token_BOI[2]] for i in range(len(o['input_ids'][i]))]
        for tag in examples["ner_list"]:
            label_start = tag['start']
            label_end = tag['end']
            label = tag['type']
            for j in range(len(labels)):
                token_start = offset_mapping[i][j][0]
                token_end = offset_mapping[i][j][1]
                if token_start == label_start:
                    labels[j] = L2I[f'{token_BOI[0]}-{label}']
                if token_start > label_start and token_end <= label_end:
                    labels[j] = L2I[f'{token_BOI[1]}-{label}']

        for k, input_id in enumerate(o['input_ids'][i]):
            if input_id in [0,1,2]:
                labels[k] = -100

        labels = token_fix_beginnings(labels, NCLASS)

        o["labels"].append(labels)

    o['labels']         = o['labels'][0]
    o['input_ids']      = o['input_ids'][0]
    o['attention_mask'] = o['attention_mask'][0]
    if 'token_type_ids' in o:o['token_type_ids'] = o['token_type_ids'][0]
    return o



@dataclass
class DataCollatorForLLM:
    tokenizer         : PreTrainedTokenizerBase
    padding           : Union[bool, str, PaddingStrategy] = True
    max_length        : Optional[int] = None
    pad_to_multiple_of: Optional[int] = None

    def __call__(self, features):
        label_name        = 'label' if 'label' in features[0].keys() else 'labels'
        labels            = [feature.pop(label_name) for feature in features]
        max_length_labels = max([len(i) for i in labels])
        labels_pad        = np.zeros((len(labels), max_length_labels, )) + -100
        for index in range(len(labels)):
#             print(len(labels[index]), labels[index])
            labels_pad[index, : len(labels[index])] = labels[index]

        batch_size         = len(features)
        flattened_features = features
        batch = self.tokenizer.pad(
            flattened_features,
            padding            = self.padding,
            max_length         = self.max_length,
            pad_to_multiple_of = self.pad_to_multiple_of,
            return_tensors     = 'pt',
        )
        batch['labels'] = torch.from_numpy(labels_pad).long()

        return batch




#################################################################################
######################## Train ##################################################
def run_train(cfg=None, cfg_name="ner_deberta", dirout="./ztmp/exp", istest=1):
    """ 
       python nlp/ner/ner_deberta.py run_train  --dirout ztmp/exp   --cfg config/traina/train1.yaml --cfg_name ner_deberta

    """
    global NCLASS, L2I, I2L    
    log("###### Config Load   #############################################")
    cfg0 = config_load(cfg)
    cfg0 = cfg0.get(cfg_name, None) if cfg0 is not None else None


    log("###### User Params   #############################################")
    cc = Box()
    cc.model_name='microsoft/deberta-v3-base'

    #### Data name
    cc.dataloader_name = "dataXX_load_prepro"  ## Function name
    cc.datamapper_name = "dataXX_create_label_mapper"  ## Function name

    cc.n_train = 5  if istest == 1 else 1000000000
    cc.n_val   = 2  if istest == 1 else 1000000000

    #### Train Args
    aa = Box({})
    aa.output_dir                  = f"{dirout}/log_train"
    aa.per_device_train_batch_size = 64
    aa.gradient_accumulation_steps = 1
    aa.optim                       = "adamw_hf"
    aa.save_steps                  = min(100, cc.n_train-1)
    aa.logging_steps               = min(50,  cc.n_train-1)
    aa.learning_rate               = 1e-5
    aa.max_grad_norm               = 2
    aa.max_steps                   = -1
    aa.num_train_epochs            = 1
    aa.warmup_ratio                = 0.2 # 20%  total step warm-up
    # lr_schedulere_type='constant'
    aa.evaluation_strategy = "epoch"
    aa.logging_strategy    = "epoch"
    aa.save_strategy       = "epoch"
    cc.hf_args_train = copy.deepcopy(aa)

    ### HF model
    cc.hf_args_model = {}
    cc.hf_args_model.model_name = cc.model_name
    cc.hf_args_model.num_labels = NCLASS*2+1 ## due to BOI notation

    #### Override by Yaml config  #####################################
    cc = exp_config_override(cc, cfg0, cfg, cfg_name)


    log("###### Experiment Folder   #######################################")
    cc = exp_create_exp_folder(task="ner_deberta", dirout=dirout, cc=cc)
    log(cc.dirout)
    del dirout


    log("###### Model : Training params ##############################")
    args = TrainingArguments( ** dict(cc.hf_args_train))


    log("###### Data Load   #############################################")
    from utilmy import load_function_uri
    ### dataXX_load_prepro()  , dataXX_create_label_mapper()
    dataloader_fun = load_function_uri(cc.dataloader_name, globals())
    datamapper_fun = load_function_uri(cc.datamapper_name, globals())

    df, df_val       = dataloader_fun()  ## = 
    taglist = getattr(cc, 'taglist', ['location', 'city', 'country', 'location_type', 'location_type_exclude'])
    ner_dataset = NERdata(tag_list=taglist)
    cc.hf_args_model.num_labels = ner_dataset.NCLASS*2+1 ## due to BOI notation
    
    columns = df.columns.tolist()
    df, df_val = df.iloc[:cc.n_train], df_val.iloc[:cc.n_val]


    cc.data ={}
    cc.data.cols          = columns
    cc.data.cols_required = ["text", "ner_list" ]
    cc.data.ner_format    = ["start", "end", "type", "value"]  
    cc.data.cols_remove   = ['overflow_to_sample_mapping', 'offset_mapping', ] + columns
    cc.data.L2I           = ner_dataset.L2I     ### label to Index Dict
    cc.data.I2L           = ner_dataset.I2L     ### Index to Label Dict
    cc.data.nclass        = ner_dataset.NCLASS  ### Number of NER Classes.

    ner_dataset.nerdata_validate_dataframe(df)
    ner_dataset.nerdata_validate_dataframe(df_val)    


    ################# Generic Code ###########################################  
    log("###### Dataloader setup  ############################################")
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
    tokenizer.pad_token = tokenizer.eos_token

    assert set(df[ "ner_list"].values[0][0].keys()) == {"start", "end", "type", "value"}
    ds_train = Dataset.from_pandas(df)
    ds_train = ds_train.map(tokenize_and_align_labels, fn_kwargs={'tokenizer': tokenizer, "L2I": ner_dataset.L2I, "token_BOI": ner_dataset.token_BOI})
    dataset_train = ds_train.remove_columns(['overflow_to_sample_mapping', 'offset_mapping', ] + columns)


    assert set(df_val[ "ner_list"].values[0][0].keys()) == {"start", "end", "type", "value"}
    ds_valid   = Dataset.from_pandas(df_val)
    ds_valid   = ds_valid.map(tokenize_and_align_labels, fn_kwargs={'tokenizer': tokenizer, "L2I": ner_dataset.L2I, "token_BOI": ner_dataset.token_BOI})
    offset_mapping = ds_valid['offset_mapping']
    dataset_valid = ds_valid.remove_columns(['overflow_to_sample_mapping', 'offset_mapping',]+ columns)


    batch = DataCollatorForLLM(tokenizer)([dataset_train[0], dataset_train[1]])
    log(dataset_valid[0])
    log(batch)


    log("######### Model : Init #########################################")
    model = AutoModelForTokenClassification.from_pretrained(cc.model_name, 
                               num_labels= cc.hf_args_model.num_labels)

    # for i in model.deberta.parameters():
    #   i.requires_grad=False
    
    log("######### Model : Training start ##############################")
    trainer = Trainer(model, args,
        train_dataset= dataset_train,
        eval_dataset = dataset_valid,
        data_collator= DataCollatorForLLM(tokenizer),
        tokenizer    = tokenizer,
        compute_metrics=partial(metrics_calc_callback_train, I2L=ner_dataset.I2L, L2I=ner_dataset.L2I),
    )

    json_save(cc, f'{cc.dirout}/config.json')
    trainer_output = trainer.train()
    trainer.save_model( f"{cc.dirout}/model")

    cc['metrics_trainer'] = trainer_output.metrics
    json_save(cc, f'{cc.dirout}/config.json', show=1)


    log("######### Model : Eval Predict  ######################################")
    preds_proba, labels, _ = trainer.predict(dataset_valid)
    
    df_val                 = pd_predict_format(df_val, preds_proba, labels, offset_mapping, ner_dataset)
    assert df_val[[  "pred_proba", "pred_class", "pred_ner_list"     ]].shape


    log("######### Model : Eval Metrics #######################################")    
    assert df_val[[ "text", "ner_list", "pred_ner_list"     ]].shape
    df_val = metrics_calc_full(df_val,)

    pd_to_file(df_val, f'{cc.dirout}/dfval_pred_ner.parquet', show=1)  


def pd_predict_format(df_val:pd.DataFrame, preds_proba:list, labels:list, 
                      offset_mapping: list, ner_dataset:NERdata)->pd.DataFrame:
    """ preds_proba: (batch, seq, NCLASS*2+1)    [-3.52225840e-01  5.51

        labels:      (batch,seq)  [[-100   10   10   10   10    3   5    5   10   10 -100 -100]
                                   [-100   10   10   10   10     10   10 -100]]
        pred_class: (batch, seq)  [[ 6  3  6 10 10 10 10 10  4 10 10  4 10  5  4 4]
                                   [ 6  6  6  4 10 10  1 10 10  2  2 10 10 0 10  5]]

        'pred_ner_list_records':
          [{ 'start': 0, 'end': 1, 'type': 'ORG', value : "B-ORG"},   ]

            pred_ner_list_records
            List<Struct<{end:Int64, predictionstring:String, start:Int64, text:String, type:String}>>

            accuracy
            Struct<{city:Float64, country:Float64, location:Float64, location_type:Float64, total_acc:Float64}>          

    """
    pred_class            = np.argmax(preds_proba, axis=-1)
    log("pred_proba: ", str(preds_proba)[:50],)
    log("labels: ",     str(labels)[:50]      )
    log("pred_class: ", str(pred_class)[:50] )

    df_val['pred_proba'] = np_3darray_into_2d(preds_proba) 
    df_val['pred_class'] = list(pred_class) ### 2D array into List of List  ## ValueError: Expected a 1D array, got an array with shape (2, 25)

    ### Need to convert into (start, end, tag) record format
    df_val['pred_ner_list'] = df_val['pred_class'].apply(lambda x : x)   
    # df_val['preds_labels'] = labels

    df_val['pred_ner_list_records'] = ner_dataset.pd_convert_ner_to_records(df_val, offset_mapping)
    return df_val



def pd_predict_convert_ner_to_records(df_val:pd.DataFrame, offset_mapping: list,
                                       col_nerlist="pred_ner_list", col_text="text")->pd.DataFrame:
    """Convert predicted classes into span records for NER.

    Args:
        df_val (pd.DataFrame): DataFrame containing input data. It should have following columns:
            - col_nerlist (str): Column name for predicted classes.
            - col_text (str): Column name for text.
        offset_mapping (list): List of offset mappings.

    Returns:
        list: List of span records for NER. Each span record is a dictionary with following keys:
            - text (str): text.
            - ner_list (list): List of named entity records. Each named entity record is a dictionary with following keys:
                - type (str)            : type of named entity.
                - predictionstring (str): predicted string for named entity.
                - start (int)           : start position of named entity.
                - end (int)             : end position of named entity.
                - text (str)            : text of named entity.

    """
    # print(df_val)
    # assert df_val[[ "text", "input_ids", "offset_mapping", "pred_ner_list"  ]]
    def get_class(c):
        if c == NCLASS*2: return 'Other'
        else: return I2L[c][2:]

    def pred2span(pred_list, df_row, viz=False, test=False):
        #     example_id = example['id']
        n_tokens = len(df_row['offset_mapping'][0])
        #     print(n_tokens, len(example['offset_mapping']))
        classes = []
        all_span = []
        for i, c in enumerate(pred_list.tolist()):
            if i == n_tokens-1:
                break
            if i == 0:
                cur_span = df_row['offset_mapping'][0][i]
                classes.append(get_class(c))
            elif i > 0 and (c == pred_list[i-1] or (c-NCLASS) == pred_list[i-1]):
                cur_span[1] = df_row['offset_mapping'][0][i][1]
            else:
                all_span.append(cur_span)
                cur_span = df_row['offset_mapping'][0][i]
                classes.append(get_class(c))
        all_span.append(cur_span)

        text = df_row["text"]
        
        # map token ids to word (whitespace) token ids
        predstrings = []
        for span in all_span:
            span_start  = span[0]
            span_end    = span[1]
            before      = text[:span_start]
            token_start = len(before.split())
            if len(before) == 0:    token_start = 0
            elif before[-1] != ' ': token_start -= 1

            num_tkns   = len(text[span_start:span_end+1].split())
            tkns       = [str(x) for x in range(token_start, token_start+num_tkns)]
            predstring = ' '.join(tkns)
            predstrings.append(predstring)

        #### Generate Record format 
        row = {  "text": text, "ner_list": []}
        es = []
        for ner_type, span, predstring in zip(classes, all_span, predstrings):
            if ner_type!='Other':
              e = {
                'type' : ner_type,
                'value': predstring,
                'start': span[0],
                'end'  : span[1],
                'text' : text[span[0]:span[1]]
              }
              es.append(e)
        row["ner_list"] = es
    
        return row


    #### Convert
    pred_class = df_val[col_nerlist].values
    valid      = df_val[[col_text]]
    valid['offset_mapping'] = offset_mapping
    valid = valid.to_dict(orient="records")

    ### pred_class : tuple(start, end, string)
    predicts= [pred2span(pred_class[i], valid[i]) for i in range(len(valid))]

    return [row['ner_list'] for row in predicts]


    #pd_to_file( predicts, dirout + '/predict_ner_visualize.parquet' )
    # pred = pd.read_csv("nguyen/20240215_171305/predict.csv")
    # pred
    # pred = pred[["text", "ner_list"]]
    # eval(pred.ner_tag.iloc[0])
    # pred["ner_list"] = pred["ner_list"].apply(eval)


def np_3darray_into_2d(v3d):
    """ Required to save 3d array in parquet format


    """ 
    shape = v3d.shape
    v2d = np.empty((shape[0], shape[1]), dtype=str)

    for i in range(shape[0]):
        for j in range(shape[1]):
            vstr    = ",".join(map(str, v3d[i,j,:]))
            v2d[i,j]= vstr
    return list(v2d)




################################################################################
########## Run Inference  ######################################################
def run_infer(cfg:str=None, dirmodel="ztmp/models/gliner/small", 
                cfg_name    = "ner_gliner_predict",
                dirdata     = "ztmp/data/text.csv",
                coltext     = "text",
                dirout      = "ztmp/data/ner/predict/",
                multi_label = 0,
                threshold   = 0.5
                  ):
  """Run prediction using a pre-trained  Deberta model.

    ### Usage
      export pyner="python nlp/ner/ner_deberta.py "

      pyner run_infer --dirmodel "./ztmp/exp/20240520/235015/model_final/"  --dirdata "ztmp/data/ner/deberta"  --dirout ztmp/out/ner/deberta/

      pyner run_infer --cfg config/train.yaml     --cfg_name "ner_deberta_infer_v1"


    Output:


  Parameters:
      cfg (dict)    : Configuration dictionary (default is None).
      dirmodel (str): path of pre-trained model 
      dirdata (str) : path of input data 
      coltext (str) : Column name of text
      dirout (str)  : path of output data 


  #log(model.predict("My name is John Doe and I love my car. I bought a new car in 2020."))

  """
  cfg0 = config_load(cfg,)
  cfg0 = cfg0.get(cfg_name, None) if isinstance(cfg0, dict) else None

  ner_tags    = ["person", "city", "location", "date", "actor", ]
  if  isinstance( cfg0, dict) : 
    if "ner_tags" in cfg0: 
        ner_tags = cfg0["ner_tags"]
    log("ner_tags:", str(ner_tags)[:100] )

    dirmodel = cfg0.get("dirmodel", dirmodel)
    dirdata  = cfg0.get("dirdata",  dirdata)
    dirout   = cfg0.get("dirout",   dirout)

  multi_label = False if multi_label==0 else True

  model = AutoModelForTokenClassification.from_pretrained(dirmodel,)
  log(str(model)[:10])
  model.eval()

  flist = exp_get_filelist(dirdata)
  for ii,fi in enumerate(flist) :
     df = pd_read_file(fi)
     log(ii, fi,  df.shape)
     #df["ner_list_pred"] = df[coltext].apply(lambda x: model.predict(x, flat_ner=True, threshold=0.5, multi_label=False))
     df["ner_list_pred"] = df[coltext].apply(lambda xstr: model.predict_entities(xstr, 
                                               labels= ner_tags, threshold=threshold,
                                               multi_label=multi_label))

     pd_to_file(df, dirout + f"/df_predict_ner_{ii}.parquet", show=1)



def run_text_generator_from_tag(dirin, dirout):
    #### Generate answer/text from TAG
    pass 



################################################################################
########## Metrics Helper    ###################################################
def metrics_calc_callback_train(p, L2I, I2L):

    metric = datasets.load_metric("seqeval")
    preds, labels = p
    preds = np.argmax(preds, axis=2)

    # Remove ignored index (special tokens)
    true_preds = [
        [I2L[p] for (p, l) in zip(pred, label) if l != -100]
        for pred, label in zip(preds, labels)
    ]
    true_labels = [
        [I2L[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(preds, labels)
    ]

    results = metric.compute(predictions=true_preds, references=true_labels)
    
    #return results
    return {
        "precision": results["overall_precision"],
        "recall"   : results["overall_recall"],
        "f1"       : results["overall_f1"],
        "accuracy" : results["overall_accuracy"],
    }



def metrics_calc_full(df_val,):
    #### Error due : Need to conver ner_list into  {start, end, tag} format
    log( metrics_ner_accuracy(df_val["ner_list"].iloc[0], df_val['pred_ner_list_records'].iloc[0]) )    
    df_val['accuracy'] = df_val.apply(lambda x: metrics_ner_accuracy(x["ner_list"], 
                                                                     x['pred_ner_list_records']),axis=1 )
    return df_val



def metrics_ner_accuracy(tags_true:list, tags_pred:list):
    """Calculate   accuracy metric for NER (NER) task.
    Args:
        tags (List[Dict]): List of dict  ground truth tags.
                            contains   'start' index, 'value', and 'type' of a tag.

        preds (List[Dict]): List of dict predicted tags.
                            contains   'start' index, 'text', and 'type' of a tag.

    Returns: Dict:   accuracy metric for each tag type

    """
    nerdata_validate_row(tags_true, cols_ref=['start', 'value', 'type'])
    nerdata_validate_row(tags_pred, cols_ref=['start', 'value', 'type'])

    ### Sort by starting indices
    tags_true = sorted(tags_true, key= lambda x: x['start'])
    tags_pred = sorted(tags_pred, key= lambda x: x['start'])

    acc = {}
    acc_count = {}
    for tag in tags_true:
        value_true = tag['value'] ## NER value 
        type_true  = tag['type']  ## NER column name

        if type_true not in acc:
            acc[type_true]       = 0
            acc_count[type_true] = 0

        acc_count[type_true] += 1

        for pred in tags_pred:
           if pred['type'] == type_true and pred['value'].strip() == value_true.strip():
              acc[type_true ]+= 1

    total_acc   = sum(acc.values()) / sum(acc_count.values())
    metric_dict = {"accuracy": {tag: v/acc_count[tag] for tag, v in acc.items() } }

    metric_dict['accuracy_total'] = total_acc
    return metric_dict





################################################################################
########## Eval with Visualization Truth   #####################################
def eval_visualize_tag(dfpred=Union[str, pd.DataFrame], dirout="./ztmp/metrics/", ner_colors_dict=None):
    """ Visualizes   predicted tags for a given dataset of NER tasks.

    python nlp/ner_deberta.py --dfpred "./ztmp/exp/ner_train/dfpred_ner.parquet"    --dirout "./ztmp/exp/ner_train/"

    dfpred[[ "pred_class", "input_ids", "offset_mapping", "text"  ]]

    Args:
        dfpred (Union[str, pd.DataFrame]):   path to   CSV file containing   predicted tags or a Pandas DataFrame with   predicted tags. Default is None.
        dirout (str):   directory where   output file will be saved. Default is './ztmp/metrics/'.
        ner_colors_dict (dict): A dictionary mapping entity types to colors. Default is None.

    """ 
    if isinstance(dfpred, str):
        dfpred = pd_read_file(dfpred)

    assert dfpred[[ "text", "input_ids", "offset_mapping", "pred_ner_list"  ]]

    if ner_colors_dict is None:
        ner_colors_dict = {'location': '#8000ff',
                    'city': '#2b7ff6',
                    'country': '#2adddd',
                    'location_type': '#80ffb4',
                    'location_type_exclude': 'd4dd80',
                    'Other': '#007f00',}

    pred_class = dfpred['pred_ner_list'].values
    valid      = dfpred[[ "input_ids", "offset_mapping", "text"  ]].to_dict(orient="records")


    def get_class(c):
        if c == NCLASS*2: return 'Other'
        else: return I2L[c][2:]

    def pred2span(pred, example, viz=False, test=False):
        #     example_id = example['id']
        n_tokens = len(example['input_ids'])
        #     print(n_tokens, len(example['offset_mapping']))
        classes = []
        all_span = []
        for i, c in enumerate(pred.tolist()):
            if i == n_tokens-1:
                break
            if i == 0:
                cur_span = example['offset_mapping'][0][i]
                classes.append(get_class(c))
            elif i > 0 and (c == pred[i-1] or (c-NCLASS) == pred[i-1]):
                cur_span[1] = example['offset_mapping'][0][i][1]
            else:
                all_span.append(cur_span)
                cur_span = example['offset_mapping'][0][i]
                classes.append(get_class(c))
        all_span.append(cur_span)

        text = example["text"]

        # map token ids to word (whitespace) token ids
        predstrings = []
        for span in all_span:
            span_start  = span[0]
            span_end    = span[1]
            before      = text[:span_start]
            token_start = len(before.split())
            if len(before) == 0:    token_start = 0
            elif before[-1] != ' ': token_start -= 1

            num_tkns   = len(text[span_start:span_end+1].split())
            tkns       = [str(x) for x in range(token_start, token_start+num_tkns)]
            predstring = ' '.join(tkns)
            predstrings.append(predstring)

        row = {  "text": text, "ner_list": []}
        es = []
        for c, span, predstring in zip(classes, all_span, predstrings):
            if c!='Other':
              e = {
                'type': c,
                'predictionstring': predstring,
                'start': span[0],
                'end': span[1],
                'text': text[span[0]:span[1]]
              }
              es.append(e)
        row["ner_list"] = es

        if viz: ner_text_visualize(row)

        return row


    ##### Check Visulaize
    def ner_text_visualize2(x):
        return ner_text_visualize(x, title='ground-truth', ner_colors_dict=ner_colors_dict )

    ner_text_visualize2(valid[32])

    #### Check Values
    predicts= [pred2span(pred_class[i], valid[i], viz=False) for i in range(len(valid))]
    ner_text_visualize(predicts[0]   )
    ner_text_visualize(predicts[2]   )
    ner_text_visualize(predicts[12]  )
    ner_text_visualize(predicts[400] )
    ner_text_visualize(predicts[328] )

    predicts = pd.DataFrame(predicts)
    pd_to_file( predicts, dirout + '/predict_ner_visualize.parquet' )
    # pred = pd.read_csv("nguyen/20240215_171305/predict.csv")
    # pred
    # pred = pred[["text", "ner_list"]]
    # eval(pred.ner_tag.iloc[0])
    # pred["ner_list"] = pred["ner_list"].apply(eval)




def ner_text_visualize(row:dict, title='visualize_model-predicted', ner_refs:list=None, ner_colors_dict:list=None,
                       jupyter=True):
    """Visualizes   NER results for a given text row.
    Args:
        row (dict):  text row to visualize.
        title (str, optional):  title of   visualization. Defaults to 'visualize_model-predicted'.
        ner_refs (list, optional): A list of entity references to include in   visualization. Defaults to None.
        ner_colors_dict (dict, optional): A dictionary mapping entity references to colors. Defaults to None.
        jupyter (bool, optional): Flag indicating whether   visualization is being rendered in Jupyter Notebook. Defaults to True.

    """
    if ner_colors_dict is None:
        ner_colors_dict = {
                'location': '#8000ff',
                'city': '#2b7ff6',
                'country': '#2adddd',
                'location_type': '#80ffb4',
                'location_type_exclude': 'd4dd80',
                'Other': '#007f00',
        }

    if ner_refs is None:
       # ner_refs = ['location', 'city', 'country', 'location_type', 'location_type_exclude'] + ['Other']
       ner_refs = [ key for key in ner_colors_dict.keys() ]

    text = row["text"]
    tags = row["ner_list"]
    ents = [{'start': k['start'], 'end': k['end'], 'label': k['type']} for k in tags if k['type'] !='Other']

    doc2 = {
        "text": text,
        "ents": ents,
        "title": title
    }

    options = {"ents": ner_refs, "colors": ner_colors_dict}
    spacy.displacy.render(doc2, style="ent", options=options, manual=True, jupyter=jupyter)






################################################################################
########## Eval with embedding ground Truth  ###################################
def eval_check_with_embed(df_test, col1='gt_answer_str', col2='predict_answer_str',  dirout="./ztmp/metrics/"):
    """Evaluate   performance of a model using embeddings for ground truth and predictions.

    Args:
        df_test (pandas.DataFrame or str):   test dataset to evaluate. If a string is provided, it is assumed to be a file path and   dataset is loaded from that file.
        col1 (str, optional):   name of   column containing   ground truth answers. Defaults to 'gt_answer_str'.
        col2 (str, optional):   name of   column containing   predicted answers. Defaults to 'predict_answer_str'.
        dirout (str, optional):   directory to save   evaluation metrics. Defaults to './ztmp/metrics/'.
    """

    df_test = pd_add_embed(df_test, col1, col2, add_similarity=1, colsim ='sim')

    log( df_test['sim'].describe())
    log( df_test[[col1, col2]].sample(1))

    pd_to_file( df_test[["text", col1, col2, 'sim']],
                f'{dirout}/predict_sim_cosine.parquet') 

    cc = Box({})
    cc['metric_sim'] = df_test['sim'].describe().to_dict()
    json_save(cc, f"{dirout}/metrics_sim_cosine.json")


def qdrant_embed(wordlist, model_name="BAAI/bge-small-en-v1.5", size=128, model=None):
    """ pip install fastembed

    Docs:

         BAAI/bge-small-en-v1.5 384   0.13
         BAAI/bge-base-en       768   0.14
         sentence-transformers/all-MiniLM-L6-v2   0.09

        ll= list( qdrant_embed(['ik', 'ok']))


        ### https://qdrant.github.io/fastembed/examples/Supported_Models/
        from fastembed import TextEmbedding
        import pandas as pd
        pd.set_option("display.max_colwidth", None)
        pd.DataFrame(TextEmbedding.list_supported_models())


    """
    from fastembed.embedding import FlagEmbedding as Embedding

    if model is None:
       model = Embedding(model_name= model_name, max_length= 512)

    vectorlist = model.embed(wordlist)
    return np.array([i for i in vectorlist])


def sim_cosinus_fast(v1, v2)-> float :
   ### %timeit sim_cosinus_fast(ll[0], ll[1])  0.3 microSec
   import simsimd
   dist = simsimd.cosine(v1, v2)
   return dist


def sim_cosinus_fast_list(v1, v2) :
   ### %timeit sim_cosinus_fast(ll[0], ll[1])  0.3 microSec
   import simsimd
   vdist = []
   for x1,x2 in zip(v1, v2):
       dist = simsimd.cosine(x1, x2)
       vdist.append(dist)
   return vdist


def pd_add_embed(df, col1:str="col_text1", col2:str="col_text2", size_embed=128, add_similarity=1, colsim=None):
    """
    df=  pd_add_embed(df, 'answer', 'answerfull', add_similarity=1)
    df['sim_answer_answerfull'].head(1)


    """
    v1 = qdrant_embed(df[col1].values)
    #     return v1
    df[col1 + "_vec"] = list(v1)

    #    if col2 in df.columns:
    v1 = qdrant_embed(df[col2].values)
    df[col2 + "_vec"] = list(v1)

    if add_similarity>0:
      colsim2 = colsim if colsim is not None else f'sim_{col1}_{col2}'
      vdist   = sim_cosinus_fast_list(df[col1 + "_vec"].values, df[col2 + "_vec"].values)
      df[ colsim2 ] = vdist
    return df


def  pd_add_sim_fuzzy_score(df:pd.DataFrame, col1='answer_fmt', col2='answer_pred_clean'):
  # pip install rapidfuzz
  from rapidfuzz import fuzz
  df['dist2'] = df[[col1, col2]].apply(lambda x: fuzz.ratio( x[col1], x[col2]), axis=1)
  return df


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




""" 

###### Config Load   #############################################
Config: Loading  config/train.yaml
Config: Cannot read file config/train.yaml [Errno 2] No such file or directory: 'config/train.yaml'
Config: Using default config
{'field1': 'test', 'field2': {'version': '1.0'}}
###### User Params   #############################################
{'model_name': 'microsoft/deberta-v3-base', 'dataloader_name': 'dataXX_load_prepro', 'datamapper_name': 'dataXX_create_label_mapper', 'n_train': 5, 'n_val': 2, 'hf_args_train': {'output_dir': 'ztmp/exp/log_train', 'per_device_train_batch_size': 64, 'gradient_accumulation_steps': 1, 'optim': 'adamw_hf', 'save_steps': 4, 'logging_steps': 4, 'learning_rate': 1e-05, 'max_grad_norm': 2, 'max_steps': -1, 'num_train_epochs': 1, 'warmup_ratio': 0.2, 'evaluation_strategy': 'epoch', 'logging_strategy': 'epoch', 'save_strategy': 'epoch'}, 'hf_args_model': {'model_name': 'microsoft/deberta-v3-base', 'num_labels': 1}, 'cfg': 'config/train.yaml', 'cfg_name': 'ner_deberta_v1'}
###### Experiment Folder   #######################################
ztmp/exp/20240524/014651-ner_deberta-5
###### Model : Training params ##############################
###### Data Load   #############################################
                                                  answer  ...                                              query
0      b'{"name":"search_places","args":{"place_name"...  ...  find  kindergarten and tech startup  in  Crack...
1      b'{"name":"search_places","args":{"place_name"...  ...  This afternoon, I have an appointment to Mitsu...
2      b'{"name":"search_places","args":{"place_name"...  ...  find  train and embassy  near by  Brooklyn Bri...
3      b'{"name":"search_places","args":{"place_name"...  ...  This afternoon, I have an appointment to Nowhe...
4      b'{"name":"search_places","args":{"place_name"...  ...  This afternoon, I have an appointment to Wawa....
...                                                  ...  ...                                                ...
9997   b'{"name":"search_places","args":{"place_name"...  ...  Next week, I am going to US. show me  fashion ...
9998   b'{"name":"search_places","args":{"place_name"...  ...  Tomorrow, I am travelling to Fort Lauderdale. ...
9999   b'{"name":"search_places","args":{"place_name"...  ...   I need to visit Naples. search  portuguese re...
10000  b'{"name":"search_places","args":{"place_name"...  ...  list some   indoor cycling and speakeasy  arou...
10001  b'{"name":"search_places","args":{"place_name"...  ...  find  fabric store and driving range  in  Hors...

[10002 rows x 4 columns]
                                                 answer  ...                                              query
0     b'{"name":"search_places","args":{"place_name"...  ...  This afternoon, I have an appointment to Barde...
1     b'{"name":"search_places","args":{"place_name"...  ...  provide  college and alternative healthcare  n...
2     b'{"name":"search_places","args":{"place_name"...  ...  list some   mountain and public artwork  near ...
3     b'{"name":"search_places","args":{"place_name"...  ...  Next week, I am going to US. what are   te...
4     b'{"name":"search_places","args":{"place_name"...  ...   I need to visit Naples. give me  rest area an...
...                                                 ...  ...                                                ...
996   b'{"name":"search_places","args":{"place_name"...  ...  provide  miniature golf and field  at  Apni Ma...
997   b'{"name":"search_places","args":{"place_name"...  ...  Next week, I am going to US. what are   ba...
998   b'{"name":"search_places","args":{"place_name"...  ...   I need to visit Fort Snelling.  provide  medi...
999   b'{"name":"search_places","args":{"place_name"...  ...  Tomorrow, I am travelling to Houston.  find  t...
1000  b'{"name":"search_places","args":{"place_name"...  ...  Tomorrow, I am travelling to Madison. provide ...

[1001 rows x 4 columns]
                                              answer  ...                                           ner_list
0  b'{"name":"search_places","args":{"place_name"...  ...  [{'type': 'location', 'value': 'Cracker Barrel...
1  b'{"name":"search_places","args":{"place_name"...  ...  [{'type': 'location', 'value': 'Mitsuwa Market...
2  b'{"name":"search_places","args":{"place_name"...  ...  [{'type': 'location', 'value': 'Brooklyn Bridg...
3  b'{"name":"search_places","args":{"place_name"...  ...  [{'type': 'location', 'value': 'Nowhere', 'sta...
4  b'{"name":"search_places","args":{"place_name"...  ...  [{'type': 'location', 'value': 'Wawa', 'start'...

[5 rows x 5 columns]
{'answer': {9392: b'{"name":"search_places","args":{"place_name":"","address":"","city":"Missoula","country":"US","location_type":"tree and photographer","location_type_exclude":[],"radius":"","navigation_style":""}}'}, 'answer_fmt': {9392: "search_places(city='Missoula',country='US',location_type=['tree', 'photographer'],location_type_exclude=[])"}, 'answerfull': {9392: b'{"name":"search_places","args":{"place_name":"Washington Grizzly Stadium","address":"32 Campus Dr","city":"Missoula","country":"US","location_type":"tree and photographer","location_type_exclude":[],"radius":2,"navigation_style":"driving"}}'}, 'text': {9392: 'Next week, I am going to US. give me  tree and photographer  near by  Missoula.'}, 'ner_list': {9392: [{'type': 'city', 'value': 'Missoula', 'start': 70, 'end': 78}, {'type': 'country', 'value': 'US', 'start': 25, 'end': 27}, {'type': 'location_type', 'value': 'tree', 'start': 38, 'end': 42}, {'type': 'location_type', 'value': 'photographer', 'start': 47, 'end': 59}]}}
{0: 'B-location', 5: 'I-location', 1: 'B-city', 6: 'I-city', 2: 'B-country', 7: 'I-country', 3: 'B-location_type', 8: 'I-location_type', 4: 'B-location_type_exclude', 9: 'I-location_type_exclude', 10: 'Other', -100: 'Special'}
###### Dataloader setup  ############################################
Map: 100%|█████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 353.81 examples/s]
Map: 100%|█████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 229.00 examples/s]
You're using a DebertaV2TokenizerFast tokenizer. Please note that with a fast tokenizer, using `__call__` method is faster than using a method to encode text followed by a call to `pad` method to get a padded encoding.
{'input_ids': [1, 433, 14047, 263, 3539, 7647, 267, 56693, 24057, 2951, 4631, 4089, 80872, 260, 2], 'token_type_ids': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'attention_mask': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'labels': [-100, 10, 10, 10, 10, 3, 10, 10, 0, 5, 5, 5, 10, 10, -100]}
{'__index_level_0__': tensor([0, 1]), 'input_ids': tensor([[    1,   433, 14047,   263,  3539,  7647,   267, 56693, 24057,  2951,
          4631,  4089, 80872,   260,     2,     2,     2,     2,     2,     2,
             2,     2,     2,     2,     2],
        [    1,   329,  2438,   261,   273,   286,   299,  3198,   264, 63526,
          6608, 21289,   260,   350, 26026,   263,  4526,   441, 63526,  6608,
         21289,   267,   846,   260,     2]]), 'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0]]), 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1]]), 'labels': tensor([[-100,   10,   10,   10,   10,    3,   10,   10,    0,    5,    5,    5,
           10,   10, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100,
         -100],
        [-100,   10,   10,   10,   10,   10,   10,   10,   10,   10,    0,    5,
           10,   10,   10,   10,   10,   10,   10,   10,   10,   10,   10,   10,
         -100]])}
######### Model : Init #########################################
Some weights of DebertaV2ForTokenClassification were not initialized from model checkpoint at microsoft/deberta-v3-base and are newly initialized: ['classifier.bias', 'classifier.weight']
You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.
######### Model : Training start ##############################
{'loss': 2.7838, 'grad_norm': 27.501415252685547, 'learning_rate': 0.0, 'epoch': 1.0}                        
{'eval_loss': 2.8043107986450195, 'eval_precision': 0.0, 'eval_recall': 0.0, 'eval_f1': 0.0, 'eval_accuracy': 0.0, 'eval_runtime': 1.2255, 'eval_samples_per_second': 1.632, 'eval_steps_per_second': 0.816, 'epoch': 1.0}
100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:04<00:00,  2.99s/it^{'train_runtime': 11.2399, 'train_samples_per_second': 0.445, 'train_steps_per_second': 0.089, 'train_loss': 2.7838191986083984, 'epoch': 1.0}
100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:11<00:00, 11.26s/it]
{'model_name': 'microsoft/deberta-v3-base', 'dataloader_name': 'dataXX_load_prepro', 'datamapper_name': 'dataXX_create_label_mapper', 'n_train': 5, 'n_val': 2, 'hf_args_train': {'output_dir': 'ztmp/exp/log_train', 'per_device_train_batch_size': 64, 'gradient_accumulation_steps': 1, 'optim': 'adamw_hf', 'save_steps': 4, 'logging_steps': 4, 'learning_rate': 1e-05, 'max_grad_norm': 2, 'max_steps': -1, 'num_train_epochs': 1, 'warmup_ratio': 0.2, 'evaluation_strategy': 'epoch', 'logging_strategy': 'epoch', 'save_strategy': 'epoch'}, 'hf_args_model': {'model_name': 'microsoft/deberta-v3-base', 'num_labels': 11}, 'cfg': 'config/train.yaml', 'cfg_name': 'ner_deberta_v1', 'dirout': 'ztmp/exp/20240524/014651-ner_deberta-5', 'data': {'cols': ['answer', 'answer_fmt', 'answerfull', 'text', 'ner_list'], 'cols_required': ['text', 'ner_list'], 'ner_format': ['start', 'end', 'type', 'value'], 'cols_remove': ['overflow_to_sample_mapping', 'offset_mapping', 'answer', 'answer_fmt', 'answerfull', 'text', 'ner_list'], 'L2I': {'B-location': 0, 'I-location': 5, 'B-city': 1, 'I-city': 6, 'B-country': 2, 'I-country': 7, 'B-location_type': 3, 'I-location_type': 8, 'B-location_type_exclude': 4, 'I-location_type_exclude': 9, 'Other': 10, 'Special': -100}, 'I2L': {0: 'B-location', 5: 'I-location', 1: 'B-city', 6: 'I-city', 2: 'B-country', 7: 'I-country', 3: 'B-location_type', 8: 'I-location_type', 4: 'B-location_type_exclude', 9: 'I-location_type_exclude', 10: 'Other', -100: 'Special'}, 'nclass': 5}, 'metrics_trainer': {'train_runtime': 11.2399, 'train_samples_per_second': 0.445, 'train_steps_per_second': 0.089, 'total_flos': 63799496250.0, 'train_loss': 2.7838191986083984, 'epoch': 1.0}}
<_io.TextIOWrapper name='ztmp/exp/20240524/014651-ner_deberta-5/config.json' mode='w' encoding='UTF-8'>
######### Model : Eval Predict  ######################################
100%|██████████████████████████████████████████████████████████████████████████| 1/1 [00:01<00:00,  1.43s/it]
pred_proba:  [[[ 0.25330016 -0.47247496 -0.08278726 -0.06999959
labels:  [[-100   10   10   10   10    3   10   10    0    
pred_class:  [[ 0  2  0  2  2  0  2  2  1  2  2  2  9  2  0 10 
{'text': 'find  kindergarten and tech startup  in  Cracker Barrel Old Country Store Rialto.', 'offset_mapping': [[[0, 0], [0, 4], [5, 18], [18, 22], [22, 27], [27, 35], [36, 39], [40, 48], [48, 55], [55, 59], [59, 67], [67, 73], [73, 80], [80, 81], [0, 0]]]} [ 0  2  0  2  2  0  2  2  1  2  2  2  9  2  0 10 10 10 10 10 10 10 10 10
 10] 25 15
{'text': 'This afternoon, I have an appointment to Mitsuwa Marketplace. get  deli and resort  around  Mitsuwa Marketplace in US.', 'offset_mapping': [[[0, 0], [0, 4], [4, 14], [14, 15], [15, 17], [17, 22], [22, 25], [25, 37], [37, 40], [40, 46], [46, 48], [48, 60], [60, 61], [61, 65], [66, 71], [71, 75], [75, 82], [83, 90], [91, 97], [97, 99], [99, 111], [111, 114], [114, 117], [117, 118], [0, 0]]]} [0 0 2 0 5 2 0 2 9 2 2 2 3 0 0 0 1 2 2 2 2 8 9 0 0] 25 25
######### Model : Eval Metrics #######################################
{'accuracy': {'location_type': 0.0, 'location': 0.0, 'city': 0.0}, 'accuracy_total': 0.0}
ztmp/exp/20240524/014651-ner_deberta-5/dfval_pred_ner.parquet
                                              answer  ...                                           accuracy
0  b'{"name":"search_places","args":{"place_name"...  ...  {'accuracy': {'location_type': 0.0, 'location'...
1  b'{"name":"search_places","args":{"place_name"...  ...  {'accuracy': {'location': 0.0, 'location_type'...

[2 rows x 10 columns]
"""