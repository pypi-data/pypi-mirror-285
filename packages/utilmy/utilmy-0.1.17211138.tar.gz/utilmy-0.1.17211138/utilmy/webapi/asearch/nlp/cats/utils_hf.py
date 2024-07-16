""" Re-usable helper functions to simplify
training with HF library

 pip install utilmy fire python-box

Some rules:

   1) Do not harcode column names, but used  default variable...
       def myfun( coltext="text')

   2)     


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
       BertModel, EarlyStoppingCallback
    )

    # from sentence_transformers import SentenceTransformer
    import torch, evaluate
    import torch.nn as nn

    #from utils.utilmy_base import diskcache_decorator, log_pd

    ### pip install utilmy : one liner helpers.
    """ 
    
    """
    from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob, config_load,
                       json_save, json_load, log, log2, loge, diskcache_decorator )



from dataclasses import dataclass



def test_setup():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
    from datasets import load_dataset
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    import numpy as np

    # Load model and tokenizer
    model = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-small", num_labels=2)
    tokenizer = AutoTokenizer.from_pretrained("microsoft/deberta-v3-small")

    # Load and preprocess dataset
    dataset = load_dataset("imdb")
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True)

    dataset = dataset.select(range(20))

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # Define metrics function
    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
        acc = accuracy_score(labels, preds)
        return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

    # Define callback
    class PrintCallback:
        def on_log(self, args, state, control, logs=None, **kwargs):
            print(f"Step: {state.global_step}, Loss: {logs['loss']:.4f}")

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir="./ztmp/results",
        num_train_epochs=epoch,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
    )





def test1():
    """


    """

    model, train_args, tokemized_ds = train_setup(epoch=3)

    cc = Box({})
    cc.vals = train_args

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds["train"],
        eval_dataset=tokenized_ds["test"],
        compute_metrics=compute_metrics,
        callbacks=[CallbackCSaveheckpoint(cc)]
    )

    # Train the model
    trainer.train()


#####################################################################################################
def tokenize_single_label_batch(rows, num_labels, label2key, coltext='text', colabel='label'):
        """
        
           Single Label: OneHot Label or Int Label. (HF has some small bugs...)

        """
        out = tokenizer( rows["text"],truncation=True,  
                        # padding=True, 
                        # max_length= cc.max_length, 
                  )

        # ##### Label_idx into Multi-Label OneHot encoding ######## 
        ll   = []
        sample_list = rows['label']
        for row in sample_list:
            ones = [0. for i in range(num_labels)]
            
            # if isinstance(row, str):
            #     row = row.split(",")
                
            if isinstance(row, int):
                ### 1 text ---> 1 Single Tags 
                ones[ row ] = 1.
                ll.append(ones)

            # elif isinstance(row, list):
            #     ### 1 text ---> Many Label Tags
            #     for vali in row:
            #         idx = label2key[vali] if isinstance(vali, str) else vali 
            #         ones[ vali ] = 1.   ### Float for Trainer
            #     ll.append(ones )                  
        out['labels'] = ll
        return out



def tokenize_single_label_batch(rows, num_labels, label2key):
        """
        
           Single Label: OneHot Label or Int Label. (HF has some small bugs...)

        """
        out = tokenizer( rows["text"],truncation=True,  
                        # padding=True, 
                        # max_length= cc.max_length, 
                  )

        # ##### Label_idx into Multi-Label OneHot encoding ######## 
        pass 


#####################################################################################################
from transformers import TrainerCallback
class CallbackCSaveheckpoint(TrainerCallback):
    def __init__(self, cc=None):
        self.cc = cc  # Store cc as an instance variable

    def on_save(self, args, state, control, **kwargs):
        """ When doing Checkpoint /saving:
             Need to save more extra information INSIDE the checkpoint Folder.
               --> current training train.py
               --> meta.json

             --> checkpoint contains ALL the needed information to re-train...

              do you see why ?

              cc = box(cc) --> contains ALL params + mapping + all; into JSON.
              cc.XXYYUEEE.  

              cc Dictionnary of all params --> must be save inside the checkpoint too.

             The checkpoint becomes Self-Indepneant : All we need is inside the checkpoint folder...
                easy to re-start,  send to somebody else
                Very useful 

              utils_huggingface.py
                 with many utils functions/class to simplify the training management.

                 

 
              json_save(cc, )

        
        """
        import os
        import json
 

        if state.is_world_process_zero:
            # Get the checkpoint folder path
            try:
               dircheckpoint = os.path.join(args.output_dir, f"checkpoint-{state.global_step}")      
               os_copy_current_file(dircheckpoint +"/train.py")
               # Serializing json from cc
               json_object = json.dumps(self.cc.to_dict(), indent=2)
               cc_box_path = os.path.join(dircheckpoint, "meta.json")

               # Writing to meta.json
               with open(cc_box_path, "w") as outputfile:
                   outputfile.write(json_object)
               
               print(f"Saved custom info to {dircheck}")


               #### other meta info inside the checkpoint folder....



            except Exception as e:
               log(e)   
        
        return control




def hf_model_load_checkpoint(dir_checkpoint):
    from transformers import AutoModelForSequenceClassification

    model = AutoModelForSequenceClassification.from_pretrained(dir_checkpoint, num_labels=2)
    checkpoint = torch.load( dir_checkpoint )
    model.load_state_dict(checkpoint, strict=False)
    return model 






##################################################################
def hf_save_model_with_checkpoint(trainer, dirout):

    trainer.save_state()
    trainer.save_pretrained(dirout)




def hf_model_get_mapping(model='mymodel'):
    from transformers import AutoConfig

    config = AutoConfig.from_pretrained(model)

    log(config)

    label2id   = config.label2id
    id2label   = config.id2label
    max_length = config.max_position_embeddings
    log('mdoel: ', str(label2id)[:100] )    
    log('model: max_length ', max_length)
    return label2id, id2label, max_length


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




def accelerator_init(device="cpu", model=None):
    from accelerate import Accelerator
    try: 
       accelerator = Accelerator(cpu=True if device == "cpu" else False)
       return accelerator
    except Exception as e:
       log(e) 


def np_argmax(tuple_list, col_idx=1):
    idx= np.argmax([t[col_idx] for t in tuple_list])
    return tuple_list[ idx] 


def np_sort(tuples, col_id=0, desc=1):
    return sorted(tuples, key=lambda x: float(x[col_id]), reverse=True if desc == 1 else False)

def argmax_score(scores):
    return max(range(len(scores)), key=scores.__getitem__)








##################################################################
######### Metrics ################################################
f1_metric       = evaluate.load("f1")
accuracy_metric = evaluate.load("accuracy")
clf_metric      = evaluate.combine(["accuracy", "f1", "precision", "recall"])




######## Multi ###########################################
def compute_multi_accuracy(eval_pred):
    """  list of OneHot_vector !!! 2D vector
    """
    preds_score_2D, labels_2D_onehot = eval_pred        ### 2D vector
    pred_labels_idx = np.argmax(preds_score_2D, axis=1) ### need reduction
    labels_idx      = np.argmax(labels_2D_onehot,      axis=1)
    
    acc = accuracy_metric.compute(predictions=pred_labels_idx, references= labels_idx)
    return {  "accuracy": acc["accuracy"], }


def compute_multi_accuracy_f1(eval_pred):
    """  list of OneHot_vector !!! 2D vector

    """
    preds_score_2D, labels_2D_onehot = eval_pred        ### 2D vector
    pred_labels_idx = np.argmax(preds_score_2D, axis=1) ### need reduction
    labels_idx      = np.argmax(labels_2D_onehot,      axis=1)
    
    acc      = accuracy_metric.compute(predictions=pred_labels_idx, references= labels_idx)
    f1_micro = f1_metric.compute(predictions=pred_labels_idx,       references= labels_idx, average='micro')["f1"]


    # Compute F1 per class
    f1_per_class = f1_metric.compute(predictions=pred_labels, references=ref_labels, average=None)['f1']
    
    # Create a dictionary with class names (adjust based on your number of classes)
    class_names       = [f"class_{i}" for i in range(len(f1_per_class))]
    f1_per_class_dict = {f"f1_{name}": score for name, score in zip(class_names, f1_per_class)}

    return {  "accuracy":     acc["accuracy"],
              "f1_micro":     f1_micro,
              "f1_per_class": f1_per_class_dict 
            }



def compute_multi_accuracy_hamming(eval_pred):
    from sklearn.metrics import hamming_loss
    preds_score, labels = eval_pred


    pred_labels = [ [ pi>0.5 for pi in pred ] for pred in preds_score ] # np.argmax(predictions, axis=1)
    ham_list    = []
    for pred, label in zip(preds_score, labels):
        ham_values = 1 - hamming_loss(labels, preds_score)
        ham_list.append( ham_values)

    return {
        "accuracy_hamming": float( np.sum(ham_list) )
    }



def metrics_multi(eval_pred):

   def sigmoid(x):
       return 1/(1 + np.exp(-x))

   preds_score, labels = eval_pred
   preds_proba = sigmoid(preds_score)
   preds  = (preds_proba > 0.5).astype(int).reshape(-1)
   labels = labels.astype(int).reshape(-1)
   dd =  clf_metric.compute(predictions=preds, references=labels)
   return dd



######## Single ###########################################
def compute_single_(eval_pred, accuracy_fn):
   predictions, labels = eval_pred
   predictions = np.argmax(predictions, axis=1)
   return accuracy_fn.compute(predictions=predictions, references=labels)


def compute_single_accuracy_f1(eval_pred):
    pred_2D, labels = eval_pred
    pred_1D = pred_2D.argmax(axis=-1)
    
    accuracy = accuracy_metric.compute(predictions=pred_1D, references=labels)["accuracy"]
    f1       = f1_metric.compute(predictions=pred_1D, references=labels, average="macro")["f1"]
    return {   "accuracy": accuracy,  "f1": f1, }
    
    
def compute_single_metrics_f1_acc_perclass(eval_pred):
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
    










############################################################################################
######## Muti-label Classifier Helper ######################################################
def test():
    data = {'col1': ['a', 'd', 'g'], 'col2': ['b', 'e', 'h'], 'col3': ['c', 'f', 'i']}
    df = pd.DataFrame(data)

    dlabel = LABELdata()
    df = dlabel.pd_labels_merge_into_singlecol(df, cols=['col1', 'col2', 'col3'], colabels="colnew")
    log(df["colnew"].values[0])



class LABELdata:
    from utilmy import (date_now, date_now, pd_to_file, log, pd_read_file, os_makedirs,
                        glob_glob, json_save, json_load, config_load,
                        dict_merge_into)

    def __init__(self, dirdata=None, dirmeta=None):
        """ Label Data Storage and converter methods
            for multi-class, multi-label

            dlabel = LABELdata()
            dlabel.create_metadict(dirin="./ztmp/data/cats/arxiv/train/df_8000.parquet")
            print(dlabel.I2L, dlabel.L2I, dlabel.NLABEL_TOTAL)

        """
        self.dirdata = dirdata  ###  training data raw files
        self.dirmeta = dirmeta  ###  meta.json file

        self.I2L, self.L2I, self.meta_dict = {}, {}, {}
        self.I2CLASS, self.CLASS2I = {}, {}
        self.NLABEL_TOTAL = 0


    def save_metadict(self, dirmeta=None):
        """ Save json mapper to meta.json
        """
        dirout2 = dirmeta if dirmeta is not None else self.dirmeta
        dirout2 = dirout2 if ".json" in dirout2 else dirout2 + "/meta.json"
        json_save(self.meta_dict, dirout2)
        log(dirout2)


    def load_metadict(self, dirmeta: str = None):
        """Load mapper from a directory containing meta.json 
        Args: dirmeta (str, optional): directory containing meta.json
        Returns: dict containing all mapping.
        """

        dirmeta = dirmeta if dirmeta is not None else self.dirmeta
        flist = glob_glob(dirmeta)
        flist = [fi for fi in flist if ".json" in fi.split("/")[-1]]
        fi = flist[0]

        if "json" in fi.split("/")[-1].split(".")[-1]:
            with open(fi, 'r') as f:
                meta_dict = json.load(f)

            if "meta_dict" in meta_dict.get("data", {}):
                ### Extract meta_dict from config training
                meta_dict = meta_dict["data"]["meta_dict"]

            self.NLABEL_TOTAL = meta_dict["NLABEL_TOTAL"]
            self.I2L = {int(ii): label for ii, label in meta_dict["I2L"].items()}  ## Force encoding
            self.L2I = {label: int(ii) for label, ii in meta_dict["L2I"].items()}

            self.dirmeta = fi
            return self.I2L, self.L2I, self.NLABEL_TOTAL, meta_dict
        else:
            log(" need meta.json")

    def create_metadict(self, dirdata="./ztmp/data/cats/arxiv/*.parquet", cols_class=None, dirout=None,
                        merge_all_labels_into_single_class=1):
        """Create a mapper json file for labels from raw training data
            python nlp/cats/multilabel.py labels_load_create_metadict --dirin "./ztmp/data/cats/arxiv/train/*.parquet" --dirout "./ztmp/data/cats/arxiv/meta/meta.json"

        Doc::
            Args: dirin (str, optional):  df[["labels"]] as string joined by ","

            Returns: meta.json
                tuple: A tuple containing following mapper dictionaries:
                    - I2L (dict): dict mapping labels to their corresponding indices.
                    - L2I (dict): dict mapping indices to their corresponding labels.
                    - NLABEL_TOTAL (int): total number of labels.
                    - meta_dict (dict): dict containing additional metadata about labels.

        """
        flist = glob_glob(dirdata)
        log("files loaded for labels: ", flist)
        df = pd_read_file(flist)
        assert df[["labels"]].shape

        ##### Expand column lbael  into multiple columns
        df2, cols_class = self.pd_labels_split_into_cols(df, colabel="labels", cols_class=cols_class)
        # df2 = df2.drop_duplicates()


        #####  mapping Label --> Index : Be careful of duplicates
        I2L, L2I = {}, {}
        I2CLASS, CLASS2I = {}, {}
        dd = {"labels_n_unique": {}, "labels": {}}
        idx = -1
        for class_i in cols_class:
            vv = df2[class_i].drop_duplicates().values
            dd["labels_n_unique"][class_i] = len(vv)
            dd["labels"][class_i] = {"labels": list(vv),
                                     "freq": df2[class_i].value_counts().to_dict()}

            class_i2 = f"{class_i}"
            if int(merge_all_labels_into_single_class) == 1:
                log(f"{class_i} : merge all_labels into_single_class")
                class_i2 = "" ### Class Name default

            ### For each label of column, add indexesm add to class indexes. 
            if class_i2 not in CLASS2I:
               CLASS2I[class_i2] = []
               
            for label in vv:
                label = label.strip()
                label2 = f"{class_i2}-{label}" if class_i2 != "" else label  ### gender-male, gender-female
                # log("label:", label2)
                if label2 not in L2I:
                    idx += 1
                    L2I[label2] = idx  ### red --> 1, blue --> 2
                    I2L[idx]    = label2  ### 1 --> red, 2 --> blue

                    I2CLASS[idx] = class_i2  ####  red --> color, blue --> color
                    CLASS2I[class_i2].append(idx)  #### Color --> [red, blue]
                    # log(CLASS2I[class_i2])

        #### All classes
        dd["class_cols"]   = list(cols_class)  ### List of class columns
        dd["NCLASS_TOTAL"] = len(cols_class)

        #### Labels of each class
        ### colA --> OnehoA,  colB --> onehotB     bigHot = concat(onehotA, onehotB,...)      

        NLABEL_TOTAL = len(L2I) 
        
        #### +1 For NA/unknow values : not needed, only at Encoding
        # NLABEL_TOTAL = NLABEL_TOTAL + 1  ### + 1 for NA/Unknown Values   
             
        dd["NLABEL_TOTAL"] = NLABEL_TOTAL
        dd["I2L"] = I2L
        dd["L2I"] = L2I
        dd["I2CLASS"] = I2CLASS  ####  red --> color, blue --> color
        dd["CLASS2I"] = CLASS2I  ####  Color --> [red, blue]

        self.meta_dict = dd
        self.I2L = I2L
        self.L2I = L2I
        self.NLABEL_TOTAL = NLABEL_TOTAL


        if dirout is not None:
            self.save_metadict(dirout)

        return I2L, L2I, NLABEL_TOTAL, self.meta_dict

    
    def pd_labels_split_into_cols(self, df, colabel="labels", cols_class=None):
        df = df[[colabel]]
        if isinstance(df[colabel].values[0], str):
            df[colabel] = df[colabel].apply(lambda xstr: [t.strip() for t in xstr.split(",")])
        else:
            df[colabel] = df[colabel].apply(lambda xlist: [t.strip() for t in xlist])

        ncols = len(df[colabel].values[0])
        cols_class = [f"class_{i}" for i in range(ncols)] if cols_class is None else cols_class
        df2 = pd.DataFrame(df[colabel].tolist(), columns=cols_class)
        df2.index = df.index

        return df2, cols_class


    def pd_labels_merge_into_singlecol(self, df, cols=None, sep=",", colabels="labels"):
        if cols is None:
            cols = df.columns.tolist()
        df[colabels] = df[cols].astype(str).agg(sep.join, axis=1)
        return df


    def to_onehot(self, xstr: str):
        """ Converts a string of ","labels into a one-hot encoded list.
        """
        zero, one = 0.0, 1.0  ## HFace needs float !!
        labels_onehot = [float(zero)] * self.NLABEL_TOTAL
        
        if isinstance(xstr, str):
              xstr = xstr.split(",")
              
        for label in xstr:
            ### If mising, One Label INDEX for unknown
            label_id = self.L2I.get(label, self.NLABEL_TOTAL - 1)
            # log("label_id:",label,  label_id)
            labels_onehot[label_id] = one  #

        return labels_onehot


    def pd_validate_dataframe(df, cols=None, sep=",", colabels="labels", nrows=1000):

        assert df[["text", "labels"]].shape

        labels = df["labels"].values
        if isinstance(labels[0], str):
            labels= [ x.split(",") for x in  labels ]
            
        nclass = len(labels[0])
        for i in range(len(df)):
            if len(labels[i]) != nclass:
                    raise Exception(" Mismatch")

        log("dataframe text, labels  validated")
        return True




def data_tokenize_split(df, tokenizer, labelEngine, cc, filter_rows=True):
    """ 

        {'input_ids': [[1, 8382, 277, 39093, 25603, 31487, 840, 39093, 28368, 59543, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
                      [1, 14046, 271, 5203, 473, 13173, 75204, 270, 6547, 40457, 267, 13946, 5648, 2, 2, 2, 2, 2, 2]],

        'token_type_ids': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 

        'attention_mask': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]], 

        'labels': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 

    """
    cols = list(df.columns)
    max_length   = cc.data.sequence_max_length
    NLABEL_TOTAL = cc.data.nlabel_total
    log("nlabel_total: ", NLABEL_TOTAL)


    df["labels"] = df["labels"].apply(lambda x: labelEngine.to_onehot(x))
    # df["labels"] = df["labels"].apply(lambda x: to_onehot(x) )
    log(df[["text", "labels"]].head(1).T)


    def preprocess_func(row):
        #### Text tokenizer
        out = tokenizer(row["text"], truncation=True, padding=True, max_length=max_length,
                        return_offsets_mapping=False,
                        return_overflowing_tokens=False)

        out["labels"] = row["labels"]
        # log(out)    
        # output["input_ids"] = output.pop("input_ids")  # Add input_ids to  output
        return out

    #### Encode texts
    ds = Dataset.from_pandas(df[["text", "labels"]])
    ds = ds.map(preprocess_func, batched=True)


    #### Filter labels with only a single instance
    if filter_rows:
        label_counts = Counter([tuple(label) for label in ds["labels"]])
        valid_labels = [label for label, count in label_counts.items() if count > 1]
        ds = ds.filter(lambda row: tuple(row["labels"]) in valid_labels)

    #### Reduce columns in dataset
    ds = ds.remove_columns(['text'])

    #  ['text', 'labels', 'input_ids', 'token_type_ids', 'attention_mask']
    # ds           = ds.remove_columns( cols)
    # ds = ds.remove_columns(['overflow_to_sample_mapping', 'offset_mapping', ] + cols)
    log(ds)
    return ds







########################################################################################
##################### Tokenizer helper ################################################
def DataCollatorClassification(tokenizer=None):
    from transformers import DataCollatorWithPadding
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, padding="longest")
    return data_collator




#######################################################################################
##### Define A model with custom classifier head : 3 softmax
class MultiSoftmaxClassifier(AutoModelForSequenceClassification):
    def __init__(self, config):
        """
        3 softmax head : one per class group: 
           class A  : A1-A5, 
           classs B : B1-B4, 
           class  C : C1-C2

        ### Usage code:
            # Load model and tokenizer
            modelid   = 'microsoft/deberta-v3-base'
            tokenizer = AutoTokenizer.from_pretrained( modelid)
            model     = MultiSoftmaxClassifier.from_pretrained(modelid, num_labels=11)
            model.eval()  # Set model to evaluation mode

            # Tokenize input text
            inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            
            # Move inputs to same device as model
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Perform inference
            with torch.no_grad():
                outputs = model(**inputs)
            print( probabilities.cpu().numpy() )

        """
        super().__init__(config)
        self.classifier = torch.nn.Linear(config.hidden_size, config.num_labels)  # Total labels across all classes

    def forward(self, **inputs):
        outputs = super().forward(**inputs)
        # logits = outputs.logits
        logits = self.classifier(outputs.pooler_output)  # Use classifier on pooled output

        # Apply softmax per class group: A1-A5, B1-B4, C1-C2
        # 1 Class can only contain 1 label only,
        logits = torch.cat([
            torch.nn.functional.softmax(logits[:, :5], dim=1),
            torch.nn.functional.softmax(logits[:, 5:9], dim=1),
            torch.nn.functional.softmax(logits[:, 9:], dim=1)
        ], dim=1)
        return torch.nn.functional.softmax(logits, dim=1)


def test5():
    import torch
    from transformers import AutoTokenizer

    # Load model and tokenizer
    modelid = 'microsoft/deberta-v3-base'
    tokenizer = AutoTokenizer.from_pretrained(modelid)
    model = MultiSoftmaxClassifier.from_pretrained(modelid, num_labels=11)
    model.eval()  # Set model to evaluation mode

    # Function to perform inference
    def predict(texts):
        # Tokenize input text
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

        # Move inputs to same device as model
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)

        # Apply softmax to logits to get probabilities
        logits = outputs['logits']
        probabilities = torch.nn.functional.softmax(logits, dim=1)

        # Convert probabilities to numpy array
        probabilities = probabilities.cpu().numpy()

        return probabilities

    # Example usage
    texts = ["Sample text for classification."]
    predictions = predict(texts)
    print("Predicted probabilities:", predictions)
















###############################################################################
###############################################################################
class NERdata(object):
    def __init__(self,dirmeta=None, nertag_list=None, token_BOI=None):
        """ Utils to normalize NER data for pandas dataframe


            Args:
                nertag_list (list): list of tags. If not provided, default list of tags is used.
                token_BOI (list): list of token BOI values. If not provided, default list of token BOI values is used.
            Info:

                    - text (str): text.
                    - ner_list (list): List of named entity records. Each named entity record is dict with following keys:
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
        L2I, I2L, NCLASS = self.create_map_dict()

        self.L2I    = L2I      ## Label to Index
        self.I2L    = I2L      ## Index to Label
        self.NCLASS = NCLASS   ## NCLASS 


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
        log(self.meta_dict)


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
            self.nertag_list = meta_dict['nertag_list']
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

    @staticmethod
    def from_meta_dict(meta_dict):
        ner_data_engine = NERdata()
        meta_dict = Box(meta_dict)
        if "meta_dict" in meta_dict.get("data", {}):
            ### Extract meta_dict from config training
            meta_dict = meta_dict["data"]["meta_dict"] 

        ner_data_engine.NLABEL_TOTAL = meta_dict["NLABEL_TOTAL"]
        ner_data_engine.I2L = { int(ii): label   for ii, label in meta_dict["I2L"].items() } ## Force encoding
        ner_data_engine.L2I = { label  : int(ii) for label,ii  in meta_dict["L2I"].items() }
        ner_data_engine.nertag_list = meta_dict['nertag_list']
        ner_data_engine.meta_dict = meta_dict
        return ner_data_engine
    
    def create_metadict(self,):     

        mm ={


        } 

        return mm


    def create_map_dict(self,):        
        NCLASS= self.NCLASS
        # log("token boi")
        # log(f'{self.token_BOI}')
        # log(f'{self.nertag_list}')
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
            dict: dict containing text and ner_list fields. ner_list field is list of dictionaries,
                  where each dict represents named entity and contains type, value, start, end, and text fields.
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
            elif i > 0 and (c-self.NCLASS == pred_list[i-1] or c==pred_list[i-1]):
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
                'value' : text[span[0]:span[1]],
                'start': span[0],
                'end'  : span[1],
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
            list: List of span records for NER. Each span record is dict with following keys:
                - text (str): text.
                - ner_list (list): List of named entity records. Each named entity record is dict with following keys:
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




########################################################################################
##################### Tokenizer helper #################################################
def token_fix_beginnings(labels, n_nerclass):
    """Fix   beginning of list of labels by adjusting   labels based on certain conditions.
    Args:
        labels (list): list of labels.        
    # tokenize and add labels    
    """
    for i in range(1,len(labels)):
        curr_lab = labels[i]
        prev_lab = labels[i-1]
        if curr_lab in range(n_nerclass,n_nerclass*2):
            if prev_lab != curr_lab and prev_lab != curr_lab - n_nerclass:
                labels[i] = curr_lab -n_nerclass
    return labels


def tokenize_and_align_labels(row:dict, tokenizer,  L2I:dict, token_BOI: list):
    """Tokenizes  given examples and aligns  labels.
    Args:
        examples (dict): dict containing  examples to be tokenized and labeled.
            - "text" (str):  query string to be tokenized.
            - "ner_list" (list): list of dictionaries representing  entity tags.
                Each dict should have  following keys:
                - 'start' (int):  start position of  entity tag.
                - 'end' (int):  end position of  entity tag.
                - "class" (str):  type of  entity tag.

    Returns:
        dict: dict containing  tokenized and labeled examples.
            It has  following keys:
            - 'input_ids' (list): list of input ids.
            - 'attention_mask' (list): list of attention masks.
            - 'labels' (list): list of labels.
            - 'token_type_ids' (list, optional): list of token type ids. Only present if 'token_type_ids' is present in  input dict.
    """
    row['text'] = row['text'].replace("\n","*")
    words = row['text'].split()
    # offset_mapping = [[]]
    # for word in words:
        
    
    o = tokenizer(row["text"],
                  return_offsets_mapping=True,
                  return_overflowing_tokens=True)
    offset_mapping = o["offset_mapping"]
    o["labels"] = []
    NCLASS = (len(L2I) - 1) // 2
    for i in range(len(offset_mapping)):
        labels = [L2I[token_BOI[2]] for i in range(len(o['input_ids'][i]))]
        for tag in row["ner_list"]:
            label_start = tag['start']
            label_end = tag['end']
            label = tag["class"]
            for j in range(len(labels)):
                token_start = offset_mapping[i][j][0]
                def fix_space(x, t):
                    while x<len(t) and t[x] ==' ':
                        x+=1
                    return x
                    # print(token_start)
                token_end = offset_mapping[i][j][1]
                
                if token_start == label_start or fix_space(token_start, row['text']) == label_start:
                    labels[j] = L2I[f'{token_BOI[0]}-{label}']
                if token_start > label_start and token_end <= label_end:
                    labels[j] = L2I[f'{token_BOI[1]}-{label}']
                # if token_start==89 or token_start==98:
                #     print(token_start, token_end, labels[j], label_start, label_end)
                    
        for k, input_id in enumerate(o['input_ids'][i]):
            if input_id in [0,1,2]:
                labels[k] = -100
        # log(labels)
        labels = token_fix_beginnings(labels, NCLASS)
        # log(labels)
        o["labels"].append(labels)

    o['labels']         = o['labels'][0]
    o['input_ids']      = o['input_ids'][0]
    o['attention_mask'] = o['attention_mask'][0]
    if 'token_type_ids' in o:o['token_type_ids'] = o['token_type_ids'][0]
    return o



def data_tokenize_split(df, tokenizer, labelEngine, cc, filter_rows=False):
    """ 

        {'input_ids': [[1, 8382, 277, 39093, 25603, 31487, 840, 39093, 28368, 59543, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
                      [1, 14046, 271, 5203, 473, 13173, 75204, 270, 6547, 40457, 267, 13946, 5648, 2, 2, 2, 2, 2, 2]],

        'token_type_ids': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 

        'attention_mask': [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]], 

        'offset_mapping': [[(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], 
                           [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]], 

        'labels': [[-100, 8382, 277, 390

    """
    pprint(cc)
    cols         = list(df.columns)
    #max_length   = cc.data.sequence_max_length
    # NLABEL_TOTAL = cc.data.nlabel_total
    # log("nlabel_total: ", NLABEL_TOTAL)

    columns = list(df.columns)

    ds = Dataset.from_pandas(df)
    ds = ds.map(tokenize_and_align_labels, 
                 fn_kwargs={'tokenizer':  tokenizer,
                             "L2I":       labelEngine.L2I, 
                             "token_BOI": labelEngine.token_BOI})

    offset_mapping = ds['offset_mapping']

    ds = ds.remove_columns(['overflow_to_sample_mapping', 'offset_mapping', ] + columns)
    log(ds)
    return ds, offset_mapping



@dataclass
class DataCollatorForNER:
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
#             log(len(labels[index]), labels[index])
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






      
###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




