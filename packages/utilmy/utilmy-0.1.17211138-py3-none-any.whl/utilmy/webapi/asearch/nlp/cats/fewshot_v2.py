"""  
## Dataset News

  text : 

  ind_name:  level 3 category,   100 labels.  F1 62 (low).  thats the issue    Hope to get  75     --> 1 model for level 3
  cat_name : level 4 category,  700 labels.  F1 60 (low). thats the issue     Hope to get  72.     --> 1 model for level 4


   level1 : 8 labels --> Easy. 90% accrucy
   level2 : 22 labels --> OK. 90% accuracy

  text2 =  "cat1: {level1}, cat2: {level2}.  {text] "




    --->  15000 samples   You need to split yourself.
        you can use ALL if ok for you.
        (if too slow, use less... )


We need Large Deberta version or Large Model for better F1

Not working super well..
      'knowledgator/comprehend_it-base'   --->  60 for F1  (level 3, level 4)


Some mdoels.

     https://huggingface.co/sileod/deberta-v3-large-tasksource-nli.  --> F1

     https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v2.0.  ---> F1

     ...
     https://huggingface.co/knowledgator/flan-t5-large-for-classification. --> F1



     Maybe Flan-T5


    Hiearchical Softmax Header fine tuning
       https://github.com/rbturnbull/hierarchicalsoftmax
       level1 --> level3 --> level4



"""
if "import":
    import os, sys, json, pandas as pd,numpy as np, gc
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

    from utils.util_exp import (exp_create_exp_folder, 
            exp_config_override, exp_get_filelist,json_save, log_pd)

    # from src.utils.utilmy_base import diskcache_decorator, log_pd
    from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob, config_load,
                       json_save, json_load, log, log2, loge)


#######################################################################
def data_filter_com(df, tag='microsoft'):
   def fun(x):
       x1 = x['com_name'].lower()
       x2 = x['com_name2'].lower()
       if tag  in x1:  return True
       if tag  in x2: return True
       #if 'amazon web' in x1: return True
       #if 'amazon web' in x2: return True
       return False
        
   df = df[ df.apply(lambda x:  fun(x) , axis=1) ]
   log('filtered',tag, df.shape)
   return df



########################################################################
# @diskcache_decorator
def data_inn_train(data0, cc): 
    """ 
         [15324 rows x 2 columns]    
    """
    data0 = data0.rename(columns={'ind_name': 'label'}, )    

    data = pd.DataFrame()
    ll = [ 'microsoft', 'amazon web', 'apple' ]
    for name in ll:
       d1   = data_filter_com( deepcopy(data0), tag=name)
       data = pd.concat((data, d1))


    data = data[['text', 'label']]
    data = data[ -data['label'].isna()] 
    # log(data['label'].values)
    log('No_NA label data', data.shape)
    ## data = data.groupby('label').apply(lambda x: x.sample(n=5, random_state=42, replace=True)).reset_index(drop=True)
    
    ##### Get label2key from all dataset
    _, label2key = pandas_to_hf_dataset_key(data)
    cc.label2key = label2key
    cc.key2label = {  idx: label       for label, idx in label2key.items()     }

    cc.classes = [''] * len(label2key)
    for label, idx in label2key.items()  :
        cc.classes[idx] = label 

    log('Nunique classes: ', len(cc.classes) ) 

    ##### Train test split     
    data = data.head(cc.n_train)
        
    data['label_text'] = data['label']
    data['label']      = data['label_text'].map(label2key)
    log('Nunique label: ',data.label.nunique() ) 
    log(str(cc)[:100] )
    
    train = data # data.head(len(data) - cc.n_test)
    test  = data.tail(cc.n_test)
    train_dataset = Dataset.from_pandas(train[['text', 'label']])
    test_dataset  = Dataset.from_pandas(test[['text',  'label']])
    
    from datasets import DatasetDict
    dataset = DatasetDict({"train":train_dataset,"test": test_dataset})
    log(f'train.shape: {train_dataset.shape}',)
    log(f'test.shape:  {test_dataset.shape}' ,)
    
    log('text:  ', test_dataset['text'][0]  )
    log('label: ', test_dataset['label'][0] )    
    
    return dataset,test_dataset, data, cc




def data_inn_pred(data):    
    data = data.rename(columns={'ind_name': 'label'}, )
    assert set(['text', "label"]).issubset(set(data.columns.tolist()))
    data = data[ -data['label'].isna()] 
    data['sort'] = 0
    data['sort'] = data.apply(lambda x: 10 if 'microsoft'  in x['text'].lower() else x['sort'] ,axis=1 )
    data['sort'] = data.apply(lambda x:  5 if 'amazon web' in x['text'].lower() else x['sort'] ,axis=1 )
    data = data.sort_values('sort', ascending=0)
    log("\n\n", data[['label', 'text' ]].head(2))
    log_pd(data)    
    return data



########################################################################
# @diskcache_decorator
def data_inn_train_v2(data0, cc): 
    """ 
         [15324 rows x 2 columns]    
    """
    #### Filter Data
    data = pd.DataFrame()
    ll = [ 'microsoft', ]
    for name in ll:
       d1   = data_filter_com( deepcopy(data0), tag=name)
       data = pd.concat((data, d1))
    log('Reduce Com: ', data.shape)


    ###### Label  Setup  #############################
    data = data.rename(columns={'ind_name': 'label'}, )    
    data = data[ -data['label'].isna()] 
    log('Label removeNA: ', data.shape)


    ###### Text Setup  ##############################
    def funm(x):    
        ss = f"Companies: {x['com_name']},  {x['com_name2']}. Title: {x['news_title']}. Text: {x['news_text']}. "
        ss = ss[:2048]
        return ss     
    data["text"] = data.apply(lambda x: funm(x), axis=1)
    log(data["text"].head(1))
  

    # log(data['label'].values)
    ## data = data.groupby('label').apply(lambda x: x.sample(n=5, random_state=42, replace=True)).reset_index(drop=True)
        
    ##### Get label2key from all dataset  ###################
    _, label2key = pandas_to_hf_dataset_key(data)
    cc.label2key = label2key
    cc.key2label = {  idx: label       for label, idx in label2key.items()     }

    cc.classes = [''] * len(label2key)
    for label, idx in label2key.items()  :
        cc.classes[idx] = label 
    log('Nunique classes: ', len(cc.classes) ) 


    ##### Train test split     
    data = data[['text', 'label']]
    data = data.head(cc.n_train)
        
    data['label_text'] = data['label']
    data['label']      = data['label_text'].map(label2key)
    log('Nunique label: ',data.label.nunique() ) 
    log(str(cc)[:100] )
    
    train = data # data.head(len(data) - cc.n_test)
    test  = data.tail(cc.n_test)


    train_dataset = Dataset.from_pandas(train[['text', 'label']])
    test_dataset  = Dataset.from_pandas(test[['text',  'label']])
    dataset = DatasetDict({"train":train_dataset,"test": test_dataset})
    log(f'train.shape: {train_dataset.shape}',)
    log(f'test.shape:  {test_dataset.shape}' ,)
    
    log('text:  ', test_dataset['text'][0]  )
    log('label: ', test_dataset['label'][0] )    
    
    return dataset,test_dataset, data, cc



def data_inn_pred_v2(data):    
    log("###prepro")
    data = data.rename(columns={'ind_name': 'label'}, )
    assert set(['text', "label"]).issubset(set(data.columns.tolist()))
    data = data[ -data['label'].isna()] 
    data['sort'] = 0
    data['sort'] = data.apply(lambda x: 10 if 'microsoft'  in x['text'].lower() else x['sort'] ,axis=1 )
    data['sort'] = data.apply(lambda x:  5 if 'amazon web' in x['text'].lower() else x['sort'] ,axis=1 )
    data = data.sort_values('sort', ascending=0)
    log_pd(data)


    ###### Text Setup  ##############################
    def funm(x):    
        ss = f"Companies: {x['com_name']},  {x['com_name2']}. Title: {x['news_title']}. Text: {x['news_text']}. "
        ss = ss[:2048]
        return ss     
    data["text"] = data.apply(lambda x: funm(x), axis=1)
    log(data["text"].head(1))



    log("\n\n", data[['label', 'text' ]].head(1).T)
    log_pd(data)    
    return data




###############################################################################
######## Segment Training   ###################################################
# @diskcache_decorator
def dataset_setup_cat(data0, cc): 
    """ 
         [15324 rows x 2 columns]    
    """
    data0 = data0.rename(columns={'ind_name': 'label'}, )    
    data = data0
    # data = pd.DataFrame()
    # ll = [ 'microsoft', 'amazon web', 'apple' ]
    # for name in ll:
    #    d1   = data_filter_com( deepcopy(data0), tag=name)
    #    data = pd.concat((data, d1))

    # data = data[ -data['label'].isna()] 
    # log(data[[ 'ind_name', 'label' ]])


    # log("##### Enhance text")
    # log(data.columns)
    # data['text0'] = data['text']
    # data['text']  = data.apply(lambda x: f"Companies: {x['com_name']}, {x['com_name2']}.  inn: {x['ind_name']}. {x['text0']} ",  axis=1)
    # log(data['text'])    


    # data = data[['text', 'label']]
    # log(data['label'].values)
    log('No_NA label data', data.shape)
    ## data = data.groupby('label').apply(lambda x: x.sample(n=5, random_state=42, replace=True)).reset_index(drop=True)
    
    log("##### Get label2key from all dataset")
    _, label2key = pandas_to_hf_dataset_key(data)
    cc.label2key = label2key
    cc.key2label = { idx: label   for label, idx in label2key.items()     }
    cc.classes   = [''] * len(label2key)
    for label, idx in label2key.items()  :
        cc.classes[idx] = label 
    log('Nunique classes: ', len(cc.classes) ) 
    log(str(cc.classes)[:100])
    
    log("##### Labels ")    
    dlabel = data['label'].value_counts(sort=True, ascending=False).reset_index(name='count')
    dlabel.columns=['label', 'count']
    log(dlabel)
    assert dlabel[['label', 'count']].shape
    pd_to_file(dlabel, cc.dirout + '/dlabel.csv', show=1)

    dlabel = dlabel[dlabel['count'] > 3 ]
    catlist = dlabel['label'].values
    log(dlabel)
    data = data[ data['label'].isin(catlist) ]    
    log("Nsamples", len(data))

    ##### Train test split     
    data = data.head(cc.n_train)
        
    data['label_text'] = data['label']
    data['label']      = data['label_text'].map(label2key)
    log('Nunique label: ',data.label.nunique() ) 
    log(str(cc)[:100] )
    
    train = data # data.head(len(data) - cc.n_test)
    test  = data.tail(cc.n_test)
    train_dataset = Dataset.from_pandas(train[['text', 'label']])
    test_dataset  = Dataset.from_pandas(test[['text',  'label']])
    
    from datasets import DatasetDict
    dataset = DatasetDict({"train":train_dataset,"test": test_dataset})
    log(f'train.shape: {train_dataset.shape}',)
    log(f'test.shape:  {test_dataset.shape}' ,)
    
    log('text:  ', test_dataset['text'][0]  )
    log('label: ', test_dataset['label'][0] )    
    
    return dataset,test_dataset, data, cc






###############################################################################    
def run_train(cfg='config/train.yml', cfg_name='cat_name', 
              dirout: str="./ztmp/exp",
              dirdata: str='./ztmp/data/cats/cat_name/train/',
              istest=1 ):
    """ 
    
       python src/catfit.py  run_train  --dirout "./ztmp/exp/indu_name5"  --istest 0
          

          9000 samples

          
       
    """
    log("\n###### User default Params   #######################################")
    if "config":    
        cc = Box()
        # cc.model_name='BAAI/bge-base-en-v1.5'   
        cc.model_name = 'knowledgator/comprehend_it-base'  
        cc.task = "indu_class"  
        cc.device = "cuda"          
        ### Need sample to get enough categories
        cc.n_train = 5000  if istest == 1 else 1000000000
        cc.n_test   = 500  if istest == 1 else int(cc.n_train*0.1)
        cc.N = 8 # few shot : per sample/class training (select only few sample to train)
        #### Train Args
        aa = Box({})
        aa.output_dir                  = f"{dirout}/log_train"
        aa.per_device_train_batch_size = 8
        aa.gradient_accumulation_steps = 1
        aa.optim                       = "adamw_hf"
        aa.save_steps                  = min(100, cc.n_train-1)
        aa.logging_steps               = min(50,  cc.n_train-1)
        aa.learning_rate               = 2e-5
        aa.max_grad_norm               = 2
        aa.max_steps                   = 2000
        aa.num_train_epochs            = 1
        aa.warmup_ratio                = 0.2 # 20%  total step warm-up
        # lr_schedulere_type='constant'
        aa.evaluation_strategy = "steps"
        aa.eval_steps = 500
        aa.save_steps = 500
        aa.logging_strategy    = "epoch"
        aa.save_strategy       = "steps"
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
    log(data.columns)
    log(data.head(1).T)
    
        
    dataset, test_dataset, data, cc = dataset_setup_cat(data, cc)
    # dataset, test_dataset, data, cc = dataset_setup_inn_v2(data, cc)
    
    
    
    
    
    assert set(['text', "label"]).issubset(set(data.columns.tolist()))    
    log("\n###############Prepare fewshot dataset#####################")
    train_dataset = get_train_dataset(dataset, cc.N)

    log("\n###############Tokenizer dataset###########################")
    tokenizer     = AutoTokenizer.from_pretrained(cc.model_name)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    print(train_dataset)
    train_dataset = train_dataset.map(partial(pretokenizer, tokenizer=tokenizer))
    
    # print(train_dataset)
    # print(train_dataset[0])
    map_label_to_tokenized ={}
    l = []
    for i in train_dataset:
        l.append(
            len(i['input_ids'])
        )
        if i['label'] not in map_label_to_tokenized:
            map_label_to_tokenized[cc.classes[i['label']]]  = tokenizer_text(
                cc.classes[i['label']], tokenizer
            )
    print(pd.DataFrame(l).describe())
    print(train_dataset)
    # exit(0)
    dataset       = transform_dataset(train_dataset, cc.classes)
    print(dataset)
    print(dataset[0])
    # exit(0)
    tk_dataset = dataset.map(partial(tokenize_and_align_label, tokenizer=tokenizer, dataset_roots=train_dataset,
                                    map_label_to_tokenized=map_label_to_tokenized))
    tk_dataset = tk_dataset.train_test_split(test_size=0.1)    
    tk_dataset = tk_dataset.with_format("torch", device= cc.device)

    if istest > 0:
        tk_dataset = dataset_reduce(tk_dataset, ntrain= 2000, ntest = 100) 
       
       
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
        compute_metrics = partial(compute_metrics, accuracy_fn=accuracy),
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
        imin,imax = 0, 500

    model_eval(model2, test_dataset, cc, dirout, imin=imin, imax=imax, istrain=1)              




    
def run_infer(cfg='config/train.yml', cfg_name='classifier_data', 
              dirout:  str = "./ztmp/exp",
              dirdata: str = './ztmp/data/cats/cat_name/train/',
              istest=1):
    """ 
    
       python src/catfit.py  run_infer --istest 0
          
       
    
    """
    log("\n###### User default Params   #######################################")
    dirdata  = './ztmp/data/cats/cat_name/train/'
    # dirmodel = './ztmp/exp/ind_name2/240626/025203-few_shot_sentiment-5000'
    # dirmodel = './ztmp/exp/ind_name3/240626/171851-ind_class-1000000000'

    ## with full text
    dirmodel = './ztmp/exp/indu_name5/240627/015210-indu_class-1000000000'
    

    


    log("\n################### Config Load  #############################")
    cc =  json_load(dirmodel +"/model/meta.json")
    cc = Box(cc)
    log(cc.keys() )
    device = torch_device("mps")

    
    log("\n###################load dataset #############################")
    data = pd_read_file(dirdata)
    log_pd(data)
    log(data.head(1).T)


    # data = data_inn_clean(data)
    data = data_inn_pred_v2(data)



    dataset = Dataset.from_pandas(data[['text', 'label']])        
    log("\n###############Tokenizer dataset###########################")
    tokenizer     = AutoTokenizer.from_pretrained(cc.model_name)

           
    log("\n###################load model #############################")
    log(str(cc.classes)[:100])
    #accuracy = evaluate.load("accuracy")
    model = pipeline("zero-shot-classification",
                      model=f"{cc.dirout}/model",tokenizer=tokenizer, device=device)

    log("\n###################Accelerate setup ##########################")
    accelerator = accelerator_init(device=device)
    model       = accelerator.prepare(model)
            
    imin=  0        
    imax = 10000
    if istest == 1:
        imin,imax = 0, 2

    log("\n################### Start inference ##########################")
    dirout = dirmodel 
    model_eval(model, dataset, cc, dirout, imin=imin, imax= imax, istrain=0)

            
def model_eval(model, dataset, cc, dirout, imin=0, imax=100000, istrain=0): 
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

            preds['pred']     = preds.apply(lambda x:  x['pred_labels'][ argmax_score(x['pred_scores'])] , axis=1) 
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


def transform_dataset(dataset, classes, template = '{}', max_sample_with_repeat_true_label=5):
   new_dataset = {'sources':[], 'targets': [], 'labels': [], 'id_of_root': []}

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
   for index, text, label_id in zip(ids, texts, labels):
       label = classes[label_id]
       for i in range(min(len(classes)-1, max_sample_with_repeat_true_label)):
           # Why we need len(class)-1 sample?? for balanced datasets
           # I prefer we limit to 5 samples.
           new_dataset['sources'].append(text)
           new_dataset['targets'].append(template.format(label))
           new_dataset['labels'].append(1.)
           new_dataset['id_of_root'].append(index)
       for i in range(len(classes)-1):
           neg_class_ = label
           while neg_class_==label:
               # neg_class_ = random.sample(classes, k=1)[0]
               neg_lbl = np.random.choice(unique_labels, p=probs)
               neg_class_ = classes[neg_lbl]

           new_dataset['sources'].append(text)
           new_dataset['targets'].append(template.format(neg_class_))
           new_dataset['labels'].append(-1.)
           new_dataset['id_of_root'].append(index)
   return Dataset.from_dict(new_dataset)


def compute_metrics(eval_pred, accuracy_fn):
   predictions, labels = eval_pred

   predictions = np.argmax(predictions, axis=1)

   return accuracy_fn.compute(predictions=predictions, references=labels)


def pretokenizer(example, tokenizer):
    tokenized_input = tokenizer(example['text'])

    for key in tokenized_input:
        example[key] = tokenized_input[key]
    return example

def tokenizer_text(text, tokenizer):
    # print(text)
    return tokenizer(text)


def tokenize_and_align_label(example, tokenizer, dataset_roots, map_label_to_tokenized):
   """
    think about optimized tokenizer
        why we need tokenizer many sample with same text for many times
        Idea cached all sources text and targets text
            But targets text is very short, so we can simply ignore this
        we need map_source_to_index_of_root_dataset
        So we can easy access to the tokenizer_datasets
        -> reduce from 40mins -> 3mins very interesting.
   """
   
   assert 'id_of_root' in example
   hypothesis = example['targets']
   seq = example["sources"]+hypothesis
    # This is bug here: seq = example["sources"]+hypothesis ->> If len of sources > 512, we will ignore target-label 
    # Very dangerous 
    # -> cached pretokenzed also help here
   tokenized_input = dataset_roots[example['id_of_root']]
   
   tokenized_target_cate = map_label_to_tokenized[hypothesis]
   
   inputs_ids_text = tokenized_input['input_ids'] 
   input_ids_target_cate = tokenized_target_cate['input_ids']
   
   if len(inputs_ids_text) + len(input_ids_target_cate) > 512:
       inputs_ids_text = inputs_ids_text[:512 - len(input_ids_target_cate)]
    
   input_ids = inputs_ids_text + input_ids_target_cate
   token_type_ids = [0,] * len(input_ids)
   attention_mask = [1,]  * len(input_ids)

   label = example['labels']
   if label==1.0:
       label = torch.tensor(1.0)
   elif label==0.0:
       label = torch.tensor(2.0)
   else:
       label = torch.tensor(0.0)
   tokenized_input = {
       'label': label,
       'input_ids': input_ids,
       'token_type_ids': token_type_ids,
       'attention_mask': attention_mask
   }
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


####
    Category fine tunning






                                                precision    recall  f1-score   support

                                 Humanoid Robots     0.0000    0.0000    0.0000         0
                                   Wearable Tech     0.0000    0.0000    0.0000         0
                                      EV Economy     0.0000    0.0000    0.0000         0
                             Truck inn Tech     0.0000    0.0000    0.0000         0
                            Satellite Management     0.0000    0.0000    0.0000         0
                                 Social Commerce     0.0000    0.0000    0.0000         0
                   B2B SaaS Management Platforms     0.0000    0.0000    0.0000         0
                       InsurTech: Personal Lines     0.0000    0.0000    0.0000         0
                                   Pet Care Tech     0.0000    0.0000    0.0000         0
                                     Mining Tech     0.0000    0.0000    0.0000         0
               Clinical Decision Support Systems     1.0000    1.0000    1.0000         1
                   Last-mile Delivery Automation     1.0000    1.0000    1.0000         1
                          Retail inn Robots     1.0000    1.0000    1.0000         1
                                         SME CRM     1.0000    1.0000    1.0000         1
                                Digital Wellness     0.2000    1.0000    0.3333         1
                Waste Recovery & Management Tech     0.5000    1.0000    0.6667         1
               Space Travel and Exploration Tech     0.2500    1.0000    0.4000         1
                             Cell & Gene Therapy     1.0000    1.0000    1.0000         1
           Smart Homes: Energy & Water Solutions     1.0000    1.0000    1.0000         1
                                     Beauty Tech     0.0000    0.0000    0.0000         0
                                      Food Waste     1.0000    1.0000    1.0000         1
                                Alternative Data     0.0000    0.0000    0.0000         0
                       Clinical Trial Technology     0.6667    1.0000    0.8000         2
                             Ecommerce Platforms     0.5000    1.0000    0.6667         2
                      Smart Mobility Information     0.1538    1.0000    0.2667         2
                          Content Creation Tools     1.0000    1.0000    1.0000         2
                       Contract Management Tools     0.5000    1.0000    0.6667         2
                            Capital Markets Tech     0.0000    0.0000    0.0000         0
                                DevOps Toolchain     0.0000    0.0000    0.0000         0
                   Retail Trading Infrastructure     1.0000    1.0000    1.0000         1
       Energy Optimization & Management Software     0.3333    1.0000    0.5000         1
                                 Cyber Insurance     1.0000    1.0000    1.0000         2
               Natural Language Processing Tools     0.4000    1.0000    0.5714         2
                                        Age Tech     0.6667    1.0000    0.8000         2
                                Automated Stores     0.5000    1.0000    0.6667         2
                              Low-code Platforms     0.3333    1.0000    0.5000         1
                              Facial Recognition     0.5000    1.0000    0.6667         3
                         Next-gen Semiconductors     0.7500    1.0000    0.8571         3
                                No-code Software     0.5000    0.6667    0.5714         3
                             Smart Security Tech     0.6000    1.0000    0.7500         3
                   Workflow Automation Platforms     0.0000    0.0000    0.0000         0
                       Hospital Interoperability     0.2500    1.0000    0.4000         1
                      Customer Service Platforms     0.0000    0.0000    0.0000         0
                     Business Expense Management     1.0000    1.0000    1.0000         1
                              Buy Now, Pay Later     0.6667    1.0000    0.8000         2
                                   Shipping Tech     1.0000    1.0000    1.0000         4
                                  Logistics Tech     0.5000    0.2500    0.3333         4
                          Climate Risk Analytics     1.0000    1.0000    1.0000         2
                           Digital Privacy Tools     0.7143    1.0000    0.8333         5
                               Next-gen Displays     0.8333    1.0000    0.9091         5
                        Next-gen Medical Devices     1.0000    1.0000    1.0000         2
                    Identity & Access Management     0.2000    1.0000    0.3333         1
                                     Sports Tech     1.0000    0.6667    0.8000         3
                               Supply Chain Tech     0.6667    0.8000    0.7273         5
                                  Web3 Ecosystem     0.0000    0.0000    0.0000         2
                                Hydrogen Economy     1.0000    1.0000    1.0000         3
                      Sales Engagement Platforms     0.5714    1.0000    0.7273         4
                       InsurTech: Infrastructure     1.0000    0.4000    0.5714         5
                       Smart Building Technology     1.0000    1.0000    1.0000         6
                           Preventive Healthcare     0.6000    0.5000    0.5455         6
                                       LegalTech     1.0000    0.5000    0.6667         2
                                   Military Tech     0.6000    1.0000    0.7500         3
                 Enterprise Blockchain Solutions     0.6667    0.8571    0.7500         7
                              Alternative Energy     0.4000    1.0000    0.5714         2
                              Precision Medicine     0.1667    1.0000    0.2857         1
                                     Travel Tech     1.0000    1.0000    1.0000         5
                    Decentralized Finance (DeFi)     0.7500    0.6000    0.6667         5
                      Remote Work Infrastructure     0.5455    1.0000    0.7059         6
                                         Esports     0.7778    0.7778    0.7778         9
                          FinTech Infrastructure     0.4000    0.3333    0.3636         6
                                      Telehealth     1.0000    0.6667    0.8000         9
    Carbon Capture, Utilization & Storage (CCUS)     0.7143    1.0000    0.8333         5
                               Foundation Models     0.0000    0.0000    0.0000         3
                               Cloud-native Tech     0.6154    0.8000    0.6957        10
                                   Smart Farming     1.0000    1.0000    1.0000        11
                                    EdTech: K-12     0.6667    0.6667    0.6667         9
                                   Smart Factory     0.4444    0.5714    0.5000         7
                               AI Drug Discovery     1.0000    0.4167    0.5882        12
                             Hospital Management     0.0000    0.0000    0.0000         0
                      EdTech: Corporate Learning     1.0000    0.4545    0.6250        11
                        Cloud Optimization Tools     0.3333    0.4167    0.3704        12
                  Metaverse Experience Platforms     1.0000    0.1111    0.2000        18
                                   Higher EdTech     0.0000    0.0000    0.0000         3
                                    Digital Twin     0.8571    0.7059    0.7742        17
                        Next-gen Mobile Networks     0.2857    1.0000    0.4444         4
                    Generative AI Infrastructure     0.0000    0.0000    0.0000         0
                               Quantum Computing     1.0000    0.9565    0.9778        23
                                Extended Reality     0.5769    0.8824    0.6977        17
                            Marketing Automation     1.0000    0.5000    0.6667        10
                      Carbon Management Software     0.8750    0.5385    0.6667        13
                 Machine Learning Infrastructure     1.0000    0.1538    0.2667        13
                                       Auto Tech     1.0000    0.5833    0.7368        24
                 Data Infrastructure & Analytics     1.0000    0.5000    0.6667        16
                      Generative AI Applications     0.5000    0.3333    0.4000         3
                          Next-gen Cybersecurity     0.9091    0.7143    0.8000        28
                               Remote Work Tools     0.7778    0.2917    0.4242        24
                                  Edge Computing     0.9697    0.6667    0.7901        48

                                        accuracy                         0.6640       500
                                       macro avg     0.5690    0.6421    0.5546       500
                                    weighted avg     0.8079    0.6640    0.6765       500




                                                precision    recall  f1-score   support

                               quantum physics     0.5826    0.7444    0.6537        90
                              condensed matter     0.7143    0.1010    0.1770        99
    electrical engineering and systems science     0.6161    0.7667    0.6832        90
             high energy physics phenomenology     0.6571    0.2614    0.3740        88
                                    statistics     0.6990    0.7273    0.7129        99
                                       physics     0.3239    0.6196    0.4254        92
                                   mathematics     0.5899    0.8678    0.7023       121
                                  astrophysics     0.9020    0.8762    0.8889       105
                              computer science     0.6796    0.6034    0.6393       116
                    high energy physics theory     0.4839    0.3000    0.3704       100

                                      accuracy                         0.5950      1000
                                     macro avg     0.6248    0.5868    0.5627      1000
                                  weighted avg     0.6287    0.5950    0.5700      1000





    pred_label:                                              sequence  ... pred
    0   This integration allows clients to leverage th...  ...   52
    1   Teleport has signed a Strategic Collaboration ...  ...   90
    2   Allianz will move parts of the global insuranc...  ...   19
    3   To launch the Digital Market Center to develop...  ...   11
    4   It utilized Microsoft's design and engineering...  ...   71
    ..                                                ...  ...  ...
    95  ARxVision, a pioneer in assistive technology, ...  ...   99
    96  AWS collaborates with Accenture to launch a su...  ...   19
    97  Axelar and Microsoft have joined forces to pro...  ...  100
    98  Accounting software FloQast has integrated Mic...  ...   19
    99  Workato and AWS sign a multi-year Strategic Co...  ...   19

    [100 rows x 6 columns]



                                                  precision    recall  f1-score   support

                               AI Drug Discovery     0.0000    0.0000    0.0000         0
                          Additive Manufacturing     0.0000    0.0000    0.0000         0
                                        Age Tech     0.0000    0.0000    0.0000         0
                                Alternative Data     0.0000    0.0000    0.0000         0
                              Alternative Energy     0.0000    0.0000    0.0000         0
                                       Auto Tech     0.0000    0.0000    0.0000         0
                                Automated Stores     0.0000    0.0000    0.0000         0
                   B2B SaaS Management Platforms     0.0000    0.0000    0.0000         0
                                     Beauty Tech     0.0000    0.0000    0.0000         0
                     Business Expense Management     0.0000    0.0000    0.0000         0
                              Buy Now, Pay Later     0.0000    0.0000    0.0000         0
                            Capital Markets Tech     0.0000    0.0000    0.0000         0
    Carbon Capture, Utilization & Storage (CCUS)     0.0000    0.0000    0.0000         0
                      Carbon Management Software     0.0000    0.0000    0.0000         0
                             Cell & Gene Therapy     0.0000    0.0000    0.0000         0
                          Climate Risk Analytics     0.0000    0.0000    0.0000         0
               Clinical Decision Support Systems     0.0000    0.0000    0.0000         0
                       Clinical Trial Technology     0.0000    0.0000    0.0000         0
                        Cloud Optimization Tools     0.0000    0.0000    0.0000         0
                               Cloud-native Tech     0.0000    0.0000    0.0000         0
                           Commercial Drone Tech     0.0000    0.0000    0.0000         0
                               Construction Tech     0.0000    0.0000    0.0000         0
                          Content Creation Tools     0.0000    0.0000    0.0000         0
                       Contract Management Tools     0.0000    0.0000    0.0000         0
                      Customer Service Platforms     0.0000    0.0000    0.0000         0
                                 Cyber Insurance     0.0000    0.0000    0.0000         0
                 Data Infrastructure & Analytics     0.0000    0.0000    0.0000         0
                    Decentralized Finance (DeFi)     0.0000    0.0000    0.0000         0
                                DevOps Toolchain     0.0000    0.0000    0.0000         0
                           Digital Privacy Tools     0.0000    0.0000    0.0000         0
                                    Digital Twin     0.0000    0.0000    0.0000         0
                                Digital Wellness     0.0000    0.0000    0.0000         0
                                      EV Economy     0.0000    0.0000    0.0000         0
                             Ecommerce Platforms     0.0000    0.0000    0.0000         0
                      EdTech: Corporate Learning     0.0000    0.0000    0.0000         0
                                    EdTech: K-12     0.0000    0.0000    0.0000         0
                                  Edge Computing     0.0000    0.0000    0.0000         0
       Energy Optimization & Management Software     0.0000    0.0000    0.0000         0
                 Enterprise Blockchain Solutions     0.0000    0.0000    0.0000         0
                                         Esports     0.0000    0.0000    0.0000         0
                                Extended Reality     0.0000    0.0000    0.0000         0
                              Facial Recognition     0.0000    0.0000    0.0000         0
                          FinTech Infrastructure     0.0000    0.0000    0.0000         0
                                      Food Waste     0.0000    0.0000    0.0000         0
                               Foundation Models     0.0000    0.0000    0.0000         0
                      Generative AI Applications     0.0000    0.0000    0.0000         0
                    Generative AI Infrastructure     0.0000    0.0000    0.0000         0
                                   Higher EdTech     0.0000    0.0000    0.0000         0
                       Hospital Interoperability     0.0000    0.0000    0.0000         0
                             Hospital Management     0.0000    0.0000    0.0000         0
                                 Humanoid Robots     0.0000    0.0000    0.0000         0
                                Hydrogen Economy     0.0000    0.0000    0.0000         0
                    Identity & Access Management     1.0000    0.5000    0.6667         2
                       InsurTech: Infrastructure     0.0000    0.0000    0.0000         2
                       InsurTech: Personal Lines     0.0000    0.0000    0.0000         2
                   Last-mile Delivery Automation     0.0000    0.0000    0.0000         2
                                       LegalTech     1.0000    0.5000    0.6667         2
                                  Logistics Tech     1.0000    0.5000    0.6667         2
                              Low-code Platforms     0.0000    0.0000    0.0000         2
                 Machine Learning Infrastructure     0.0000    0.0000    0.0000         2
                            Marketing Automation     1.0000    1.0000    1.0000         2
                  Metaverse Experience Platforms     0.0000    0.0000    0.0000         2
                                   Military Tech     1.0000    1.0000    1.0000         2
                                     Mining Tech     1.0000    0.5000    0.6667         2
               Natural Language Processing Tools     0.5000    0.5000    0.5000         2
                          Next-gen Cybersecurity     0.0000    0.0000    0.0000         2
                               Next-gen Displays     0.0000    0.0000    0.0000         2
                        Next-gen Medical Devices     0.5000    0.5000    0.5000         2
                        Next-gen Mobile Networks     0.0000    0.0000    0.0000         2
                         Next-gen Semiconductors     0.0000    0.0000    0.0000         2
                                No-code Software     0.0000    0.0000    0.0000         2
                                   Pet Care Tech     0.0000    0.0000    0.0000         2
                              Precision Medicine     1.0000    0.5000    0.6667         2
                           Preventive Healthcare     0.0000    0.0000    0.0000         2
                               Quantum Computing     1.0000    0.5000    0.6667         2
                      Remote Work Infrastructure     1.0000    0.5000    0.6667         2
                               Remote Work Tools     0.0000    0.0000    0.0000         2
                    Restaurant inn Robotics     1.0000    1.0000    1.0000         2
                          Retail inn Robots     0.0000    0.0000    0.0000         2
                   Retail Trading Infrastructure     0.0000    0.0000    0.0000         2
                                         SME CRM     0.0000    0.0000    0.0000         2
                      Sales Engagement Platforms     0.0000    0.0000    0.0000         2
                            Satellite Management     1.0000    1.0000    1.0000         2
                            Serverless Computing     0.0000    0.0000    0.0000         2
                                   Shipping Tech     1.0000    1.0000    1.0000         2
                       Smart Building Technology     1.0000    1.0000    1.0000         2
                                   Smart Factory     1.0000    0.5000    0.6667         2
                                   Smart Farming     0.0000    0.0000    0.0000         2
           Smart Homes: Energy & Water Solutions     0.0000    0.0000    0.0000         2
                      Smart Mobility Information     0.5000    0.5000    0.5000         2
                             Smart Security Tech     0.3333    0.5000    0.4000         2
                                 Social Commerce     0.0000    0.0000    0.0000         2
               Space Travel and Exploration Tech     1.0000    0.5000    0.6667         2
                                     Sports Tech     1.0000    1.0000    1.0000         2
                               Supply Chain Tech     1.0000    1.0000    1.0000         2
                                      Telehealth     0.3333    0.5000    0.4000         2
                                     Travel Tech     1.0000    1.0000    1.0000         2
                             Truck inn Tech     1.0000    1.0000    1.0000         2
                Waste Recovery & Management Tech     1.0000    1.0000    1.0000         2
                                   Wearable Tech     0.6667    1.0000    0.8000         2
                                  Web3 Ecosystem     1.0000    0.5000    0.6667         2
                   Workflow Automation Platforms     0.0000    0.0000    0.0000         2

                                        accuracy                         0.3900       100
                                       macro avg     0.2337    0.1912    0.2036       100
                                    weighted avg     0.4767    0.3900    0.4153       100




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
