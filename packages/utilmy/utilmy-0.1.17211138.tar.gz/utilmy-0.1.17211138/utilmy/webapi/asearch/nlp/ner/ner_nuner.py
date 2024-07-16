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


    export cfg="config/ner/ner_cfg.yaml"
    

    python nlp/ner_gliner.py data_converter_collnll2003    --dirout ztmp/models/gliner/mymodel/

    python nlp/ner_gliner.py run_train     --cfg $cfg  --dirout ztmp/exp/
    
    python nlp/ner_gliner.py run_predict   --cfg $cfg  --dirout ztmp/models/gliner/mymodel/



  
  
   https://www.freecodecamp.org/news/getting-started-with-ner-models-using-huggingface/ 
   

   https://arxiv.org/html/2402.10573v2

"""
import os, json, pandas as pd, numpy as np 
from types import SimpleNamespace, Dict
from box import Box

from datasets import load_dataset, concatenate_datasets
from gliner import GLiNER
import torch
from transformers import get_cosine_schedule_with_warmup

from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob, config_load,
                    json_save, json_load)
from utilmy import log, log2



##########################################################################################################
CONFIG_DEFAULT = Box(
        num_steps        = 4,  # number of training iteration
        train_batch_size = 2,
        eval_every       = 4 // 2,   # evaluation/saving steps
        save_directory   = "ztmp/exp/ztest/gliner/", # where to save checkpoints
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

    data_converter_collnll2003( dirout=test_dir, nrows=100)
    json = nerparquet_load_to_json_gliner(test_dir)
    print(json[0])
    # length of dataset
    assert len(json) == 100
    assert json[0].keys() == {'tokenized_text', 'ner'}


    ### other part to be quicly tested

    cleanup(test_dir)
    os.rmdir(test_dir)





###########################################################################################################
####### Datalod Custom ####################################################################################
def data_converter_collnll2003(dirout="ztmp/data/ner/norm/conll2003",  nrows=100000000):
   """Convert raw data to NER Parquet format.
      NER_COLSTARGET       = ["dataset_id", "dataset_cat1", "text_id",  "text", "ner_list",  "info_json" ]

      pip install fire utilmy

      python nlp/ner_gliner.py data_converter_collnll2003  --dirout ztmp/data/ner/norm/conll2003

   
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
   ds0 = load_dataset(dataset,)  ### option to donwload in disk only
   # ds = concatenate_datasets([ds[k] for k in ds.keys()])  ### train and test separate. 


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
                ner_list.append([ str(start_idx), str(i - 1), str(ner_tag) ])
            start_idx = i
            ner_tag   = ner_tags[i]


         ## End  :  when current tag is 0 : enpty NER
         elif ner_tags[i] == 0 and start_idx != -1:
            ner_list.append([ str(start_idx), str(i - 1), str(ner_tag) ])
            start_idx = -1


      ### Last NER 
      if start_idx != -1:
         ner_list.append([ str(start_idx), str(len(tokens) - 1), str(ner_tag) ])

      return ner_list


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
        df2["text_id"]      = ds["id"]    if 'id' in ds.features else np.arange(len(ds))
        df2["info_json"] = list(map((lambda x:  json.dumps({}) )))  

        #### Text: 1 row : Concetanate all tokens merged into one string  (because of BOI tokenizer).
        df2["text"]      = list(map(lambda x: " ".join(x), ds["tokens"])) 

        #### NER_list : [ ( string_idx_start, string_idx_end, ner_tag),   ( idx_start, idx_end, ner_tag),   .... ( idx_start, idx_end, ner_tag),      ]
        #### idx_start: position of string.  
        df2["ner_list"]  = list(map(lambda x: ner_merge_BOI_to_triplet_v1(x[0], x[1]), zip(ds["tokens"], ds["ner_tags"])))




        log("#### Save to parquet  ################################")
        pd_to_file(df2[ NER_COLSTARGET ], dirout + f"/{dtype}/df.parquet", show=1)





def data_converter_myNewDataset(dirout="ztmp/data/ner/norm/conll2003",  nrows=100000000):
   """Convert raw data to NER Parquet format.
      NER_COLSTARGET       = ["dataset_id", "dataset_cat1", "text_id",  "text", "ner_list",  "info_json" ]

      python nlp/ner_gliner.py data_converter_  --dirout ztmp/data/ner/norm/conll2003

   
       ### Initial Format



       ### Target Format
          NER_COLSTARGET       = ["dataset_id", "dataset_cat1",   "text_id"  "text", "ner_list", "info_json" ]
           "text" :     Full text concatenated as string.
           "ner_list" : [ ( str_idx_start, str_idx_end, ner_tag),   ( idx_start, idx_end, ner_tag),   .... ( idx_start, idx_end, ner_tag),      ]


       Custom tokenizer    
       
   """
   dataset  = "XXXX"
   version = None
   dataset_cat = "YYYYY"

   url = "https://huggingface.co/datasets/" + dataset 
   ds0 = load_dataset(dataset,)  ### option to donwload in disk only
   # ds = concatenate_datasets([ds[k] for k in ds.keys()])  ### train and test separate. 


   def ner_merge_BOI_to_triplet_v1(tokens:list, ner_tags:list):      
        pass 


   for dtype in ds0.keys():  
        log("#### Converting", dtype)  ### dtype: "train", "test"
        ds = ds0[dtype]  ### ds is custom Object, not dataframe.
        ds = ds.filter(lambda _, idx: idx < nrows, with_indices=True)  #

        log("#### Convert/Normalize to Standard Format  ################################")
        df2        = pd.DataFrame(columns=NER_COLSTARGET) 

        ### ["dataset_id", "text_id",  "text", "ner_list", "cat1", "info_json" ]
        df2["dataset_id"]   = url
        df2["dataset_cat1"] = dataset_cat
        df2["text_id"]      = ds["id"]    if 'id' in ds.features else np.arange(len(ds))

        #### Text: 1 row : Concetanate all tokens merged into one string 
        df2["text"]      = list(map(lambda x: " ".join(x), ds["tokens"])) 

        #### NER_list : [ ( string_idx_start, string_idx_end, ner_tag),   ( idx_start, idx_end, ner_tag),   .... ( idx_start, idx_end, ner_tag),      ]
        #### idx_start: position of string.  
        df2["ner_list"]  = list(map(lambda x: ner_merge_BOI_to_triplet_v1(x[0], x[1]), zip(ds["tokens"], ds["ner_tags"])))

        df2["info_json"] = list(map((lambda x:  json.dumps({}) )))  


        log("#### Save to parquet  ################################")
        pd_to_file(df2, dirout + f"/{dtype}/df.parquet", show=1)










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
  
    """
    if ".json" in dirin: 
         djson = json_load(dirin)
         return djson


    log("######## Start conversion dataframe to json format...")
    df = pd_read_file( dirin + "/*.parquet", nrows= nrows)
    assert len(df[NER_COLSTARGET])>0

    djson = []
    for i, row in df.iterrows():
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
      """
      ner_list = []  
      token_text_list = []
      token_id1 = 0
      for (idx1, idx2, tag ) in ner_list:
         ### idx1, idx2 are String indexes
         idx1, idx2 = int(idx1), int(idx2)  ### because parquet is saved as string. 
         tag = str(tag)

         llist =  text[idx1:idx2+1].split(sep)
         token_text_list = token_text_list + llist ### add token list to token_text_list

         ### token_id1 are List indexes
         token_id2 = len(token_text_list) - 1
         ner_list.append( [token_id1, token_id2, tag,]  )         
         token_id1 = token_id2 + 1

      dd ={"tokenized_text" : token_text_list, "ner" : ner_list}
      return dd






##########################################################################################################
##########################################################################################################
def run_train(cfg:dict=None, cfg_name:str=None, dirout:str="ztmp/exp", 
              model_name:str="urchade/gliner_small",
              dirdata_train="./ztmp/data/ner/normalized/mydataset/",   
              dirdata_val=None,   
              
              device  = "cpu"):
  """A function to train a model using specified configuration and data.

  python nlp/ner_gliner.py  run_train  --dirout  --cfg "ztmp/myconfig.yaml"

  Parameters:
      cfg (dict): Configuration dictionary (default is None).  "ztmp/myconfig.yaml"
      dirout (str): Output directory path (default is None).
      model_name (str): Name of model to use (default is "urchade/gliner_small").
      dirdata (str): Directory path of data to use (default is "data/sample_data.json").

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




def run_predict(cfg:dict=None, dirmodel="ztmp/models/gliner/small", 
                dirdata="ztmp/data/text.csv",
                coltext="text",
                dirout="ztmp/data/ner/predict/",
                kbatch=100):
  """Function to run prediction using a pre-trained GLiNER model.

    python nlp/ner_gliner.py --dirdata "ztmp/data/text.csv"     --coltext text    --dirout ztmp/data/ner/predict/data1/


    predict_entities(self, text, labels, flat_ner=True, threshold=0.5, multi_label=False):

  Parameters:
      cfg (dict): Configuration dictionary (default is None).
      dirmodel (str): Directory path of pre-trained model (default is "ztmp/models/gliner/small").
      dirdata (str): Directory path of input data (default is "ztmp/data/text.csv").

  #log(model.predict("My name is John Doe and I love my car. I bought a new car in 2020."))

  """
  model = GLiNER.from_pretrained(dirmodel, local_files_only=True)
  log(model)
  model.eval()

  df = pd_read_file(dirdata)
  log(df[coltext].shape)

  df["ner_list_pred"] = df[coltext].apply(lambda x: model.predict(x))
  pd_to_file(df, dirout +"/df_predict_ner.parquet", show=1)



##########################################################################################################
def train(model, config, train_data, eval_data=None):

    cc = Box({})
    cc.config = dict(config)

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





###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()










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

