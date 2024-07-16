""" Goal is to fine tuning and Inference using GLINER model.
    for ANY dataset.

    -->
       No harcoding of dataset fields,names
       Need to normalize raw NER datase into intermediat NER format:
           ["dataset_id", "dataset_cat1", "text_id",  "text", "ner_list",  "info_json" ]

       Input of model will be this parquet(  ["dataset_id",  ...,  "text", "ner_list",  "info_json" ])    

              Never change: 
                   NormalizedNER_dataset --> Preppro --> Code Train 

              Change
                 Dataset XXXX -->  NormalizedNER_dataset
                 --> Need a custom function for each dataset.


    ### Install
    pip intall gliner utilmy fire

    ### Usage
      cd asearch/
      mkdir -p ./ztmp/data/         ### ztmp is in .gitignore

      export cfg="config/train.yml"
      export dirout="./ztmp/exp"
    
      ### Test sample
         python nlp/ner/ner_gliner.py run_train --dirout "./ztmp/exp"

         python nlp/ner/ner_gliner.py run_train   --cfg_name "ner_gliner_vTEST"  --cfg $cfg    --dirout $dirout


         python nlp/ner/ner_gliner.py run_infer  --dirmodel  "./ztmp/exp/20240521/003915/model_final" --dirdata "./ztmp/data/ner/gliner/"  --cfg $cfg  --dirout ztmp/models/gliner/mymodel/


      ### Full dataset
         python nlp/ner/ner_gliner.py run_train   --cfg_name "ner_gliner_vXX"  --cfg $cfg    --dirout $dirout



  
  
   https://www.freecodecamp.org/news/getting-started-with-ner-models-using-huggingface/ 
   

   https://arxiv.org/html/2402.10573v2

"""
import warnings
warnings.filterwarnings("ignore")

import os, json, copy, pandas as pd, numpy as np
from typing import List, Dict
from box import Box

from gliner import GLiNER
import torch
from transformers import get_cosine_schedule_with_warmup

from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, config_load,
                    json_save, json_load, )
from utilmy import log

##### Local Import
from utils.util_exp import (exp_create_exp_folder, exp_config_override, exp_get_filelist
                            )

##########################################################################################################
CONFIG_DEFAULT = Box(
        num_steps        = 4,  # number of training iteration
        train_batch_size = 2,
        eval_every       = 4 // 2,   # evaluation/saving steps
        save_directory   = "./ztmp/exp/ztest/gliner/", # where to save checkpoints
        warmup_ratio     = 0.1,    # warmup steps
        device           = "cpu",
        lr_encoder       = 1e-5,   # learning rate for backbone
        lr_others        = 5e-5,   # learning rate for other parameters
        freeze_token_rep = False,  # freeze of not backbone
        
        # Parameters for set_sampling_params
        max_types          = 25,   # maximum number of entity types during training
        shuffle_types      = True, # if shuffle or not entity types
        random_drop        = True, # randomly drop entity types
        max_neg_type_ratio = 1,    # ratio of positive/negative types, 1 mean 50%/50%, 2 mean 33%/66%, 3 mean 25%/75% ...
        max_len            = 384   # maximum sentence length
  )



######Dataset ############################################################################################
NER_COLSTARGET       = ["dataset_id", "dataset_cat1", "text_id",  "text", "ner_list",  "info_json" ]
NER_COLSTARGET_TYPES = ["str", "int64"  "str", "list", "str", "str" ]





##########################################################################################################
def test1():
    def cleanup(dir):
        from glob import glob
        files = glob(os.path.join(dir, "*"))
        for f in files:
            os.remove(f)
    
    
    test_dir = "./ztmp/test"
    json = nerparquet_load_to_json_gliner(test_dir)



def test2():
    """ 
       python nlp/ner/ner_gliner.py test2

    """
    text = """
    Libretto by Marius Petipa, based on 1822 novella ``Trilby, ou Le Lutin d'Argail`` by Charles Nodier, first presented by Ballet of Moscow Imperial Bolshoi Theatre on January 25/February 6 (Julian/Gregorian calendar dates), 1870, in Moscow with Polina Karpakova as Trilby and Ludiia Geiten as Miranda and restaged by Petipa for Imperial Ballet at Imperial Bolshoi Kamenny Theatre on January 17–29, 1871 in St. Petersburg with Adèle Grantzow as Trilby and Lev Ivanov as Count Leopold.
    """

    model = GLiNER.from_pretrained("urchade/gliner_small")
    model.save_pretrained("./ztmp/model/gliner_Med")
    model2 = GLiNER.from_pretrained("./ztmp/model/gliner_Med", local_files_only=True)

    labels = ["person", "book", "location", "date", "actor", "character"]

    entities = model2.predict_entities(text, labels, threshold=0.4)

    for entity in entities:
        print(entity["text"], ":", entity["label"])


def test3():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("gliner_spacy")
    text = "This is a text about Bill Gates and Microsoft."
    doc = nlp(text)
    from spacy import displacy
    displacy.render(doc, style="ent")
    for ent in doc.ents:
       print(ent.text, ent.label_)





###########################################################################################################
####### Datalod Custom ####################################################################################
def data_conll203_load_datasplit():
    """  
    python nlp/ner/ner_gliner.py data_conll203_load_datasplit
  
    """
    dirtrain = "./ztmp/data/ner/conll2003/norm/train"
    dirval   = "./ztmp/data/ner/conll2003/norm/validation"

    d_train:dict = nerparquet_load_to_json_gliner( dirtrain, nrows=1000000)
    d_val:dict   = nerparquet_load_to_json_gliner( dirval, nrows=1000000)

    return d_train, d_val


def data_conll203_create_label_mapper(json_data):
    global NCLASS, L2I, i2L

    tag_list = set()
    for x in json_data:
        for vk in  x["ner"]:
            tag_list.add(vk[2])
    tag_list = list(tag_list)

    L2I = { tag:i for i, tag in enumerate(tag_list)}
    i2L = { i:tag for i, tag in enumerate(tag_list)}
    NCLASS = len(L2I)

    return L2I, i2L, NCLASS



def dataTEST_load_prepro():
    """  
    python nlp/ner/ner_gliner.py data_conll203_load_datasplit
  
    """
    dirtrain = "./ztmp/data/ner/gliner/sample_data.json"

    d_train:dict = json_load(dirtrain)
    d_val:dict = copy.deepcopy(d_train[:10])

    log(dirtrain)
    log(str(d_train)[:100])
    return d_train, d_val


def dataTEST_create_label_mapper(json_data):
    global NCLASS, L2I, i2L

    tag_list = set()
    for x in json_data:
        for vk in  x["ner"]:
            tag_list.add(vk[2])
    tag_list = list(tag_list)

    L2I = { tag:i for i, tag in enumerate(tag_list)}
    i2L = { i:tag for i, tag in enumerate(tag_list)}
    NCLASS = len(L2I)

    return L2I, i2L, NCLASS





########################################################################################
##################### Data Validator ###################################################
def test_nerdata():
    # Example usage of NERdata class

    # Define list of nertags
    nertags = ['person', 'organization', 'location']

    # Create an instance of NERdata class
    ner_data = NERdata(nertag_list=nertags)
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

    ner_data.nerdata_validate_dataframe(df)
    ner_data.nerdata_validate_row(ner_records[0])


    # Get class name from class index
    class_name = ner_data.get_class(1)
    log(f"Class name for index 1: {class_name}")

    # Create mapping dictionaries
    log(f"Label to Index mapping: {ner_data.L2I}")
    log(f"Index to Label mapping: {ner_data.I2L}")

    # Convert predictions to span records for single row
    row_df = {
        'text': "John lives in New York.",
        'offset_mapping': [[(0, 4), (5, 10), (11, 13), (14, 17), (18, 21), (22, 24), (25, 28), (29, 33)]]
    }
    pred_list = [0, 1, 2, 0, 0, 0, 3, 0]
    span_record = ner_data.pred2span(pred_list, row_df)
    log(f"Span record: {span_record}")


def dataDEFAULT_load_datasplit(dirin="./ztmp/data/ner/legaldoc"):
    """ Data Loader by DEFAULT for training. """ 
    df = pd_read_file(dirin + "/train", )
    log(df)
    assert df[[ "text", "ner_list"  ]].shape
    assert len(df)>1     and df.shape[1]>= 2 


    df_val = pd_read_file(dirin + "/val", )
    log(df_val)
    assert df_val[[ "text", "ner_list"  ]].shape
    assert len(df_val)>1 and df.shape[1]>= 2

    NERdata().nerdata_validate_dataframe(df, df_val)
    return df, df_val


def dataDEFAULT_load_metadict(dirmeta="./ztmp/data/ner/legaldoc/meta/meta.json"):
    """ Meta Loader by DEFAULT for training. """ 
    nerlabelEngine = NERdata(dirmeta=dirmeta)
    I2L, L2I, NLABEL_TOTAL, meta_dict =  nerlabelEngine.metadict_load(dirmeta=dirmeta)
    return nerlabelEngine, meta_dict 





def nerdata_validate_dataframe(*dflist):
    return NERdata.nerdata_validate_dataframe(*dflist)


def nerdata_validate_row(xdict_record:dict, cols_ref=None):
    """Check format of NER records.
    Args:
        x (Union[list, dict]):     NER records to be checked. list of dict or single dict.
        cols_ref (set, optional):  reference set of columns to check against. 
    Returns: bool: True if format of NER records is valid.
    """
    return NERdata.nerdata_validate_row(x=xdict_record, cols_ref=cols_ref)


class NERdata(object):
    def __init__(self,dirmeta=None, nertag_list=None, token_BOI=None):
        """ Utils to normalize NER data for pandas dataframe


            Args:
                nertag_list (list): list of tags. If not provided, default list of tags is used.
                token_BOI (list): list of token BOI values. If not provided, default list of token BOI values is used.
            Info:

                    - text (str): text.
                    - ner_list (list): List of named entity records. Each named entity record is dictionary with following keys:
                        - type (str)            : type of named entity.
                        - predictionstring (str): predicted string for named entity.
                        - start (int)           : start position of named entity.
                        - end (int)             : end position of named entity.
                        - text (str)            : text of named entity.
            Append dix;
                    - default list of tags is: ['location', 'city', 'country', 'location_type', 'location_type_exclude']
        """

        ##### dirmeta ###################################################
        self.dirmeta = dirmeta 


        #### Class #####################################################################
        tags0 = ['location', 'city', 'country', 'location_type', 'location_type_exclude']        
        if nertag_list is None:
            log(f"Using default nertag list inside NERdata.", tags0)
            self.nertag_list = tags0
        else:
            self.nertag_list = nertag_list 


        # self.NCLASS       = len(self.tag) # Gpy40 make mistake here 
        self.NCLASS       = len(self.nertag_list)


        #############################################################################
        #### B-token am I-token, "other" as NA field
        #### We should make sure client provide exactly token_BOI with size 3.
        #### First for begin of words, second for inside and last for other-word.
        token_BOI   = ["B", "I", "Other"]         if token_BOI is None else token_BOI
        if len(token_BOI) != 3:
            log(f"Please use exactly name of token POI with size 3 for Begin, Inside and other word")
            self.token_BOI = ["B", "I", "Other"] 
            
        self.token_BOI = token_BOI
        self.N_BOI  = len(token_BOI) - 1


        #############################################################################
        ### Number of classes for model : B-token, I-token, O-End, + "Other" ####
        self.NCLASS_BOI = self.NCLASS * self.N_BOI + 1

        ### Number of Labels for model : B-token, I-token, O-End, + "Other"  ####
        self.NLABEL_TOTAL = self.NCLASS*2+1 ## due to BOI notation


        ##### Dict mapping ########################################################## 
        self.L2I = {}      ## Label to Index
        self.I2L = {}      ## Index to Label
        L2I, I2L, NCLASS = self.create_map_dict()


        ##### NER record template for data validation ##############################
        self.ner_dataframe_cols = ['text', 'ner_list']
        self.ner_fields         = ["start", "end", "class", "value"]

        ##### Meta dict load
        self.meta_dict = self.metadict_init()



    def metadict_save(self, dirmeta=None):
        """ Save json mapper to meta.json
        """
        dirout2 = dirmeta if dirmeta is not None else self.dirmeta 
        dirout2 = dirout2 if ".json" in dirout2 else dirout2 + "/meta.json"
        json_save(self.meta_dict, dirout2 )
        log(dirout2)


    def metadict_load(self, dirmeta:str=None):
        """Load mapper from directory containing meta.json 
        Args: dirmeta (str, optional): directory containing meta.json
        Returns: dict containing all mapping.
        """
        from utilmy import glob_glob
        dirmeta = dirmeta if dirmeta is not None else self.dirmeta
        flist = glob_glob(dirmeta)
        flist = [ fi for fi in flist if ".json" in fi.split("/")[-1]  ]
        fi = flist[0]

        if "json" in fi.split("/")[-1].split(".")[-1]:
            with open(fi, 'r') as f:
                meta_dict = json.load(f)

            meta_dict = Box(meta_dict)
            if "meta_dict" in meta_dict.get("data", {}):
                ### Extract meta_dict from config training
                meta_dict = meta_dict["data"]["meta_dict"] 

            self.NLABEL_TOTAL = meta_dict["NLABEL_TOTAL"]
            self.I2L = { int(ii): label   for ii, label in meta_dict["I2L"].items() } ## Force encoding
            self.L2I = { label  : int(ii) for label,ii  in meta_dict["L2I"].items() }

            self.dirmeta = fi

            self.meta_dict = meta_dict
            return self.I2L, self.L2I, self.NLABEL_TOTAL, meta_dict
        else:
            log(" need meta.json")



    def metadict_init(self,):   
        dd = Box({})
        dd.nertag_list  = self.nertag_list
        dd.NCLASS       = self.NCLASS
        dd.NCLASS_BOI   = self.NCLASS_BOI
        dd.NLABEL_TOTAL = self.NLABEL_TOTAL
        dd.token_BOI    = self.token_BOI
        dd.L2I          = self.L2I
        dd.I2L          = self.I2L
        dd.ner_fields   = self.ner_fields
        dd.ner_dataframe_cols = self.ner_dataframe_cols

        self.meta_dict = dd



    def create_metadict(self,):     

        mm ={


        } 

        return mm


    def create_map_dict(self,):        
        NCLASS= self.NCLASS

        begin_of_word  = self.token_BOI[0]
        inside_of_word = self.token_BOI[1]
        other_word     = self.token_BOI[2]
        ### Dict mapping: Label --> Index        
        L2I = {}
        for index, c in enumerate(self.nertag_list):
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
            return self.I2L[class_idx].replace(self.token_BOI[0], "").replace(self.token_BOI[1], "").replace("-", "")


    def pred2span(self, pred_list, row_df, test=False):
        """ Converts list of predicted labels to spans and generates record format for each span.

        Args:
            pred_list (list or numpy.ndarray): list or numpy array of predicted labels.
            row_df (pandas.DataFrame)        : DataFrame containing text and offset_mapping columns.
            test (bool, optional)            : flag indicating whether it is in test mode. Defaults to False.

        Returns:
            dict: dictionary containing text and ner_list fields. ner_list field is list of dictionaries,
                  where each dictionary represents named entity and contains type, value, start, end, and text fields.
        """

        n_tokens = len(row_df['offset_mapping'][0])
        classes  = []
        all_span = []
        log(row_df, pred_list, len(pred_list), n_tokens)
        # Gpt4o make mistake here: pred_list is list or numpy array 
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
                "class" : ner_type,
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
            list: List of span records for NER. Each span record is dictionary with following keys:
                - text (str): text.
                - ner_list (list): List of named entity records. Each named entity record is dictionary with following keys:
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

    @staticmethod
    def nerdata_validate_dataframe(*dflist):

        for df in dflist:
           assert df[["text", "ner_list" ]].shape
           rowset = set(df[ "ner_list"].values[0][0].keys())
           assert rowset.issuperset({"start", "end", "class", "value"}), f"error {rowset}"

    @staticmethod
    def nerdata_validate_row(x:Union[list, dict], cols_ref=None):
        """Check format of NER records.
        Args:
            x (Union[list, dict]):     NER records to be checked. list of dict or single dict.
            cols_ref (set, optional):  reference set of columns to check against. 
        """

        cols_ref = {'start', 'value', "class"} if cols_ref is None else set(cols_ref)

        if isinstance(x, list):
            ner_records = set(x[0].keys())
            assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

        elif isinstance(x, dict):
            ner_records = set(x.keys())
            assert ner_records.issuperset(cols_ref), f" {ner_records} not in {cols_ref}"

        return True

    @staticmethod
    def nerdata_extract_nertag_from_df(df_or_path):
        df = pd_read_file(df_or_path)
        tag_list = []
        for index, row in df.iterrows():
            for tag in row['ner_list']:
                type_of_tag = tag["class"]
                if type_of_tag not in tag_list:
                    tag_list.append(type_of_tag)
        tag_list = sorted(tag_list)
        log("tag_list", tag_list)
        return tag_list








###########################################################################################################
####### Dataloder Commmon #################################################################################
def nerparquet_load_to_json_gliner( dirin="ztmp/data/ner/norm/conll2003", nrows=1000000)->Dict:
    """Load NER data from a parquet or a JSON file and convert it to a JSON format.

    Input:  parquet file like this
            ["dataset_id", "dataset_cat1", "text_id",  "text", "ner_list",  "info_json" ]


    Output: Gliner Model JSON format
        Target Format             0          1         2       3     4      5
        [{  "tokenized_text": ["State", "University", "of", "New", "York", "Press", ",", "1997", "."],

                                 Token_start  tokenid_end
            "ner":            [ [ 0,         5,                     "Publisher" ] ]
                                State University of New York Press 
        },
  
      data_val = {
        "entity_types": ["Person", 'Event Reservation'],  ### TODO: Remove entity hardcoding
        "samples": data_train[:10]}

    """
    if ".json" in dirin: 
         djson = json_load(dirin)
         return djson


    log("######## Start conversion dataframe to json format...")
    df = pd_read_file( dirin + "/*.parquet", nrows= nrows)
    log(df)
    assert len(df[[ "text", "ner_list" ]])>0

    djson = []
    for i, row in df.iterrows():
      # break  
      #### dd ={"tokenized_text" : df.at[i, "text"], "ner" : ner_list}
      dd = nerparquet_tokenizer_to_json_gliner(row['text'], row["ner_list"], sep=" ")
      djson.append(dd)

    return djson


def nerparquet_tokenizer_to_json_gliner(text:str, ner_list:list, sep=" "):
      """ Reformat  NER data by tokenizing  text and creating a new list of NER entities.

      Parameters:
          text (str):  input text to be tokenized.
          ner_list (List[Tuple[int, int, str]]):  list of NER entities in  format (start_index, end_index, tag).
          sep (str, optional):  separator used to split  text. Defaults to " ".

      Returns:       
            Target Frormat[{  "tokenized_text": ["State", "University", "of", "New", "York", "Press", ",", "1997", "."],
                              "ner":            [ [ 0, 5, "Publisher" ] ]
            },
       0 1 2 3 4 5 6 7 8 9  10 11
      'E U   r e j e c t s     G  erman call to boycott British lamb .'


      """
      ner_list2 = []
      token_text_list = []
      token_id1 = 0
      for (idx1, idx2, tag ) in ner_list:
         ### idx1, idx2 are String indexes
         idx1, idx2 = int(idx1), int(idx2)  ### because parquet is saved as string. 
         tag = str(tag)

         llist =  text[idx1:idx2].split(sep)
         token_text_list = token_text_list + llist ### add token list to token_text_list

         ### token_id1 are List indexes
         token_id2 = len(token_text_list) - 1
         ner_list2.append( [token_id1, token_id2, tag,]  )         
         token_id1 = token_id2 + 1

      dd ={"tokenized_text" : token_text_list, "ner" : ner_list2}
      return dd



def nerparquet_prepro_predict_data(df, coltext="text"):
    sep = " "
    df[coltext] = df[coltext].apply( lambda x: x.split(sep) )
    return df





##########################################################################################################
##########################################################################################################
def run_train(cfg=None, cfg_name="ner_gliner", dirout="./ztmp/exp", istest=1):
    """ 
       python nlp/ner/ner_gliner.py run_train  --dirout ztmp/exp   --cfg "config/train/train1.yaml"  --cfg_name "ner_deberta"

       Args:
          cfg (dict)      : Configuration dictionary (default is None).  "ztmp/myconfig.yaml"
          cfg_name (str)  : sub-name in config to use (default is "ner_gliner").
          dirout (str)    : Output path (default is None).

        Train Frormat
            [{  "tokenized_text": ["State", "University", "of", "New", "York", "Press", ",", "1997", "."],
                "ner":            [ [ 0, 5, "Publisher" ] ]
            }

    """
    log("###### User Params   #############################################")
    if "params":
        cc = Box()
        cc.model_name="urchade/gliner_small"

        #### Data name
        cc.dataloader_name = "dataTEST_load_prepro"
        cc.datamapper_name = "dataTEST_create_label_mapper"

        cc.n_train = 20 if istest == 1 else 1000000000
        cc.n_val   = 5  if istest == 1 else 1000000000

        ##### Train Args
        aa                = CONFIG_DEFAULT
        aa.num_steps      = 2
        aa.save_directory = cc.dirout + "/train_log/"
        aa.eval_every     = aa.num_steps // 2
        aa.device         = "cpu"
        cc.hf_args_train = copy.deepcopy(aa)
        os_makedirs(aa.save_directory)

        ##### HF model
        cc.hf_args_model = {}
        cc.hf_args_model.model_name = cc.model_name
        # cc.hf_args_model.num_labels = NCLASS*2+1 ## due to BOI notation


    log("###### Config Load   #############################################")
    cfg0 = config_load(cfg)
    cfg0 = cfg0.get(cfg_name, None) if cfg0 is not None else None
    ### Override by config  #################################################
    cc = exp_config_override(cc, cfg0, cfg, cfg_name)

    log("###### Experiment Folder   #######################################")
    cc = exp_create_exp_folder(task="train-ner_gliner", dirout=dirout, cc=cc)
    log(cc.dirout)



    log("###### User Data Load   ##########################################")
    from utilmy import load_function_uri
    dataloader_fun = load_function_uri(cc.dataloader_name)
    datamapper_fun = load_function_uri(cc.datamapper_name)

    data_train, data_val = dataloader_fun()            ## data_conll203_load_datasplit()
    L2I, i2L, NCLASS     = datamapper_fun(data_train)  ## data_conll203_load_metadict() Label to Index, Index to Label

    tag_list = list(L2I.keys())

    data_train, data_val = data_train[:cc.n_train], data_val[:cc.n_val]
    eval_data ={ "samples" : data_val, "entity_types": tag_list  }
    log("data_train", data_train[0])

    if "data":
        cc.data ={}
        # cc.data.cols          = columns
        # cc.data.cols_required = ["text", "ner_list" ]
        # cc.data.ner_format    = ["start", "end", "type", "value"]  
        #cc.data.cols_remove   = ['overflow_to_sample_mapping', 'offset_mapping', ] + columns
        cc.data.L2I           = L2I     ### label to Index Dict
        cc.data.i2l           = i2L     ### Index to Label Dict
        cc.data.nclass        = NCLASS  ### Number of NER Classes.


    log("\n##### Model Load ################################################")
    #### available models: https://huggingface.co/urchade
    json_save(cc.to_dict(), f"{cc.dirout}/config.json")
    model = GLiNER.from_pretrained(cc.model_name)


    log("\n##### Train start ######################################")
    train(model, cc.hf_args_train, train_data= data_train, eval_data= eval_data)


    cc.dirmodel = f"{cc.dirout}/model_final"
    log("##### Model Save", cc.dirmodel)
    os_makedirs(cc.dirmodel) 
    model.save_pretrained( cc.dirmodel)




def train(model, config, train_data, eval_data=None):

    cc = Box({})
    cc.config = dict(config)

    assert "entity_types" in eval_data and "samples" in eval_data

    model = model.to(config.device)

    # Set sampling parameters from config
    model.set_sampling_params(
        max_types=config.max_types, 
        shuffle_types=config.shuffle_types, 
        random_drop=config.random_drop, 
        max_neg_type_ratio=config.max_neg_type_ratio, 
        max_len=config.max_len
    )
    
    model.train()

    train_loader = model.create_dataloader(train_data, batch_size=config.train_batch_size, shuffle=True)
    optimizer    = model.get_optimizer(config.lr_encoder, config.lr_others, config.freeze_token_rep)

    n_warmup_steps = int(config.num_steps * config.warmup_ratio) if config.warmup_ratio < 1 else  int(config.warmup_ratio)


    scheduler = get_cosine_schedule_with_warmup(optimizer,
        num_warmup_steps=n_warmup_steps,
        num_training_steps=config.num_steps)

    iter_train_loader = iter(train_loader)

    log("###### training Start Epoch...")
    for step in range(0, config.num_steps):
        try:
            x = next(iter_train_loader)
        except StopIteration:
            iter_train_loader = iter(train_loader)
            x = next(iter_train_loader)

        for k, v in x.items():
            if isinstance(v, torch.Tensor):
                x[k] = v.to(config.device)

        loss = model(x)  # Forward pass
            
        # Check if loss is nan
        if torch.isnan(loss):
            continue

        loss.backward()        # Compute gradients
        optimizer.step()       # Update parameters
        scheduler.step()       # Update learning rate schedule
        optimizer.zero_grad()  # Reset gradients

        descrip = f"step: {step} | epoch: {step // len(train_loader)} | loss: {loss.item():.2f}"
        log(descrip)

        if (step + 1) % config.eval_every == 0:
            model.eval()            
            if eval_data is not None:
                results, f1 = model.evaluate(eval_data["samples"], flat_ner=True, threshold=0.5,
                                      batch_size=12,
                                      entity_types=eval_data["entity_types"])

                log(f"Step={step}\n{results}")


            dirout2 = f"{config.save_directory}/finetuned_{step}"
            os_makedirs(dirout2)                
            model.save_pretrained(dirout2)
            #json_save(cc.to_dict(), f"{config.save_directory}/config.json")
            model.train()




##########################################################################################################
def run_infer(cfg:str=None, dirmodel="ztmp/models/gliner/small", 
                cfg_name:str="ner_gliner_predict",
                dirdata="ztmp/data/text.csv",
                coltext="text",
                dirout="ztmp/data/ner/predict/",
                multi_label = 0,
                threshold = 0.5
                  ):
  """Run prediction using a pre-trained GLiNER model.

    ### Usage
      export pyner="python nlp/ner/ner_gliner.py "

      pyner run_infer --dirmodel "./ztmp/exp/20240520/235015/model_final/"  --dirdata "ztmp/data/ner/gliner"  --dirout ztmp/out/ner/gliner/

      pyner run_infer --cfg config/train.yaml     --cfg_name "ner_gliner_infer_v1"


    labels = ["person", "book", "location", "date", "actor", "character"]
    entities = model2.predict_entities(text, labels, threshold=0.4)

    Output:
        London is capital of united kingdom
            [{"end": 7, "label": "city", "score": 0.9897423982620239, "start": 1, "text": "London"},
            {"end": 40, "label": "location", "score": 0.5948763489723206, "start": 26, "text": "united kingdom"}]

        Paris is capital of France
        [{"end": 6, "label": "city", "score": 0.9915580749511719, "start": 1, "text": "Paris"}]

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


  model = GLiNER.from_pretrained(dirmodel, local_files_only=True)
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






##########################################################################################################
################## Legal Benchmark ########################################################################
def data_load_legalDoc(cfg=None, dirin=r"", dirout=r""):
  """ Convert data to json 
  Input : csv or parquet file

  Target Frormat
  [
  {
    "tokenized_text": ["State", "University", "of", "New", "York", "Press", ",", "1997", "."],
    "ner": [ [ 0, 5, "Publisher" ] ]
  }
  ],
  
  """
  def find_indices_in_list(text, start_pos, end_pos):
        words = text.split(" ")
        cumulative_length = 0
        start_index = None
        end_index = None

        for i, word in enumerate(words):
            word_length = len(word) + 1  # Add 1 for space character
            cumulative_length += word_length

            if start_index is None and cumulative_length > start_pos:
                start_index = i

            if cumulative_length > end_pos:
                end_index = i
                break

        return start_index, end_index

  def convert_to_target(data):
        #### Is it easier for you : faster for you ???, OK, no pb
     
        lowercase_values = {
        'COURT': 'court',
        'PETITIONER': 'petitioner',
        'RESPONDENT': 'respondent',
        'JUDGE': 'judge',
        'LAWYER': 'lawyer',
        'DATE': 'date',
        'ORG': 'organization',
        'GPE': 'geopolitical entity',
        'STATUTE': 'statute',
        'PROVISION': 'provision',
        'PRECEDENT': 'precedent',
        'CASE_NUMBER': 'case_number',
        'WITNESS': 'witness',
        'OTHER_PERSON' : 'OTHER_PERSON'
        }

        targeted_format = []

        for value in data:
            tokenized_text = value['data']['text'].split(" ")      
            ner_tags = []

            for results in value["annotations"][0]['result']:
                ner_list = []
                start, end = find_indices_in_list(value['data']['text'], results['value']['start'],results['value']['end'])
                
                ner_list.append(start)
                ner_list.append(end)
                
                for label in results['value']['labels']:
                    ner_tags.append(ner_list + [lowercase_values[label]])

            targeted_format.append({"tokenized_text" : tokenized_text, "ner":ner_tags})

        return targeted_format

  with open(dirin,'r') as f:
      data = json.load(f)

  data = convert_to_target(data)

  #   cfg = config_load(cfg)
  #   df = pd_read_file(dirin)
  #df["tokenized_text"] = df["text"].apply(lambda x: x.split())
  # 
  #   data= df[[ "tokenized_text", "ner"]].to_json(dirout, orient="records")
  log(str(data)[:100])
  json_save(data, dirout)



def run_train_v2(cfg:dict=None, cfg_name:str=None, dirout:str="ztmp/exp", 
              model_name:str="urchade/gliner_small",
              dirdata=r"D:/github/myutil/utilmy/webapi/asearch/ddata/Legal_NER_Dataset.json"):
  """A function to train a model using specified configuration and data.
  Parameters:
      cfg (dict): Configuration dictionary (default is None).
      dirout (str): Output path (default is None).
      model_name (str): Name of model to use (default is "urchade/gliner_small").
      dirdata (str): path of data to use (default is "data/sample_data.json").

  Returns:
      None
  """
  dt      = date_now(fmt="%Y%m%d/%H%M%S")
  device  = "cpu"
  dirout2 = f"{dirout}/{dt}"


  cfg    = config_load(cfg)
  config = cfg.get(cfg_name, None) if isinstance(cfg, dict) else None
  if config is None:
    config = CONFIG_DEFAULT
    nsteps = 2
    config.num_steps      = nsteps
    config.save_directory = dirout2
    config.eval_every     = nsteps // 2
    config.device         = device
    

  #### evaluation only support fix entity types (but can be easily extended)
  data  = json_load(dirdata)
  eval_data = {
      "entity_types": ['court', 'petitioner', 'respondent', 'judge', 'lawyer', 'date', 'organization', 'geopolitical entity', 'statute', 'provision', 'precedent', 'case_number', 'witness', 'OTHER_PERSON'],
      "samples": data[:10]
  }


  log("##### Model Load", model_name)
  #### available models: https://huggingface.co/urchade
  model = GLiNER.from_pretrained(model_name)


  log("##### Train start")
  train(model, config, data, eval_data)

  dirfinal = f"{dirout2}/final/"
  log("##### Model Save", dirfinal)
  os_makedirs(dirfinal) 
  model.save_pretrained( dirfinal)





##########################################################################################################




###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()






""" 
#### All results
    You need to Copy ALL outputs, always
    ---> its easier, faster. Faster is best, Simple is best, Fast and efficient: OK ?
    COPY PASTE evetything here, every time.



    ### Run fine tunning
    cd asearch/nlp  
    python3 ./ner_gliner.py  run_train_v2 --dirdata  "./ztmp/data/Legal_NER_Dataset.json"  --dirout "./ztmp/models/gliner/small"

    
    ### Output   
        Config: Using default config
        {'field1': 'test', 'field2': {'version': '1.0'}}
        ##### Model Load urchade/gliner_small
        ##### Train start
        ###### training Start Epoch...
        step: 0 | epoch: 0 | loss: 12.55
        Step=0
        P: 15.79%       R: 23.08%       F1: 18.75%

        step: 1 | epoch: 0 | loss: 5.64
        Step=1
        P: 17.65%       R: 23.08%       F1: 20.00%


        ## rename your train to run_train_v2
                rename function to _v2
                  --> easy and simple, ok ?
          Do not delete my code OK N??????????

        Your file has issue your re-write my original code,
        THATS BAD

        you should copy and rename function, OK ?

        Let arrange file now.
         let add your code in my repo and push it

         
                   

         
    ## Metrics F1 is 0.20 ( F1 is a bit low, now ?)
        Previous project: how much was your F1 level :  0.61

        which model ? best score by using GRU with Glove. F1 level: 0




        





        
    

"""














def zzz_run_train_v1(cfg:dict=None, cfg_name:str=None, dirout:str="ztmp/exp", 
              model_name:str="urchade/gliner_small",
              dirdata_train="./ztmp/data/ner/normalized/mydataset/",   
              dirdata_val=None,   
              
              device  = "cpu"):
  """A function to train a model using specified configuration and data.

  python nlp/ner_gliner.py  run_train  --dirout  --cfg "ztmp/myconfig.yaml"

  Parameters:
      cfg (dict)      : Configuration dictionary (default is None).  "ztmp/myconfig.yaml"
      dirout (str)    : Output path (default is None).
      model_name (str): Name of model to use (default is "urchade/gliner_small").
      dirdata (str)   : path of data to use (default is "data/sample_data.json").

  Returns:
      None
  """
  dt      = date_now(fmt="%Y%m%d/%H%M%S")
  dirout2 = f"{dirout}/{dt}"


  log("##### Load Config", cfg_name)
  cfg    = config_load(cfg)  ### String path for config
  config = cfg.get(cfg_name, None) if isinstance(cfg, dict) else None
  if config is None:
    config = CONFIG_DEFAULT
    nsteps = 2
    config.num_steps      = nsteps
    config.save_directory = dirout2
    config.eval_every     = nsteps // 2
    config.device         = device
    

  log("##### Load data", dirdata_train)
  #### evaluation only support fix entity types (but can be easily extended)
  #### Want to rreplace by dataframe load
  data_train : dict = nerparquet_load_to_json_gliner(dirdata_train)

  if dirdata_val is None :
    data_val = {
        "entity_types": ["Person", 'Event Reservation'],  ### TODO: Remove entity hardcoding
        "samples": data_train[:10]}
  else:
    data_val : dict = nerparquet_load_to_json_gliner(dirdata_val)



  log("##### Model Load", model_name)
  #### available models: https://huggingface.co/urchade
  model = GLiNER.from_pretrained(model_name)


  log("##### Train start")
  train(model, config, train_data= data_train, eval_data= data_val)


  dirfinal = f"{dirout2}/final/"
  log("##### Model Save", dirfinal)
  os_makedirs(dirfinal) 
  model.save_pretrained( dirfinal)





##########################################################################################################
def zzzz_data_to_json(cfg=None, dirin="ztmp/data.csv", dirout="ztmp/data/ner/sample_data.json"):
  """ Convert data to json 
  Input : csv or parquet file


  
  """
  cfg = config_load(cfg)
  df  = pd_read_file(dirin)

  data= df[[ "tokenized_text", "ner"]].to_json(dirout, orient="records")
  log(str(data)[:100])
  json_save(data, dirout)

