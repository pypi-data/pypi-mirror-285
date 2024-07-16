"""  
## Install

     pip install --upgrade utilmy fire python-box
     pip install -q -U bitsandbytes peft accelerate  transformers==4.37.2
     pip install  setfit


    ### Dataset Download
        cd asearch
        mkdir -p ./ztmp/
        cd "./ztmp/"
        git clone https://github.com/arita37/data2.git   data
        cd data
        git checkout text

        
    ### Usage:
        cd asearch
        export PYTHONPATH="$(pwd)"  ### Need for correct import

        python nlp/cats/few_shot_setfit.py  preprocess_scientific_text_dataset

    ### Usage scientific dataset
        cd asearch 
        export PYTHONPATH="$(pwd)"
        python nlp/cats/few_shot_setfit.py  run_train --cfg_name few_shot_setfit_scientific --dirout "./ztmp/exp/few_shot"
        
    
    ### Diskcache Enable
    export CACHE_ENABLE="1"   
        
cols = ['L1_cat', 'L1_cat1', 'L2_cat', 'L2_catid', 'L2_catidn', 'L3_cat',
       'L3_cat_des', 'L3_catid', 'L4_cat', 'L4_catid', 'cat_id', 'cat_name',
       'com_id', 'com_id2', 'com_name', 'com_name2', 'dt', 'ind_id',
       'ind_name', 'partnership_acquisition', 'partnership_type', 'text',
       'url']

"single_label_classification"
"multi_label_classification"
"question_answering"
"token_classification"
"sequence_to_sequence"
"causal_language_modeling"
"masked_language_modeling"
"multiple_choice"
"image_classification"
"speech_recognition"
"audio_classification"
"text_generation"
"text_to_speech"


       
"""
if "import":
    import os, sys, json, pandas as pd,numpy as np, gc, time
    import copy, random
    from copy import deepcopy
    from typing import Optional, Union
    from box import Box
    from tqdm import tqdm
    from functools import partial

    from datasets import load_dataset, DatasetDict, Dataset
    from sklearn.metrics import classification_report

    from transformers import (AutoTokenizer, AutoModelForSequenceClassification,    
       TrainingArguments, Trainer, pipeline, DataCollatorWithPadding,
       BertModel
    )

    from sentence_transformers import SentenceTransformer

    import torch, evaluate
    import torch.nn as nn

    from src.engine.usea.utils.util_exp import (exp_create_exp_folder, 
            exp_config_override, exp_get_filelist,json_save, log_pd,
            torch_device)

    from src.utils.utilmy_base import diskcache_decorator, log_pd
    from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob, config_load,
                       json_save, json_load, log, log2, loge)



from dataclasses import dataclass


#######################################################################
def data_load_news():
   df = pd_read_file("ztmp/data/cats/news/train/*.parquet")
   df = df[-df.L4_cat.isna() ]
   df = df[  df.news_text.str.len() > 100 ]
   df = df[ -df.news_text.str.contains("Error") ]
   df = df[ -df.news_text.st_r.contains("error") ]
   df = df[ -df.url.str.contains("sp-edge.com")]
   df = df[ df.apply( lambda x :  x['com_name'].lower()  in x['news_text'].lower() , axis=1 ) ]

   log(df.shape)

   df = pd_com_rerank(df)
   log(df.shape)

   df.index = [i for i in range(len(df))]
   return df 

def data_filter_com(df, tags='microsoft'):
   def fun(x, tag):
       x1 = x['com_name'].lower()
       x2 = x['com_name2'].lower()
       if tag  in x1:  return True
       if tag  in x2: return True
       #if 'amazon web' in x1: return True
       #if 'amazon web' in x2: return True
       return False
   
   if isinstance(tag,str):
       tags = tags.split(",")

   elif isinstance(tags, list):
       pass    

   dfnew= pd.DataFrame()
   for tag in tags: 
      df1 = df[ df.apply(lambda x:  fun(x, tag) , axis=1) ]
      log(tag, len(df1))
      dfnew = pd.concat((dfnew, d1))

   log('filtered',tag, dfnew.shape)
   return dfnew


def data_common(data, cc, istrain=1):        
    ##### Get label2key from all dataset  ###################
    _, label2key = pandas_to_hf_dataset_key(data)
    cc.label2key = label2key
    cc.key2label = {  idx: label       for label, idx in label2key.items()     }

    cc.classes = [''] * len(label2key)
    for label, idx in label2key.items()  :
        cc.classes[idx] = label 

    cc.num_labels =  len(cc.classes)   
    log('Nunique classes: ', cc.num_labels ) 


    onehot=False
    if onehot:
        #### To Onehot
        def to_onehot(x): 
            zero, one = 0.0, 1.0  ## HFace needs float !!
            labels_onehot = [float(zero)] * cc.num_labels
            
            if isinstance(xstr, str):
                  xstr = xstr.split(self.sep)
                  
            for label in xstr:
                ### If mising, One Label INDEX for unknown
                label_id = self.L2I.get(label, cc.num_labels - 1)
                # log("label_id:",label,  label_id)
                labels_onehot[label_id] = one  #

            return labels_onehot

        data['label_onehot'] = data['label'].apply(lambda x : to_onehot( x['label']) )    

    else: 
        data['label_text'] = data['label']
        data['label']      = data['label_text'].map(label2key)
        log('Nunique label: ',data.label.nunique() ) 
        log('label final\n', data['label']  )

    #### Frequency
    freq = data['label_text'].value_counts().reset_index()
    log("\n\n", freq)
    # cc.label_freq = freq.values.tolist()


    ##### Train test split     
    data = data[['text', 'label']]
    data = data.head(cc.n_train)        

    if istrain == 0 :
        dataset = Dataset.from_pandas(data[['text', 'label']])
        return dataset,None,data,cc
    
    train = data # data.head(len(data) - cc.n_test)
    train_dataset = Dataset.from_pandas(train[['text', 'label']])
    log(f'train.shape: {train_dataset.shape}',)

    test         = data.tail(min(80, cc.n_test) )
    test_dataset = Dataset.from_pandas(test[['text',  'label']])
    dataset      = DatasetDict({"train":train_dataset,"test": test_dataset})
    log(f'test.shape:  {test_dataset.shape}' ,)
    
    log('text:  ', test_dataset['text'][0]  )
    log('label: ', test_dataset['label'][0] )    

    return dataset,test_dataset, data, cc




###############################################################################
######## level 4   ############################################################
# @diskcache_decorator
def data_L4_train(data0, cc, istrain=1): 
    """ 
    """
    #### Filter Data
    #ll = [ 'microsoft', 'amazon web service', ]
    #'apple', 'google', 'nvidia' ]
    #data = pd_filter_com(df,  ll)

    data = data0
    log('\nReduce Size: ', data.shape)
    colabel = "L4_cat"


    ###### Label  Setup  #############################
    data = data.rename(columns={colabel: 'label'}, )    
    data = data[ -data['label'].isna()] 
    data = data[ -data['label'].str.len() < 6 ] 
    data['label'] = data['label'].apply(lambda x : x.lower().replace('_', ' '))  
    log('\nLabel After removeNA: ', data.shape)

    ###### Text Setup  ###############################
    def funm(x):    
        # ss = f"{x['label']}. {x['news_title']}.  {x['news_text']}. "  ### Check if OVerfit
        # ss = f"{x['news_title']}.  {x['news_text']}. "        
        ss = f" {x['L1_cat']}.  {x['L2_cat']}.  {x['L3_cat']}. {x['gpt_tags']}.  {x['gpt_text']}. "        
        ss = ss[:2048].strip()
        return ss    
     
    data["text"] = data.apply(lambda x: funm(x), axis=1)
    data = data[data.text.str.len() > 100 ] ### Fitler out bad text
    data = data[ data.apply( lambda x :  x['com_name'].lower()  in x['text'].lower() , axis=1 ) ]

    log(data["text"].head(1))
    log(data.shape)
  
    # log(data['label'].values)
    ## data = data.groupby('label').apply(lambda x: x.sample(n=5, random_state=42, replace=True)).reset_index(drop=True)

    return data_common(data, cc, istrain)



###############################################################################
######## level 4   ############################################################

# @diskcache_decorator
def data_L3_train(data0, cc): 
    """ 
    """
    data = data0
    log('\nReduce Size: ', data.shape)
    colabel = "L3_cat"


    ###### Label  Setup  #############################
    data = data.rename(columns={colabel: 'label'}, )    
    data = data[ -data['label'].isna()] 
    data = data[ -data['label'].str.len() < 6 ] 
    data['label'] = data['label'].apply(lambda x : x.lower().replace('_', ' '))  
    log('\nLabel After removeNA: ', data.shape)

    ###### Text Setup  ###############################
    def funm(x):    
        # ss = f"{x['label']}. {x['news_title']}.  {x['news_text']}. "  ### Check if OVerfit
        # ss = f"{x['news_title']}.  {x['news_text']}. "        
        ss = f" {x['L1_cat']}.  {x['L2_cat']}.   {x['gpt_tags']}.  {x['gpt_text']}. "        
        ss = ss[:2048].strip()
        return ss    
     
    data["text"] = data.apply(lambda x: funm(x), axis=1)
    data = data[data.text.str.len() > 100 ] ### Fitler out bad text
    data = data[ data.apply( lambda x :  x['com_name'].lower()  in x['text'].lower() , axis=1 ) ]

    log(data["text"].head(1))
    log(data.shape)
  
    # log(data['label'].values)
    ## data = data.groupby('label').apply(lambda x: x.sample(n=5, random_state=42, replace=True)).reset_index(drop=True)

    return data_common(data, cc)


########################################################################
######### L2 level category ############################################
@diskcache_decorator
def data_L2_train(data0, cc): 
    """ 
    """
    #### Filter Data
    #data = pd.DataFrame()
    #ll = [ 'microsoft', 'amazon web service', ]
    #'apple', 'google', 'nvidia' ]
    #for name in ll:
    #   d1   = data_filter_com( deepcopy(data0), tag=name)
    #   data = pd.concat((data, d1))

    data = data0
    log('\nReduce Size: ', data.shape)

    colabel = "L2_cat"


    ###### Label  Setup  #############################
    data = data.rename(columns={colabel: 'label'}, )    
    data = data[ -data['label'].isna()] 
    data = data[ -data['label'].str.len() < 6 ] 
    data['label'] = data['label'].apply(lambda x : x.lower().replace('_', ' '))  
    log('\nLabel After removeNA: ', data.shape)

    ###### Text Setup  ##############################
    def funm(x):    
        # ss = f"{x['label']}. {x['news_title']}.  {x['news_text']}. "  ### Check if OVerfit
        # ss = f"{x['news_title']}.  {x['news_text']}. "        
        ss = f"{x['gpt_tags']}.  {x['gpt_text']}. "        
        ss = ss[:2048].strip()
        return ss    
     
    data["text"] = data.apply(lambda x: funm(x), axis=1)
    data = data[data.text.str.len() > 100 ] ### Fitler out bad text
    data = data.apply([data.text.str.len() > 100 ]) ### Fitler out bad text
    data = data[ data.apply( lambda x :  x['com_name'].lower()  in x['text'].lower() , axis=1 ) ]

    log(data["text"].head(1))
    log(data.shape)
  
    # log(data['label'].values)
    ## data = data.groupby('label').apply(lambda x: x.sample(n=5, random_state=42, replace=True)).reset_index(drop=True)

    return data_common(data, cc)





########################################################################
######### L1 level category ############################################
@diskcache_decorator
def data_L1_train(data0, cc, istrain=1): 
    """ 
    """
    data = data0
    log('\nReduce Size: ', data.shape)


    ###### Label  Setup  #############################
    data = data.rename(columns={'L1_cat': 'label'}, )    
    data = data[ -data['label'].isna()] 
    data['label'] = data['label'].apply(lambda x : x.lower().replace('_', ' '))  
    log('\nLabel removeNA: ', data.shape)


    ###### Text Setup  ##############################
    def funm(x):    
        # ss = f"{x['label']}. {x['news_title']}.  {x['news_text']}. "  ### Check if OVerfit
        # ss = f"{x['news_title']}.  {x['news_text']}. "        
        ss = f"{x['gpt_tags']}.  {x['gpt_text']}. "        
        ss = ss[:2048].strip()
        return ss    
     
    data["text"] = data.apply(lambda x: funm(x), axis=1)
    data = data[ data.apply(lambda x: len(x['text']) > 50 , axis=1) ]
    data = data[ data.apply(lambda x: x['com_name'] in x['text'], axis=1 ) ]    
    log(data["text"].head(1))
  
    # log(data['label'].values)
    ## data = data.groupby('label').apply(lambda x: x.sample(n=5, random_state=42, replace=True)).reset_index(drop=True)

    return data_common(data, cc, istrain)





def ds_test_token():

    from datasets import load_dataset
        
    dataset = load_dataset('knowledgator/events_classification_biotech') 
        
    classes = [class_ for class_ in dataset['train'].features['label 1'].names if class_]
    class2id = {class_:id for id, class_ in enumerate(classes)}
    id2class = {id:class_ for class_, id in class2id.items()}


    from transformers import AutoTokenizer
    model_path = "microsoft/deberta-v3-base"
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    def preprocess_function(example):
       text = f"{example['title']}.\n{example['content']}"
       all_labels = example['all_labels'] # .split(', ')
       labels = [0. for i in range(len(classes))]
       for label in all_labels:
           label_id = class2id[label]
           labels[label_id] = 1.
      
       example = tokenizer(text, truncation=True)
       example['labels'] = labels

       #dd2 = {k:v for k,v in example.items() if k in ll }     
       return example

    tokenized_dataset = dataset.map(preprocess_function)
    log(tokenized_dataset)
    n_labels = len(classes)
    return tokenized_dataset, tokenizer, n_labels 



def hf_tokenized_data_clean(tk_ds, cols_remove1=None):
    ll = [ 'input_ids', 'token_type_ids', 'attention_mask', 'labels' ]

    if 'train' in tk_ds:
        cols_remove = [  ci   for ci in tk_ds['train'].column_names if ci not in ll  ]

    tk_ds       = tk_ds.remove_columns(cols_remove)


    log(tk_ds)
    log('labels: ', tk_ds['train']['labels'][0] )
    return tk_ds


def tokenize_singlerow(rows, num_labels, label2key):
    """
      # tokenize2 = partial(tokenize_singlerow, num_labels=cc.num_labels, label2key=cc.label2key)
      # tk_ds = dataset.map(partial( tokenize2)) # , batched=False)

    """
    out = tokenizer( rows["text"], truncation=True, max_length=2048, )
             # padding=True, 
             # max_length=2048, 
    xval = rows['label']
    if isinstance(xval, str):
         xval = xval.split(',')
    elif isinstance(xval, list):
         pass 
    else :
         xval = [xval]    
   
    if isinstance(xval, list):            
        ones = [0. for i in range(num_labels)]
        for label_idx in xval :
           ones[label_idx] = 1.

    out['labels'] = ones
    #     # ones = torch.tensor(ones, dtype=torch.float)
    return out



def run_train_multi(istest=1, dirout="./ztmp/exp/L1_cat/v3deber/" ):
    """  multi_label_prediction ONLY
         
         python  src/catfit.py  run_train_multi --istest 0
         
         
    """
    log("\n###### User default Params   ###################################")
    if "config":    
        cc = Box()
        # cc.model_name='BAAI/bge-base-en-v1.5'   
        # cc.model_name = 'knowledgator/comprehend_it-base'  
        # cc.model_name="sileod/deberta-v3-large-tasksource-nli"
        cc.model_name ="MoritzLaurer/deberta-v3-base-zeroshot-v2.0"
        # cc.model_name ="microsoft/deberta-v3-base"


        dirout  = "./ztmp/exp/L1_cat/deberV3/"
        cc.task = "L1_cat"  

        cc.datafun_name = "data_L1_train"

        #cc.checkpoint = dirout +'/train/checkpoint-10500-backup'     
        cc.checkpoint = None
        cc.epochs = 1
        cc.device = torch_device("cpu")         

         
        ### Need sample to get enough categories
        cc.n_train = 20   if istest == 1 else 1000000000
        cc.n_test   = 10  if istest == 1 else int(cc.n_train*0.1)

        cc.save_steps = 500
        cc.eval_steps = 50 
        cc.max_length_tokenizer = 2048


        cc.problem_type =  "multi_label_classification" ### Hard-Coded
        cc.dirout            = dirout
        cc.dirout_checkpoint =  cc.dirout + '/train'
        cc.dirout_log        =  cc.dirout + '/log'
        cc.dirout_model      =  cc.dirout + '/model'
        

        #### Trainer Args #############################
        aa = Box({})
        aa.output_dir    = cc.dirout_checkpoint
        aa.logging_dir   = cc.dirout_log
        aa.logging_steps = 10

        aa.per_device_train_batch_size = 4
        aa.gradient_accumulation_steps = 1
        aa.optim                       = "adamw_hf"
        aa.save_steps                  = min(100, cc.n_train-1)
        aa.logging_steps               = min(50,  cc.n_train-1)
        aa.learning_rate               = 2e-5
        aa.max_grad_norm               = 2
        aa.max_steps                   = -1
        aa.warmup_ratio                = 0.2 # 20%  total step warm-up
        # lr_schedulere_type='constant'
        aa.evaluation_strategy    = "steps"
        aa.save_strategy          = "steps"
        aa.load_best_model_at_end = True

        aa.num_train_epochs  = cc.epochs
        aa.eval_steps=   cc.eval_step      
        aa.save_steps=   cc.save_steps

        cc.hf_args_train = copy.deepcopy(aa)

        os_makedirs(cc.dirout_log)
        os_makedirs(cc.dirout_checkpoint)
        os_makedirs(cc.dirout + "/model")        


    log("\n##### Load+clean data  #########################################")
    data = pd_read_file("ztmp/data/cats/news/train_gpt/*.parquet")
    log(data.columns, data.head(1).T, "\n\n")    
    from utilmy import load_function_uri

    dataload_fun = load_function_uri(cc.datafun_name,  globals() )
    dataset, test_dataset, data, cc = dataload_fun(data, cc) 
    del data; gc.collect()

    cc.num_labels = len(cc.classes)
    log('N_labels used:', cc.num_labels)
    log(len(cc.label2key), len(cc.key2label) )



    log("\n###################load Tokenizer #############################")
    torch_init()
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)    

    def tokenize_batch(rows, num_labels, label2key):
        out = tokenizer( rows["text"],truncation=True, max_length=2048, )
                 # padding=True, 
                 # max_length=2048, 

        ##### Label encoding: OneHot needed for multi_label 
        ll   = []
        sample_list = rows['label']
        for row in sample_list:
            ones = [0. for i in range(num_labels)]
            
            if isinstance(row, int):
                ### 1 text ---> 1 Single Tags 
                ones[ row ] = 1.
                ll.append(ones)

            elif isinstance(row, list):
                ### 1 text ---> Many Label Tags 
                for vali in row:
                    ones[ vali ] = 1.   ### Float for Trainer
                ll.append(ones )
               
        out['labels'] = ll
        return out


    tk_batch2 = partial(tokenize_batch, num_labels=cc.num_labels, label2key=cc.label2key)
    tk_ds     = dataset.map(tk_batch2 , batched=True)

    log('##### \ntk_ds', tk_ds)
    log(tk_ds['test'][0]['labels'], "\n")
    # tk_ds, tokenizer, num_labels = ds_token1()


    from transformers import DataCollatorWithPadding
    tk_ds         = hf_tokenized_data_clean(tk_ds, cols_remove1=None)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)


    log("\n###################load model #############################")
    model = AutoModelForSequenceClassification.from_pretrained(cc.model_name, 
                      num_labels= cc.num_labels,
                      # id2label= cc.key2label, label2id= cc.label2key,
                      problem_type= "multi_label_classification", ### Hard Coded, cannot Change
                      ignore_mismatched_sizes=True)


    # Set up training
    training_args = TrainingArguments(**cc.hf_args_train )

    trainer = Trainer( model=model, args=training_args, tokenizer=tokenizer,
        train_dataset = tk_ds['train'],
        eval_dataset  = tk_ds['test'],
        data_collator = data_collator,

        compute_metrics = compute_metrics_v2
    )

    log("\n###################Train: start #############################")
    json_save(cc, f'{cc.dirout}/config.json')
    log("#### Checkpoint: ", cc.checkpoint)
    trainer_output = trainer.train(resume_from_checkpoint= cc.checkpoint)
    trainer.save_model( f"{cc.dirout}/model")

    evals = trainer.evaluate()
    cc['trainer_eval']    = str(evals)
    cc['trainer_metrics'] = trainer_output.metrics
    log(cc)
    json_save(cc, f'{cc.dirout}/config.json',     show=0)
    json_save(cc, f'{cc.dirout}/model/meta.json', show=0)  ### Required when reloading for     
    del trainer; del model; gc.collect()





############################################################################### 
def run_train_single(istest=1, dirout="./ztmp/exp/L1_cat/v3deber/" ):
    """  
         
         python  src/catfit.py  run_train2 --istest 0
         
         
    """
    log("\n###### User default Params   #####################################")
    if "config":    
        cc = Box()
        # cc.model_name='BAAI/bge-base-en-v1.5'   
        # cc.model_name = 'knowledgator/comprehend_it-base'  
        # cc.model_name = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
        # cc.model_name="sileod/deberta-v3-large-tasksource-nli"
        # cc.model_name ="MoritzLaurer/deberta-v3-base-zeroshot-v2.0"
        cc.model_name ="microsoft/deberta-v3-base"


        dirout = "./ztmp/exp/L1_cat/deberV3/"
        cc.task = "L1_cat"  

        cc.datafun_name = "data_L1_train"

        #cc.checkpoint = dirout +'/train/checkpoint-10500-backup'     
        cc.checkpoint = None

        ### with less labels --> can increase cc.N to 8
        ### 10 cat --> 4160
        # cc.N = 10 # few shot : per sample/class training (select only few sample to train)
        cc.epochs = 5

        cc.dirout = dirout
        cc.device = torch_device("cpu")         


        cc.problem_type =  HFproblemtype.MULTI_LABEL_CLASSIFICATION
         
        ### Need sample to get enough categories
        cc.n_train = 20   if istest == 1 else 1000000000
        cc.n_test   = 10  if istest == 1 else int(cc.n_train*0.1)
  

        cc.max_length_tokenizer = 2048


        cc.dirout_checkpoint =  cc.dirout + '/train'
        cc.dirout_log        =  cc.dirout + '/log'
        cc.dirout_model      =  cc.dirout + '/model'
        
        #### Trainer Args
        aa = Box({})
        aa.output_dir                  = f"{dirout}/train"
        aa.logging_dir= cc.dirout_log,
        aa.logging_steps=10,

        aa.per_device_train_batch_size = 4
        aa.gradient_accumulation_steps = 1
        aa.optim                       = "adamw_hf"
        aa.save_steps                  = min(100, cc.n_train-1)
        aa.logging_steps               = min(50,  cc.n_train-1)
        aa.learning_rate               = 2e-5
        aa.max_grad_norm               = 2
        aa.max_steps                   = -1
        aa.warmup_ratio                = 0.2 # 20%  total step warm-up
        # lr_schedulere_type='constant'
        aa.evaluation_strategy="steps"
        aa.save_strategy="steps",
        aa.load_best_model_at_end=True,

        aa.num_train_epochs  = cc.epochs
        aa.eval_steps=  20      
        aa.save_steps= 1000,

        cc.hf_args_train = copy.deepcopy(aa)

        os_makedirs(cc.dirout_log)
        os_makedirs(cc.dirout_checkpoint)
        os_makedirs(cc.dirout + "/model")        


    log("\n##### Load data  ###############################################  ")
    data = pd_read_file("ztmp/data/cats/news/train_gpt/*.parquet")
    log(data.columns, data.head(1).T, "\n")    
    from utilmy import load_function_uri

    dataload_fun = load_function_uri(cc.datafun_name,  globals() )
    dataset, test_dataset, data, cc = dataload_fun(data, cc) 
    del data; gc.collect()

    log( len(cc.label2key), len(cc.key2label) )
    cc.num_labels = len(cc.classes)
    log('N_labels used:', cc.num_labels)



    log("\n###################load Tokenizer #############################")
    torch_init()
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)    
    def tokenize(rows, num_labels, label2key):
        out = tokenizer( rows["text"],truncation=True)
                 # padding=True, 
                 # max_length=2048, 

        xval = rows['label']
        if isinstance(xval, str):
            xval = xval.split(',')
        elif isinstance(xval, list):
            pass 
        else :
             xval = [xval]    
       
        if isinstance(xval, list):            
            ones = [0. for i in range(num_labels)]
            for label_idx in xval :
               ones[label_idx] = 1.


        out['labels'] = ones
        #     # ones = torch.tensor(ones, dtype=torch.float)
        return out

    # tokenize2 = partial(tokenize, num_labels=cc.num_labels, label2key=cc.label2key)
    # tk_ds = dataset.map(partial( tokenize2)) # , batched=True)


    def tokenize_batch(rows, num_labels, label2key):
        out = tokenizer( rows["text"],truncation=True)
                 # padding=True, 
                 # max_length=2048, 

        ll = []
        xval = rows['label']
        for val in xval:
            ones = [0. for i in range(num_labels)]
            ones[ val ] = 1.
            ll.append(ones )

        out['labels'] = ll
        #     # ones = torch.tensor(ones, dtype=torch.float)
        return out

    # def tokenize_batch(batch, num_labels, label2key):
    #     texts = [row["text"] for row in batch]
    #     out = tokenizer(texts, truncation=True, padding=True, return_tensors="pt")
        
    #     labels = torch.zeros((len(batch), num_labels))
    #     for i, row in enumerate(batch):
    #         xval = row['label']
    #         xval = [xval] if not isinstance(xval, list) else xval
    #         for label in xval:
    #             label_idx = label2key[label] if isinstance(label, str) else label
    #             labels[i, label_idx] = 1.
        
    #     out['labels'] = labels
    #     return out

    tokenize_batch2 = partial(tokenize_batch, num_labels=cc.num_labels, label2key=cc.label2key)
    tk_ds = dataset.map( tokenize_batch2 , batched=True)


    log('##### \ntk_ds', tk_ds)
    log(tk_ds['test'][0]['labels'], "\n")
    # val_ds   = test_dataset.map(tokenize_function, batched=True)
    # dsdict = DatasetDict({"train":train_ds,"test": val_ds })

    num_labels = cc.num_labels
    # tk_ds, tokenizer, num_labels = ds_token1()


    tk_ds = hf_tokenized_data_clean(tk_ds, cols_remove1=None)



    from transformers import DataCollatorWithPadding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)


    log("\n###################load model #############################")
    model = AutoModelForSequenceClassification.from_pretrained(cc.model_name, 
                      num_labels= num_labels,
                      # problem_type = cc.problem_type,
                      # id2label= cc.key2label, label2id= cc.label2key,
                      # problem_type=   "single_label_classification", 
                      problem_type= "multi_label_classification",
                      ignore_mismatched_sizes=True)


    # Set up training
    training_args = TrainingArguments(
        output_dir= cc.dirout + "/train",
        num_train_epochs= cc.epochs,
        per_device_train_batch_size=1,

        logging_dir= dirout + '/log',
        logging_steps=10,

        save_strategy="steps",
        save_steps= 1000,

        evaluation_strategy="steps",
        eval_steps= 20      #// training_args.per_device_train_batch_size,
    )


    trainer = Trainer( model=model, args=training_args, tokenizer=tokenizer,
        train_dataset= tk_ds['train'],
        eval_dataset=  tk_ds['test'],        
        compute_metrics= compute_metrics_f1_acc,
        data_collator = data_collator
    )

    log("\n###################Train: start #############################")
    json_save(cc, f'{cc.dirout}/config.json')
    log("#### Checkpoint: ", cc.checkpoint)
    trainer_output = trainer.train(resume_from_checkpoint= cc.checkpoint)
    trainer.save_model( f"{cc.dirout}/model")

    evals = trainer.evaluate()
    cc['trainer_eval']    = str(evals)
    cc['trainer_metrics'] = trainer_output.metrics
    log(cc)
    json_save(cc, f'{cc.dirout}/config.json',     show=0)
    json_save(cc, f'{cc.dirout}/model/meta.json', show=0)  ### Required when reloading for     
    del trainer; del model; gc.collect()


    
    

###############################################################################    
def run_train_nli(cfg='config/train.yml', cfg_name='cat_name', 
              dirout: str="./ztmp/exp",
              dirdata: str='./ztmp/data/cats/cat_name/train/',
              istest=1 ):
    """ 
    
       python src/catfit.py  run_train  --dirout "./ztmp/exp/L1_cat_MoritzV3large"  --istest 1


       python src/catfit.py  run_train  --dirout "./ztmp/exp/L1_comprehend"  --istest 1
          

          
       
    """
    log("\n###### User default Params   #######################################")
    if "config":    
        cc = Box()
        # cc.model_name='BAAI/bge-base-en-v1.5'   
        cc.model_name = 'knowledgator/comprehend_it-base'  
        # cc.model_name = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
  
        ### with less labels --> can increase cc.N to 8
        ### 10 cat --> 4160
        cc.task = "L1_cat"  
        cc.N = 10 # few shot : per sample/class training (select only few sample to train)
        epochs = 1 
        cc.device = torch_device("mps")         
         
        ### Need sample to get enough categories
        cc.n_train = 4000  if istest == 1 else 1000000000
        cc.n_test   = 500  if istest == 1 else int(cc.n_train*0.1)
  
  
        #### Train Args
        aa = Box({})
        aa.num_train_epochs            = epochs


        aa.output_dir                  = f"{dirout}/log_train"
        aa.per_device_train_batch_size = 8
        aa.gradient_accumulation_steps = 1
        aa.optim                       = "adamw_hf"
        aa.save_steps                  = min(100, cc.n_train-1)
        aa.logging_steps               = min(50,  cc.n_train-1)
        aa.learning_rate               = 2e-5
        aa.max_grad_norm               = 2
        aa.max_steps                   = -1
        aa.warmup_ratio                = 0.2 # 20%  total step warm-up
        # lr_schedulere_type='constant'
        #aa.evaluation_strategy = "epoch"
        aa.evaluation_strategy="steps"
        aa.eval_steps= 500       #// training_args.per_device_train_batch_size,
        aa.logging_strategy    = "epoch"
        aa.save_strategy       = "epoch"
        cc.hf_args_train = copy.deepcopy(aa)


        ### HF model
        cc.hf_args_model = {}
        cc.hf_args_model.model_name = cc.model_name

    log("\n################### Config Load  #############################")
    cfg0 = config_load(cfg)
    cfg0 = cfg0.get(cfg_name, None) if cfg0 is not None else None
    #### Override of cc config by YAML config  ############################### 
    cc = exp_config_override(cc, cfg0, cfg, cfg_name)
    cc = exp_create_exp_folder(task= cc.task , dirout=dirout, cc=cc)
    
    cc.hf_args_train.output_dir = f'{cc.dirout}/log_train'
    log('direxp : ', cc.dirout)
    
    
    log("\n###################load dataset #############################")
    data = pd_read_file(dirdata)
    log(data.columns, "\n",  data.head(1).T)
    
        
    # dataset, test_dataset, data, cc = dataset_setup_cat(data, cc)
    dataset, test_dataset, data, cc = data_L1_train(data, cc)
    

        
    assert set(['text', "label"]).issubset(set(data.columns.tolist()))    
    log("\n###############Prepare fewshot dataset#####################")
    train_dataset = get_train_dataset(dataset, cc.N)

    log("\n###############Tokenizer dataset###########################")
    tokenizer     = AutoTokenizer.from_pretrained(cc.model_name)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    dataset       = transform_dataset(train_dataset, cc.classes)

    tk_dataset = dataset.map(partial(tokenize_and_align_label, tokenizer=tokenizer))
    tk_dataset = tk_dataset.train_test_split(test_size=0.1)    
    tk_dataset = tk_dataset.with_format("torch", device= cc.device)

    if istest > 0:
        tk_dataset = dataset_reduce(tk_dataset, ntrain= 10, ntest = 5) 
       
       
    log("\n###################load model #############################")
    model = AutoModelForSequenceClassification.from_pretrained(cc.model_name)
    model = model.to(cc.device)
    log(str(cc.classes)[:100])
    accuracy = evaluate.load("accuracy")
    training_args  = TrainingArguments( ** dict(cc.hf_args_train))


    trainer = Trainer(
        model           = model,
        args            = training_args,
        train_dataset   = tk_dataset["train"],
        eval_dataset    = tk_dataset['test'],
        tokenizer       = tokenizer,
        data_collator   = data_collator,
        compute_metrics = compute_metrics_f1_acc, # partial(compute_metrics, accuracy_fn=accuracy),
    )

    log("\n###################Accelerate setup ##########################")
    accelerator = accelerator_init(device=cc.device)
    model       = accelerator.prepare(model)
    trainer     = accelerator.prepare(trainer)


    log("\n###################Train: start #############################")
    json_save(cc, f'{cc.dirout}/config.json')
    trainer_output = trainer.train()
    trainer.save_model( f"{cc.dirout}/model")

    cc['metrics_trainer'] = trainer_output.metrics
    json_save(cc, f'{cc.dirout}/config.json',     show=0)
    json_save(cc, f'{cc.dirout}/model/meta.json', show=0)  ### Required when reloading for     
    del trainer; del model; gc.collect()
    
    
    log("\n###################Eval: start #############################")    
    model2 = pipeline("zero-shot-classification",
                      model=f"{cc.dirout}/model",tokenizer=tokenizer, device=cc.device)
    
    dirout = f"{cc.dirout}/eval"
    imin=  0        
    imax = 10000
    if istest == 1:
        imin,imax = 0, 2

    model_eval(model2, test_dataset, cc, dirout, imin=imin, imax=imax, istrain=1)              



    
def run_eval(cfg='config/train.yml', cfg_name='classifier_data', 
              dirout:  str = "./ztmp/exp",
              dirdata: str = './ztmp/data/cats/cat_name/train/',
              istest=1):
    """ 
    
       python src/catfit.py  run_eval --istest 0        
          
       
    
    """
    cc = Box({})
    log("\n###### User default Params   ###################################")

    dirdata  = "ztmp/data/cats/news/train_gpt/*.parquet"

    # dirmodel = './ztmp/exp/L4_cat/deberV3/model_v2/'
    # dirmodel = './ztmp/exp/L4_cat/deberV3/train/checkpoint-10500-backup'
    # dataprepro_name = "data_L4_train"    


    dirmodel = './ztmp/exp/L1_cat/deberV3/train/checkpoint-4000'
    dataprepro_name = "data_L1_train"    



    log("\n################### Config Load  #############################")
    cc = json_load(dirmodel +"/meta.json")
    if cc is None or len(cc) < 1 :
       cc = json_load(dirmodel +"/../../config.json") #### Checkpoint
     
    cc = Box(cc) ; log(cc.keys() )
    device = torch_device("mps")
    cc.dirmodel     = dirmodel
    cc.dirdata      =  dirdata
    cc.datafun_name = dataprepro_name
    cc.task         = HFtask.text_classification

    cc.dirout       = cc.dirmodel +'/eval/'

    cc.n_train = 10 if istest == 1 else 10000000 
    cc.n_test  = 1  if istest == 1 else 100000 

    cc.batch_size = 8


    log('cc:',str(cc.classes)[:100])
    log("\n###################load dataset #############################")    
    from utilmy import load_function_uri

    data = pd_read_file(cc.dirdata)
    log(data.columns, data.head(1).T, "\n")
    
    dataload_fun = load_function_uri( cc.datafun_name,  globals() )
    dataset, test_dataset, data, cc = dataload_fun(data, cc, istrain=0) 
    
    
    
    dataset = Dataset.from_pandas(data[['text', 'label']])                   
    log("\n################## Load model #############################")
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
    model     = pipeline(cc.task,
                      model=f"{cc.dirmodel}",tokenizer=tokenizer, device=device,
                      batch_size= cc.batch_size, return_all_scores=True)


    label2id, id2label= hf_model_get_mapping(model= f"{cc.dirmodel}" )
    log(str(label2id)[:100] )


    log("\n################### Accelerate setup ##########################")
    accelerator = accelerator_init(device=device)
    model       = accelerator.prepare(model)
            

    log("\n################### Start inference ##########################")
    with torch.no_grad():
        predictions = model(dataset["text"])

    #### Mapping
    label2idx, idx2label   = cc.label2key, cc.key2label
    classes_idx = [label2idx[li] for li in cc.classes ] 


    log("\n################### Start Mapping ##########################")
    imin,imax =  0,  10000
    imin,imax = (0, 2)   if istest == 1 else (imin,imax)

    if cc.task == HFtask.text_classification :
            pred_labels = [ label2id[ pred["label"] ] for pred in predictions]
            true_labels = dataset["label"]
            dfp = pd.DataFrame({ 'text': dataset['text'], 'label_idx' : dataset['label'], 'pred_idx': pred_labels } )

            dfp['label'] = dfp['label_idx'].apply(lambda x : idx2label.get(x, "") )
            dfp['pred']  = dfp['pred_idx'].apply(lambda  x : idx2label.get(x, "") )


    elif cc.task == HFtask.zeroshot_classifier :
            true_labels = dataset["label"]
            pred_labels = [ x['labels'][ [ np.argmax(x['scores']) ] ] for x in predictions]

            dfp =[]
            for row in predictions :
               dfp.append( [row['labels'], row['scores'] ])
            dfp = pd.DataFrame( dfp, columns=['labels', 'scores'] )
            dfp['text']  = dataset['text']
            dfp['label'] = dataset['label']

    pd_to_file(dfp, f"{cc.dirout}/df_pred.parquet", show=1 )


    log("\n################### Start Metrics ##########################")    
    #from utilmy.webapi.asearch.utils.util_metrics import metrics_eval
    #metrics = metrics_eval(true_labels, pred_labels, metric_list=['accuracy', 'f1', 'precision', 'recall'])
    #print(metrics)
    accuracy_score = accuracy_metric.compute(references=true_labels, predictions=pred_labels)
    f1_score       = f1_metric.compute(references=true_labels, predictions=pred_labels, average='micro')

    txt = classification_report(true_labels, pred_labels, 
                              target_names= cc.classes,
                              labels      = classes_idx,                                            
                              digits=4)

    txt += f"\n\nAccuracy: {accuracy_score['accuracy']}" 
    txt += f"\nF1 Score: {f1_score['f1']}" 
    log(txt)
    with open(f"{cc.dirout}/metrics.txt", mode='w') as fp:
        fp.write(txt)






def model_eval_zeroClassifier(model, dataset, cc, dirout, imin=0, imax=100000, istrain=0): 
    log("\n################### Start inference ##########################")
    pred0 = []
    ymd,hm = date_now(fmt="%y%m%d-%H%M").split("-")
    dirout0 = dirout + f"/preds/{ymd}/{hm}"
        
    rr = {'report': []}    

    label2idx   = cc.label2key
    idx2label   = cc.key2label
    classes_idx = [label2idx[li] for li in cc.classes ] 
    for ii, example in enumerate(tqdm(dataset)):
        if ii < imin: continue
        pred_dd = model(example['text'], cc.classes)
        if ii == 0: log(pred_dd)
        pred0.append([ example['text'], example['label'], pred_dd['labels'], pred_dd['scores'] ])
        
        #if ii % 20 == 0 : 
        #    pi = pd.DataFrame(pred0, columns=['text', 'true', 'pred_labels', 'pred_scores'])                 
        #    pd_to_file(pi,  f"{dirout0}/ztmp/preds_{ii}_{len(pi)}.parquet", show=0)

        if ii % 100 == 0 or ii == min(imax, len(dataset)-1) :  

            if istrain == 1:       
               ## In train the label == index_label !!! 
               preds = pd.DataFrame(pred0, columns=['text', 'true_idx', 'pred_labels', 'pred_scores'])    
               preds['true']    = preds.apply(lambda x:  idx2label.get(x['true_idx'], -1), axis=1)                                 

            else: ### In Pred: opposite.
               preds = pd.DataFrame(pred0, columns=['text', 'true', 'pred_labels', 'pred_scores'])    
               preds['true_idx'] = preds.apply(lambda x:  label2idx.get(x['true'], -1), axis=1)                                 

            preds['pred']     = preds.apply(lambda x:  x['pred_labels'][  np.argmax(x['pred_scores']) ], axis=1) 
            # preds['pred']     = preds.apply(lambda x:  x['pred_labels'][ argmax_score(x['pred_scores'])] , axis=1) 
            preds['pred_idx'] = preds.apply(lambda x:  label2idx.get(x['pred'], -1), axis=1) 
            log(preds[[ 'true', 'pred'    ]])  
            log(preds.head(1).T)

            pd_to_file(preds, f"{dirout0}/preds_{ii}_{len(preds)}.parquet", show=1)
            try:      
                dfi = preds[ (preds.true_idx > -1) & (preds.pred_idx > -1) ]   
                log(dfi[[ 'true_idx', 'pred_idx', 'true', 'pred'    ]])
                txt = classification_report(dfi['true_idx'].values, dfi['pred_idx'].values, 
                                          target_names= cc.classes,
                                          labels      = classes_idx,                                            
                                          digits=4)
                log(txt)
                with open(f"{dirout0}/report.txt", mode='a') as fp:
                    fp.write(txt +"\n\n\n----------------------")  
            except Exception as e: 
                loge(e)

        if ii > imax: break                 




####################################################################################
def pandas_to_hf_dataset_key(df: pd.DataFrame, shuffle=False, seed=41) -> Dataset:
    data = Dataset.from_pandas(df)
    if shuffle:
        data = data.shuffle(seed=seed)
    ids = []
    label2count = {}
    
    for id, example in enumerate(data):
        if example['label'] not in label2count:
            label2count[example['label']]=1
        else:
            label2count[example['label']]+=1
    
    label_key = list(label2count.keys())
    label_key = sorted(label_key, key=lambda x: label2count[x])
    
    label_key = {
        k: index for index, k in enumerate(label_key)
    }
    return Dataset.from_pandas(df), label_key


def save_hf_dataset(dataset: Dataset, path: str):
    dataset.save_to_disk(path)


def transform_dataset(dataset, classes, template = '{}'):
   new_dataset = {'sources':[], 'targets': [], 'labels': []}

   texts = dataset['text']
   labels = dataset['label']

   label2count = {}
   for label in labels:
       if label not in label2count:
           label2count[label]=1
       else:
           label2count[label]+=1
   count = len(labels)
   label2prob = {label:lc/count for label, lc in label2count.items()}
   unique_labels = list(label2prob)
   probs = list(label2prob.values())

   ids = list(range(len(labels)))
   for text, label_id in zip(texts, labels):
       label = classes[label_id]
       for i in range(len(classes)-1):
           new_dataset['sources'].append(text)
           new_dataset['targets'].append(template.format(label))
           new_dataset['labels'].append(1.)

       for i in range(len(classes)-1):
           neg_class_ = label
           while neg_class_==label:
               # neg_class_ = random.sample(classes, k=1)[0]
               neg_lbl = np.random.choice(unique_labels, p=probs)
               neg_class_ = classes[neg_lbl]

           new_dataset['sources'].append(text)
           new_dataset['targets'].append(template.format(neg_class_))
           new_dataset['labels'].append(-1.)
   return Dataset.from_dict(new_dataset)




def tokenize_and_align_label(example, tokenizer):
   hypothesis = example['targets']

   seq = example["sources"]+hypothesis

   tokenized_input = tokenizer(seq, truncation=True, max_length=512, 
                                                    padding="max_length")

   label = example['labels']
   if label==1.0:
       label = torch.tensor(1.0)
   elif label==0.0:
       label = torch.tensor(2.0)
   else:
       label = torch.tensor(0.0)
   tokenized_input['label'] = label
   return tokenized_input

def get_train_dataset(dataset, N):
    ids = []
    label2count = {}
    train_dataset = dataset['train'].shuffle(seed=41)
    for id, example in enumerate(train_dataset):
        if example['label'] not in label2count:
            label2count[example['label']]=1
        elif label2count[example['label']]>=N:
            continue
        else:
            label2count[example['label']]+=1
        ids.append(id)
    return train_dataset.select(ids)

def test123(val=""):
   print("ok")



##################################################################
def hf_model_get_mapping(model='mymodel'):
    from transformers import AutoConfig

    config = AutoConfig.from_pretrained(model)

    label2id = config.label2id
    id2label = config.id2label
    return label2id, id2label


@dataclass
class HFtask:
    text_classification     : str = "text-classification"
    token_classification    : str = "token-classification"
    question_answering      : str = "question-answering"
    summarization           : str = "summarization"
    translation             : str = "translation"
    text_generation         : str = "text-generation"
    fill_mask               : str = "fill-mask"
    zero_shot_classification: str = "zero-shot-classification"
    sentence_similarity     : str = "sentence-similarity"
    feature_extraction      : str = "feature-extraction"
    text2text_generation    : str = "text2text-generation"
    conversational          : str = "conversational"
    table_question_answering: str = "table-question-answering"


@dataclass
class HFproblemtype:
    CAUSAL_LM                  : str = "causal_lm"
    MASKED_LM                  : str = "masked_lm"
    SEQ_2_SEQ_LM               : str = "seq2seq_lm"
    SEQUENCE_CLASSIFICATION    : str = "sequence_classification"
    QUESTION_ANSWERING         : str = "question_answering"
    TOKEN_CLASSIFICATION       : str = "token_classification"
    MULTIPLE_CHOICE            : str = "multiple_choice"
    SEMANTIC_SEGMENTATION      : str = "semantic_segmentation"
    MULTI_LABEL_CLASSIFICATION : str = "multi_label_classification"
    MASK_GENERATION            : str = "mask_generation"
    SINGLE_LABEL_CLASSIFICATION: str = "single_label_classification"



def torch_init():

    try:
        print( torch.mps.current_allocated_memory() )
        torch.mps.empty_cache()
    except Exception as e :
       log(e)    




##################################################################
f1_metric       = evaluate.load("f1")
accuracy_metric = evaluate.load("accuracy")
clf_metric      = evaluate.combine(["accuracy", "f1", "precision", "recall"])



from evaluate import load
import numpy as np
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

def compute_metrics_v2(eval_pred):
    """  list of OneHot_vector !!! 2D vector
            from transformers.trainer_utils import EvalPrediction
            import json

            class CustomJSONEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, EvalPrediction):
                        return obj.__dict__
                    return super().default(obj)

            trainer.save_model(output_dir, save_function=lambda m, p: json.dump(m.state_dict(), p, cls=CustomJSONEncoder))

    """
    predictions, references = eval_pred   
    pred_labels =  np.argmax(predictions, axis=1)
    ref_labels  =  np.argmax(references,  axis=1)
    
    acc = accuracy.compute(predictions=pred_labels, references=ref_labels)
    # f1_scores = f1.compute(predictions=pred_labels, references=ref_labels, average=None)
    
    return {  "accuracy": acc["accuracy"],
              # "f1_per_class": list( f1_scores["f1"])
              }


def compute_accuracy_hamming(eval_pred):
    from sklearn.metrics import hamming_loss
    preds, labels = eval_pred


    pred_labels = [ [ pi>0.5 for pi in pred ] for pred in preds ] # np.argmax(predictions, axis=1)
    ham_list    = []
    for pred, label in zip(preds, labels):
        ham_values = 1 - hamming_loss(labels, preds)
        ham_list.append( ham_values)

    return {
        "accuracy_hamming": float( np.sum(ham_list) )
    }



def compute_metrics_multi(eval_pred):

   def sigmoid(x):
       return 1/(1 + np.exp(-x))

   preds_score, labels = eval_pred
   preds_proba = sigmoid(preds_score)
   preds  = (preds_proba > 0.5).astype(int).reshape(-1)
   labels = labels.astype(int).reshape(-1)
   dd =  clf_metric.compute(predictions=preds, references=labels)
   return dd


def compute_metrics_accuracy_multi(eval_pred):
    preds, labels = eval_pred
    preds = preds.argmax(axis=-1)

    ### Need to reformat
    preds  = preds.astype(int).reshape(-1)


    labels = labels.argmax(axis=-1)
    labels = labels.astype(int).reshape(-1)
    
    accuracy = accuracy_metric.compute(predictions=preds, references=labels)["accuracy"]
    
    return {   "accuracy": accuracy, }




###########################################################################
def compute_metrics_single(eval_pred, accuracy_fn):
   predictions, labels = eval_pred
   predictions = np.argmax(predictions, axis=1)
   return accuracy_fn.compute(predictions=predictions, references=labels)


def compute_metrics_f1_acc_single(eval_pred):
    predictions, labels = eval_pred
    predictions = predictions.argmax(axis=-1)
    
    accuracy = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1       = f1_metric.compute(predictions=predictions, references=labels, average="macro")["f1"]
    
    return {   "accuracy": accuracy,  "f1": f1, }
    
    
def compute_metrics_f1_acc_perclass_single(eval_pred):
    predictions, labels = eval_pred
    predictions = predictions.argmax(axis=-1)
    
    accuracy = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1       = f1_metric.compute(predictions=predictions, references=labels, average="macro")["f1"]
    
    # Compute F1 per class
    f1_per_class = f1_metric.compute(predictions=predictions, references=labels, average=None)['f1']
    
    # Create a dictionary with class names (adjust based on your number of classes)
    class_names       = [f"class_{i}" for i in range(len(f1_per_class))]
    f1_per_class_dict = {f"f1_{name}": score for name, score in zip(class_names, f1_per_class)}
    
    return {   "accuracy": accuracy,
               "f1": f1,
               **f1_per_class_dict
            }
    
        

###########################################################################
def classification_report_v2(y_true, y_pred, labels=None, target_names=None):

    report = classification_report(y_true, y_pred, labels=labels, target_names=target_names, output_dict=True)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    per_class_accuracy = cm.diagonal() / cm.sum(axis=1)
    
    for i, label in enumerate(labels or range(len(per_class_accuracy))):
        report[str(label)]['accuracy'] = per_class_accuracy[i]
    
    return report




def check1():
    """ 
      MoritzLaurer/deberta-v3-large-zeroshot-v2.0





    """










##################################################################
def dataset_reduce(data_dict, ntrain: int = 10, ntest: int = 5) :
    return DatasetDict({
        'train': data_dict['train'].select(range(ntrain)),
        'test':   data_dict['test'].select(range(ntest))
    })


def accelerator_init(device="cpu"):
    from accelerate import Accelerator
    try: 
       accelerator = Accelerator(cpu=True if device == "cpu" else False)
       return accelerator
    except Exception as e:
       log(e) 






# class MultiLabelMultiClassModel(nn.Module):
#     def __init__(self, num_labels_list):
#         super().__init__()
#         self.bert = SentenceTransformer('bert-base-uncased').bert
#         self.classification_heads = nn.ModuleList([
#             nn.Linear(self.bert.config.hidden_size, num_labels) for num_labels in num_labels_list
#         ])

#     def forward(self, input_ids, attention_mask):
#         outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
#         pooled_output = outputs.pooler_output
#         logits = [head(pooled_output) for head in self.classification_heads]
#         return logits

# # Example usage:
# model = MultiLabelMultiClassModel(num_labels_list=[3, 4])  # Assuming 3 classes for first label set, 4 for second
# input_ids = torch.tensor([[101, 1024, 102]])  # Example input
# attention_mask = torch.tensor([[1, 1, 1]])    # Example attention mask
# logits = model(input_ids, attention_mask)


def tes1():
   """ 
     
           
   """ 
   df = pd_read_file(  dirdata + "/raw_db/*train*.tsv", sep="\t")
   df.columns 
   cols = [ 'dt', 'com_name', 'com_name2',  'partnership_type',  'ind_name', 
            'cat_name', 'text', 'url', 
            'com_id', 'com_id2',  'ind_id',   'cat_id',  'partnership_acquisition', ]
      
   pd_to_file(df[cols], dirdata + "/train/activity_news_ok.parquet", sep="\t")   
      

   df['indcat'] = df['ind_name'] + "@" + df['cat_name']

   pd_to_file(df, dirdata + "/train/activity_news_ok.parquet", sep="\t") 
   
   dfm = df[ df.apply(lambda x: 'microsoft' in x['com_name'].lower() or 'microsoft' in x['com_name2'].lower()  , axis=1) ]


   dfm2 = df[ df.apply(lambda x: 'amazon web' in x['com_name'].lower() or 'amazon web' in x['com_name2'].lower()  , axis=1) ]


   dma = pd.concat((dfm, dfm2))
                                        
   pd_to_file(dfm, dirdata + "/train/activity_news_msft.parquet")   
      
   df[[ 'text', 'indcat' ]].drop_duplicates()    
   df[ df['cat_name'].isna() ]     
   dma[[ 'cat_name']].drop_duplicates()
   df[[ 'ind_name']].drop_duplicates()   


def run_v3():
    """ 
    
      python src/catfit.py run_v3      
      data = pd_filter1(data)    
      df1 = data.drop_duplicates('url')
        
      pd_to_file(df1['url'],  "./ztmp/data/urls/url_msft.csv", sep="\t")
      
            
    """
    text = "Angela Merkel is a politician in Germany and leader of the CDU"
    hypo = "This example is about {}"
    classes = ["politics", "economy", "entertainment", "environment"]
    
    classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33")
    output = classifier(text, classes, hypothesis_template=hypo, multi_label=True)
    print(output)

    ##############################################################
    dirdata = './ztmp/data/cats/cat_name/train/'
    data    = pd_read_file(dirdata)
    log(data.columns)
    data = data.rename(columns={'ind_name': 'label'}, )
    assert set(['text', "label"]).issubset(set(data.columns.tolist()))
    log(data.head(2))
    
    cc = Box({"n_train": 1000, "n_test": 2,})
        
    dataset, test_dataset, cc = dataset_setup_v1(data, cc)
    
    preds =[]
    for ii,example in enumerate(test_dataset):
        log(ii)
        pred = classifier(example['text'],cc.classes, hypothesis_template=hypo, multi_label=True )
        pred['true'] = example['label']
        preds.append(pred)
        # break     
    preds = pd.DataFrame(preds)    
    
    classes        = cc.classes
    preds['pred1'] = preds.apply(lambda x:   x['labels'][ argmax_score(x['scores'])] , axis=1) 
    preds['pred']  = preds.apply(lambda x:  cc.label2key[x['pred1']], axis=1) 
    
    
    pd_to_file(preds, "./ztmp/data/pred/cat_name/pred_deberta_zero/pred.parquet")
        
    log('pred_label:', preds)
    #log('true_label:', test_dataset['label'])
    print(classification_report(preds['true'].values, preds['pred'].values, 
                                            target_names=cc.classes,
                                            labels=range(len(cc.classes)),                                            
                                            digits=4))
    
    
def argmax_score(scores):
    return max(range(len(scores)), key=scores.__getitem__)

    
""" 


                          precision    recall  f1-score   support

 constructionandrealestate     0.2683    0.7333    0.3929        15
       aerospaceanddefence     0.3333    0.8125    0.4727        16
                    retail     0.3636    0.6667    0.4706        18
        foodandagriculture     0.6500    0.6842    0.6667        19
      hospitalityandtravel     0.8214    0.9200    0.8679        25
     pharmaandlifesciences     0.6111    0.6471    0.6286        68
    energyandclimatechange     0.4653    0.6104    0.5281        77
         salesandmarketing     0.5333    0.4167    0.4678        96
             manufacturing     0.5400    0.5347    0.5373       101
         financialservices     0.5403    0.6442    0.5877       104
educationandpublicservices     0.9390    0.6814    0.7897       113
         healthandwellness     0.8913    0.6074    0.7225       135
    sportsandentertainment     0.1616    0.5248    0.2471       141
                  security     0.7008    0.6312    0.6642       141
transportationandlogistics     0.4129    0.5924    0.4866       184
                      work     0.3474    0.4714    0.4000       350
     informationtechnology     0.6505    0.1062    0.1826       631

                  accuracy                         0.4418      2234
                 macro avg     0.5430    0.6050    0.5361      2234
              weighted avg     0.5569    0.4418    0.4297      2234

              


### Comprehenc 3 loop
                               precision    recall  f1-score   support

 CONSTRUCTION_AND_REAL_ESTATE     0.0000    0.0000    0.0000         0
        AEROSPACE_AND_DEFENCE     0.3333    1.0000    0.5000         1
                       RETAIL     0.0000    0.0000    0.0000         0
         FOOD_AND_AGRICULTURE     0.0000    0.0000    0.0000         0
       HOSPITALITY_AND_TRAVEL     1.0000    1.0000    1.0000         1
     PHARMA_AND_LIFE_SCIENCES     0.8571    0.6667    0.7500         9
    ENERGY_AND_CLIMATE_CHANGE     0.8462    0.5789    0.6875        19
          SALES_AND_MARKETING     0.5556    0.4167    0.4762        12
                MANUFACTURING     0.8750    0.7000    0.7778        10
           FINANCIAL_SERVICES     0.5000    0.8000    0.6154         5
EDUCATION_AND_PUBLIC_SERVICES     0.7857    0.7857    0.7857        14
          HEALTH_AND_WELLNESS     0.9286    0.7647    0.8387        17
     SPORTS_AND_ENTERTAINMENT     0.0882    0.3333    0.1395         9
                     SECURITY     0.2174    0.7143    0.3333         7
 TRANSPORTATION_AND_LOGISTICS     0.7500    0.4615    0.5714        13
                         WORK     0.4872    0.3800    0.4270        50
       INFORMATION_TECHNOLOGY     0.3077    0.1176    0.1702        34

                     accuracy                         0.4776       201
                    macro avg     0.5019    0.5129    0.4749       201
                 weighted avg     0.5807    0.4776    0.5039       201



    ## Zero Shot Classifier

    #!pip install transformers[sentencepiece]
    from transformers import pipeline
    text = "Angela Merkel is a politician in Germany and leader of the CDU"
    hypothesis_template = "This example is about {}"
    classes_verbalized = ["politics", "economy", "entertainment", "environment"]
    zeroshot_classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33")
    output = zeroshot_classifier(text, classes_verbalised, hypothesis_template=hypothesis_template, multi_label=False)
    print(output)


    https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v1.1-all-33




                               ind_name
    0                               NaN
    3                       Travel Tech
    16             Marketing Automation
    19       Smart Mobility Information
    30               Human Gene Editing
    ...                             ...
    19420  Online Freelancing Platforms
    23157       Infectious Disease Tech
    23658                Furniture Tech
    24442               Smart Packaging
    28560                   Bioprinting

    [157 rows x 1 columns]



    In [124]:    df[[ 'cat_name']].drop_duplicates()
    Out[124]: 
                                   cat_name
    0                                   NaN
    3                 Online search/booking
    16                      Marketing cloud
    19         Parking inventory management
    24           Marketing data & analytics
    ...                                 ...
    28149               IoT smart furniture
    28481            Veterinary diagnostics
    28560              Bioprinting services
    28735                Reusable packaging
    28905  Pure Play Biosimilars Developers

    [705 rows x 1 columns]




"""


   
      
###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




"""LOGS 



################### Accelerate setup ##########################

################### Start inference ##########################

################### Start Mapping ##########################
./ztmp/exp/L1_cat/deberV3/train/checkpoint-4000/eval//df_pred.parquet
                                                   text  ...                          pred
0     1. Automotive Cybersecurity\n2. Software Defin...  ...  transportation and logistics
1     1. Artificial Intelligence\n2. Generative AI\n...  ...                          work
2     1. Artificial Intelligence (AI) in Contract Ma...  ...           sales and marketing
3     1. AI Partnerships\n2. Microsoft AI Technology...  ...        information technology
4     1. Enterprise Automation\n2. Artificial Intell...  ...                          work
...                                                 ...  ...                           ...
7839                                       None.  None.  ...                        retail
7840                                       None.  None.  ...                        retail
7841                                       None.  None.  ...                        retail
7842                                       None.  None.  ...                        retail
7843                                       None.  None.  ...                        retail

[7844 rows x 5 columns]

################### Start Metrics ##########################
                               precision    recall  f1-score   support

                       retail     0.3110    0.7143    0.4333        91
 construction and real estate     0.8659    0.7172    0.7845        99
        aerospace and defence     0.9404    0.9281    0.9342       153
       hospitality and travel     0.8971    0.8798    0.8883       208
         food and agriculture     0.9286    0.9242    0.9264       211
                     security     0.8932    0.8708    0.8819       240
          sales and marketing     0.8555    0.9062    0.8801       320
     pharma and life sciences     0.9250    0.9509    0.9378       428
                         work     0.8610    0.7833    0.8203       443
                manufacturing     0.8197    0.8780    0.8479       492
          health and wellness     0.9251    0.9098    0.9174       543
     sports and entertainment     0.9680    0.9331    0.9502       583
education and public services     0.9282    0.9023    0.9151       645
           financial services     0.8848    0.9117    0.8981       657
    energy and climate change     0.9227    0.9261    0.9244       812
       information technology     0.9253    0.9129    0.9191       896
 transportation and logistics     0.9355    0.8651    0.8989      1023

                     accuracy                         0.8943      7844
                    macro avg     0.8698    0.8773    0.8681      7844
                 weighted avg     0.9040    0.8943    0.8977      7844


Accuracy: 0.8943141254462009
F1 Score: 0.8943141254462009




################### Start Metrics ##########################
                               precision    recall  f1-score   support

                       retail     0.6373    0.7143    0.6736        91
 construction and real estate     0.8659    0.7172    0.7845        99
        aerospace and defence     0.9404    0.9404    0.9404       151
         food and agriculture     0.0000    0.0000    0.0000       204
       hospitality and travel     0.0095    0.0097    0.0096       206
                     security     0.8932    0.8745    0.8837       239
          sales and marketing     0.8555    0.9206    0.8869       315
     pharma and life sciences     0.9250    0.9667    0.9454       421
                         work     0.8610    0.7977    0.8282       435
                manufacturing     0.8197    0.8816    0.8496       490
          health and wellness     0.9251    0.9199    0.9225       537
     sports and entertainment     0.9680    0.9379    0.9527       580
education and public services     0.9282    0.9108    0.9194       639
           financial services     0.8848    0.9215    0.9028       650
    energy and climate change     0.9227    0.9412    0.9318       799
       information technology     0.9253    0.9243    0.9248       885
 transportation and logistics     0.9355    0.8886    0.9114       996

                     accuracy                         0.8581      7737
                    macro avg     0.7822    0.7804    0.7804      7737
                 weighted avg     0.8596    0.8581    0.8584      7737



    00.sh: Create dataset
    python nlp/cats/few_shot_setfit.py  preprocess_scientific_text_dataset
                                                    text                              label
    0    We will consider the indefinite truncated mu...                        mathematics
    1    We discuss the Higgs mass and cosmological c...  high energy physics phenomenology
    2    While a lot of work in theoretical computer ...                   computer science
    3    We explore the physics of the gyro-resonant ...                       astrophysics
    ztmp/data/cats/scientific-text-classification/train/data.parquet
    (78631, 2)
    save successfull
    --------------------------
    01.sh run_train

    CUDA_VISIBLE_DEVICES=1 python nlp/cats/few_shot_setfit.py  run_train --cfg_name few_shot_setfit_scientific --dirout ./ztmp/exp_few_shot

    ###### User default Params   #######################################

    ################### Config Load  #############################
    Config: Loading  config/train.yml
    ###### Overide by config few_shot_setfit_scientific ####################
    {'model_name': 'knowledgator/comprehend_it-base', 'n_train': 1000, 'n_test': 10, 'N': 8, 'hf_args_train': {'output_dir': './ztmp/exp_few_shot/log_train', 'per_device_train_batch_size': 8, 'gradient_accumulation_steps': 1, 'optim': 'adamw_hf', 'save_steps': 100, 'logging_steps': 50, 'learning_rate': 2e-05, 'max_grad_norm': 2, 'max_steps': -1, 'num_train_epochs': 1, 'warmup_ratio': 0.2, 'evaluation_strategy': 'epoch', 'logging_strategy': 'epoch', 'save_strategy': 'epoch'}, 'hf_args_model': {'model_name': 'BAAI/bge-base-en-v1.5'}, 'cfg': 'config/train.yml', 'cfg_name': 'few_shot_setfit_scientific'}

    ###################load dataset #############################
                                   label                                               text
    0                        mathematics    We will consider the indefinite truncated mu...
    1  high energy physics phenomenology    We discuss the Higgs mass and cosmological c...
    {'model_name': 'knowledgator/comprehend_it-base', 'n_train': 1000, 'n_test': 10, 'N': 8, 'hf_args_train': {'output_dir': './ztmp/exp_few_shot/log_train', 'per_device_train_batch_size': 8, 'gradient_accumulation_steps': 1, 'optim': 'adamw_hf', 'save_steps': 100, 'logging_steps': 50, 'learning_rate': 2e-05, 'max_grad_norm': 2, 'max_steps': -1, 'num_train_epochs': 1, 'warmup_ratio': 0.2, 'evaluation_strategy': 'epoch', 'logging_strategy': 'epoch', 'save_strategy': 'epoch'}, 'hf_args_model': {'model_name': 'BAAI/bge-base-en-v1.5'}, 'cfg': 'config/train.yml', 'cfg_name': 'few_shot_setfit_scientific', 'dirout': './ztmp/exp_few_shot/240625/083652-few_shot_sentiment-1000', 'label2key': {'mathematics': 0, 'astrophysics': 1, 'quantum physics': 2, 'high energy physics phenomenology': 3, 'electrical engineering and systems science': 4, 'physics': 5, 'condensed matter': 6, 'statistics': 7, 'computer science': 8, 'high energy physics theory': 9}, 'classes': ['mathematics', 'astrophysics', 'quantum physics', 'high energy physics phenomenology', 'electrical engineering and systems science', 'physics', 'condensed matter', 'statistics', 'computer science', 'high energy physics theory']}
    train.shape: (990, 2)
    test.shape: (10, 2)

    ###############Prepare fewshot dataset#####################

    ###############Tokenizer dataset#####################
    Map: 100%|██████████████████████████████████████████████████████████████████████████████████████████| 1440/1440 [00:00<00:00, 1822.63 examples/s]

    ###################load model #############################
    ['mathematics', 'astrophysics', 'quantum physics', 'high energy physics phenomenology', 'electrical engineering and systems science', 'physics', 'condensed matter', 'statistics', 'computer science', 'high energy physics theory']
    Detected kernel version 5.4.0, which is below the recommended minimum of 5.5.0; this can cause the process to hang. It is recommended to upgrade the kernel to the minimum version or higher.
    {'model_name': 'knowledgator/comprehend_it-base', 'n_train': 1000, 'n_test': 10, 'N': 8, 'hf_args_train': {'output_dir': './ztmp/exp_few_shot/log_train', 'per_device_train_batch_size': 8, 'gradient_accumulation_steps': 1, 'optim': 'adamw_hf', 'save_steps': 100, 'logging_steps': 50, 'learning_rate': 2e-05, 'max_grad_norm': 2, 'max_steps': -1, 'num_train_epochs': 1, 'warmup_ratio': 0.2, 'evaluation_strategy': 'epoch', 'logging_strategy': 'epoch', 'save_strategy': 'epoch'}, 'hf_args_model': {'model_name': 'BAAI/bge-base-en-v1.5'}, 'cfg': 'config/train.yml', 'cfg_name': 'few_shot_setfit_scientific', 'dirout': './ztmp/exp_few_shot/240625/083652-few_shot_sentiment-1000', 'label2key': {'mathematics': 0, 'astrophysics': 1, 'quantum physics': 2, 'high energy physics phenomenology': 3, 'electrical engineering and systems science': 4, 'physics': 5, 'condensed matter': 6, 'statistics': 7, 'computer science': 8, 'high energy physics theory': 9}, 'classes': ['mathematics', 'astrophysics', 'quantum physics', 'high energy physics phenomenology', 'electrical engineering and systems science', 'physics', 'condensed matter', 'statistics', 'computer science', 'high energy physics theory'], 'metrics_trainer': {'train_runtime': 134.2872, 'train_samples_per_second': 9.651, 'train_steps_per_second': 1.206, 'total_flos': 341001104670720.0, 'train_loss': 0.4421150772659867, 'epoch': 1.0}}
    <_io.TextIOWrapper name='./ztmp/exp_few_shot/240625/083652-few_shot_sentiment-1000/config.json' mode='w' encoding='UTF-8'>
    {'loss': 0.4421, 'grad_norm': 2.330045700073242, 'learning_rate': 0.0, 'epoch': 1.0}                                                             
    {'eval_loss': 0.10409875214099884, 'eval_accuracy': 0.9652777777777778, 'eval_runtime': 4.5897, 'eval_samples_per_second': 31.374, 'eval_steps_per_second': 3.922, 'epoch': 1.0}                                                                                                                  
    {'train_runtime': 134.2872, 'train_samples_per_second': 9.651, 'train_steps_per_second': 1.206, 'train_loss': 0.4421150772659867, 'epoch': 1.0}  
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████| 162/162 [02:14<00:00,  1.21it/s]
    100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:01<00:00,  5.85it/s]
    [7, 5, 0, 3, 0, 8, 1, 9, 0, 4]
    [7, 6, 0, 3, 2, 8, 1, 9, 9, 0]
                                                precision    recall  f1-score   support

                                   mathematics     0.3333    0.5000    0.4000         2
                                  astrophysics     1.0000    1.0000    1.0000         1
                               quantum physics     0.0000    0.0000    0.0000         1
             high energy physics phenomenology     1.0000    1.0000    1.0000         1
    electrical engineering and systems science     0.0000    0.0000    0.0000         0
                                       physics     0.0000    0.0000    0.0000         0
                              condensed matter     0.0000    0.0000    0.0000         1
                                    statistics     1.0000    1.0000    1.0000         1
                              computer science     1.0000    1.0000    1.0000         1
                    high energy physics theory     1.0000    0.5000    0.6667         2

                                      accuracy                         0.6000        10
                                     macro avg     0.5333    0.5000    0.5067        10
                                  weighted avg     0.6667    0.6000    0.6133        10









"""










