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

        
    ### Dataset Create 
        We will work on parquet file 
        +> Firstly, We need to download raw dataset from hf: https://huggingface.co/datasets/knowledgator/Scientific-text-classification
        +> Secondly, We save it to parquet file ztmp/data/cats/scientific-text-classification/train/data.parquet
        
    ### Usage:
        cd asearch
        export PYTHONPATH="$(pwd)"  ### Need for correct import

        python nlp/cats/few_shot_setfit.py  preprocess_scientific_text_dataset

    ### Usage scientific dataset
        cd asearch 
        export PYTHONPATH="$(pwd)"
        python nlp/cats/few_shot_setfit.py  run_train --cfg_name few_shot_setfit_scientific --dirout ./ztmp/exp_few_shot
        

"""

import os, sys, json
import copy
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from sklearn.metrics import classification_report
from datasets import Dataset

import pandas as pd
from utilmy import pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob, config_load
from utilmy import log, log2
from typing import Optional, Union
from box import Box

from transformers import TrainingArguments, Trainer
from transformers import DataCollatorWithPadding
from datasets import Dataset
import random
import torch
import evaluate
import numpy as np
from functools import partial

from transformers import pipeline
from sklearn.metrics import classification_report
from tqdm import tqdm
from utils.util_exp import (exp_create_exp_folder, exp_config_override, exp_get_filelist, json_save,
                                log_pd)

def preprocess_scientific_text_dataset(save_path: str = 'ztmp/data/cats/scientific-text-classification/train/data.parquet'):
    """
        This function preprocess dataset from hf and save it to parquet file: save_path
    """
    
    # Create folder if not exits
    os.makedirs(
        os.path.dirname(save_path),
        exist_ok=True
    )
    
    # load dataset from hf
    dataset = load_dataset("knowledgator/Scientific-text-classification")
    
    # convert to pandas type
    
    train = dataset['train'].to_pandas()
    
    assert set(['text', "label"]).issubset(set(train.columns.tolist()))
    # save it to 
    log(train.head(4))
    pd_to_file(
        train, save_path
    )

    log(
        "save successfull"
    )


def run_train(cfg='config/train.yml', cfg_name='few_shot_setfit_scientific', dirout: str="./ztmp/exp",
              parquet_folder: str='./ztmp/data/cats/scientific-text-classification/train/',
              istest=1):
    log("\n###### User default Params   #######################################")
    if "config":    
        cc = Box()
        cc.model_name='BAAI/bge-base-en-v1.5'

        
        cc.n_train = 1000  if istest == 1 else 1000000000
        cc.n_test   = 10  if istest == 1 else int(cc.n_train*0.1)
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


    log("\n################### Config Load  #############################")
    cfg0 = config_load(cfg)
    cfg0 = cfg0.get(cfg_name, None) if cfg0 is not None else None
    #### Override of cc config by YAML config  ############################### 
    cc = exp_config_override(cc, cfg0, cfg, cfg_name)
    cc = exp_create_exp_folder(task="few_shot_sentiment", dirout=dirout, cc=cc)
    
    log("\n###################load dataset #############################")

    data = pd_read_file(parquet_folder)
    
    assert set(['text', "label"]).issubset(set(data.columns.tolist()))
    
    log(data.head(2))
    
    # Train test split 
    
    data = data.head(cc.n_train)
    
    # Get label2key from all dataset
    _, label2key = pandas_to_hf_dataset_key(data)
    cc.label2key = label2key
    cc.classes = list(label2key.keys())
    
    data['label_text'] = data['label']
    data['label'] = data['label_text'].map(label2key)
    log(cc)
    
    train = data.head(len(data) - cc.n_test)
    test  = data.tail(cc.n_test)
    train_dataset = Dataset.from_pandas(train[['text', 'label']])
    test_dataset = Dataset.from_pandas(test[['text', 'label']])
    
    
    from datasets import DatasetDict

    dataset = DatasetDict({
        "train":train_dataset,
        "test": test_dataset
    })
    log(f'train.shape: {train_dataset.shape}')
    log(f'test.shape: {test_dataset.shape}')
    
    
    log("\n###############Prepare fewshot dataset#####################")
    
    train_dataset = get_train_dataset(dataset, cc.N)

    log("\n###############Tokenizer dataset#####################")
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    dataset = transform_dataset(train_dataset, cc.classes)

    tokenized_dataset = dataset.map(partial(tokenize_and_align_label, tokenizer=tokenizer))
    tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.1)
   
    
    log("\n###################load model #############################")
    model = AutoModelForSequenceClassification.from_pretrained(cc.model_name)
    log(cc.classes)
    accuracy = evaluate.load("accuracy")
    training_args  = TrainingArguments( ** dict(cc.hf_args_train))

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset['test'],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=partial(compute_metrics, accuracy_fn=accuracy),
    )

    # trainer.train()
    json_save(cc, f'{cc.dirout}/config.json')
    trainer_output = trainer.train()
    trainer.save_model( f"{cc.dirout}/model")

    cc['metrics_trainer'] = trainer_output.metrics
    json_save(cc, f'{cc.dirout}/config.json',     show=1)
    json_save(cc, f'{cc.dirout}/model/meta.json', show=0)  ### Required when reloading for inference
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    classifier = pipeline("zero-shot-classification",
                        model=f"{cc.dirout}/model",tokenizer=tokenizer, device=device)

    preds = []
    label2idx = {label: id for id, label in enumerate(cc.classes)}

    for example in tqdm(test_dataset):
        pred = classifier(example['text'],cc.classes)['labels'][0]
        idx = label2idx[pred]
        preds.append(idx)
    log(preds)
    log(test_dataset['label'])
    print(classification_report(test_dataset['label'], preds, 
                                            target_names=cc.classes, digits=4))
    




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

# Example usage:
# dataset = Dataset.from_dict({'column1': [1, 2], 'column2': ['a', 'b']})
# save_hf_dataset(dataset, "path/to/save/dataset")




def compute_metrics(eval_pred, accuracy_fn):
   predictions, labels = eval_pred

   predictions = np.argmax(predictions, axis=1)

   return accuracy_fn.compute(predictions=predictions, references=labels)

def tokenize_and_align_label(example, tokenizer):
   hypothesis = example['targets']

   seq = example["sources"]+hypothesis

   tokenized_input = tokenizer(seq, truncation=True, max_length=512, 
                                                    padding="max_length")

   label = example['labels']
   if label==1.0:
       label = torch.tensor(1)
   elif label==0.0:
       label = torch.tensor(2)
   else:
       label = torch.tensor(0)
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




import torch
import torch.nn as nn
from transformers import BertModel
from sentence_transformers import SentenceTransformer

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





###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




"""LOGS 
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