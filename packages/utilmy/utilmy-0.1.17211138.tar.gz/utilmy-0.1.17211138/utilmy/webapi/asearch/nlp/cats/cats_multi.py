""" 
Docs::

    ### Install
        pip install --upgrade fire utilmy
        # pip install -r pip/pip_full.txt

        cd webapi/asearch
        mkdir -p ztmp


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
       export PYTHONPATH="$(pwd)"
       alias pycat="python nlp/cats/multilabel.py  "


       ### Data prep : You need to create your own custom function to normalize data
            pycat data_arxiv_create_norm  --dirin "./ztmp/data/cats/arxiv/raw" 

            pycat data_toxic_create_norm  --dirin "ztmp/data/cats/toxicity/raw/*.csv" 


       ### Train
            pycat run_train  --dirout ztmp/exp   --cfg config/train.yml --cfg_name  multilabel_train_v1


       ### Metrics recalc  : pick up the exp folder
          export dexp=ztmp/exp/20240615/220208-class_deberta-10000/
          pycat metrics_calc_full --dirin "$dexp/dfval_pred_labels.parquet"  --dirout $dexp/dfmetrics_v1.csv  


        ### Inference
           pycat run_infer_file --nrows 10 --dirmodel "$dexp/model"  --dirdata "$dexp/dfval_pred_labels.parquet"  --dirout "$dexp/predict"

           pycat run_infer_file  --dirout ztmp/exp   --cfg config/traina/train1.yaml --cfg_name class_deberta_v1 


        ### Eval
           pycat run_eval  --nrows 10 --dirmodel "$dexp/model"  --dirdata "$dexp/dfval_pred_labels.parquet"  --dirout "$dexp/predict"




    #### Dataset Test
        https://www.kaggle.com/datasets/spsayakpaul/arxiv-paper-abstracts

        For label = "cs.ML"
        Cat1 : cs
        Cat2:  ML


      Fashion text  (cloth)
         color,     gender,    style
         blue/red       
         
      https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data

      raw record:
        comment_text	CSR BEFORE YOU PSS AROUND ON MY WORK
        id	0002bcb3da6cb337
        identity_hate	0
        insult	1
        obscene	1
        severe_toxic	1
        threat	0
        toxic	1

      normalized record:
        text: CSR BEFORE YOU PSS AROUND ON MY WORK
        labels: 0,1,1,1,0,1


    ### Fine Tuning Strategies using LLM and SetFit

        https://medium.com/@xmikex83/using-large-language-models-to-train-smaller-ones-ee64ff3e4bd3

        https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v2.0


    ### US patents dataset

        https://huggingface.co/datasets/HUPD/hupd

        https://huggingface.co/datasets/AI-Growth-Lab/patents_claims_1.5m_traim_test


    #### Full Training 
      pycat run_train  --dirout ztmp/exp   --cfg config/train.yml --cfg_name  multilabel_train_v2


"""
if "Import":
    import time, json, re, os, pandas as pd, numpy as np, copy
    from dataclasses import dataclass
    from typing import Optional, Union
    from box import Box

    from collections import Counter
    from sklearn.metrics import f1_score

    import datasets
    from datasets import load_dataset, Dataset, load_metric
    import evaluate

    # If issue dataset: please restart session and run cell again
    from transformers import (
        BitsAndBytesConfig,
        GenerationConfig,
        HfArgumentParser,
        TrainingArguments,
        Trainer,

        ###
        DataCollatorWithPadding,
        AutoTokenizer,

        ### Tokenizer / Sequence
        AutoModelForMultipleChoice,
        AutoModelForSemanticSegmentation,
        AutoModelForSequenceClassification,

        ### LLM
        AutoModelForCausalLM,
        PhiForCausalLM, DebertaForSequenceClassification,

    )
    # from transformers.models.qwen2.modeling_qwen2 import
    from transformers.tokenization_utils_base import PreTrainedTokenizerBase, PaddingStrategy
    from seqeval.metrics import f1_score, precision_score, recall_score, classification_report

    import spacy, torch
    # from pylab import cm, matplotlib

    from utilmy import (date_now, date_now, pd_to_file, log, pd_read_file, os_makedirs,
                        glob_glob, json_save, json_load, config_load,
                        dict_merge_into
                        )

    from utils.util_exp import (exp_create_exp_folder, exp_config_override, exp_get_filelist)



################################################################################################
######## Dataloder Toxic dataset #####################################################
def labels_check(df, cols_class):
    log("labels encoded check :")
    for ii in range(0, 3):
       log("\n\n", df[cols_class].iloc[ii,:].T)
       log("\nlabels: ", df["labels"].values[ii])
        
    #### Check if same length
    count_class   = [row.count(",") for row in df["labels"].values]
    assert min(count_class) == max(count_class)

    
    
def data_toxic_create_norm(dirin="./ztmp/data/cats/toxicity/raw/*.csv"):
    """ 
    #### Manual download
        files(train.csv, test.csv) manually downloaded and extracted from https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data

        ensure train and test csv are present
        url = "https://www.kaggle.com/datasets/spsayakpaul/arxiv-paper-abstracts"
        competetion = "jigsaw-toxic-comment-classification-challenge"
        os.system("kaggle competitions download -c jigsaw-toxic-comment-classification-challenge")
        
           INTO "ztmp/data/cats/toxicity/raw/
        
    #### Run the Conversion
       pycat data_toxic_create_norm --dirin "ztmp/data/cats/toxicity/raw/*.csv" 
    
    
    Converts:
    	comment_text	             
        id	          
        identity_hate    0.0
        insult           1.0
        obscene          1.0
        severe_toxic     1.0
        threat           0.0
        toxic            1.0

        to    
                text:    "My name is John Doe and I love my car. I bought a new car in 2020."
                labels:  identity_hate_NO,insult,obscene,severe_toxic,threat_NO,toxic


    """
    dirdata = dirin.split("raw")[0]

    log("\n\n#### Load Raw data    ##########################################")
    flist = glob_glob(dirin,)
    log(f"flist: {flist}")
    if len(flist)<0: raise Exception("No file found")
    
    df = pd_read_file(flist, )
    cols = list(df.columns)
    log(df.head(5).T, cols, df.shape)
    assert df[['comment_text', 'id', 'identity_hate', 'insult', 'obscene', 'severe_toxic', 'threat', 'toxic']].shape


    ########################################################################## 
    log("\n\n#### Label merging/clearning   ##################################")
    cols_class =['identity_hate', 'insult', 'obscene', 'severe_toxic', 'threat', 'toxic']
    df = df[df[cols_class].sum(axis=1) > 0]


    def get_label(row):
        ### All labels are projected into Single SAME OneHot Space
        ###  --> label name MUST BE Global Unique !!!!!!!!!!
        ##  onehot.shape == (100000,  Ncolumn * Nlabel_per_class  + 1_for_NA_global )
        llist = []
        for col in cols_class:             
             if row[col] == 1.0 : 
                 llist.append(col)            ###  1.0
             elif row[col] == 0.0 : 
                 llist.append( col + "_NO")   ###  0.0                 
             else:                
                 llist.append( "NA")          ### NA Global
                 
        return ",".join(llist)        
             
    df["labels"] = df[cols_class].apply(lambda x: get_label(x), axis=1)    
    
    labels_check(df, cols_class)


    ################################################################### 
    log("\n\n#### Text Cleaning       #################################")
    df.rename(columns={"comment_text": "text"}, inplace=True)
    df = df[["text", "labels"]]
    
    log(df.iloc[2,:].head(1).T)
    log(df.iloc[10,:].head(1).T)
    

    ###################################################################     
    ### Size of train and val #########################################
    n_train = int(len(df) * 0.8)
    df_val  = df.iloc[n_train:, :]
    df      = df.iloc[:n_train, :]
    n_val   = len(df_val)

    pd_to_file(df,     f"{dirdata}/train/df_{n_train}.parquet", show=1)
    pd_to_file(df_val, f"{dirdata}/val/df_{n_val}.parquet", show=1)


    log("############# Create Label Mapper ######################")
    dlabel = LABELdata()
    dlabel.create_metadict(dirdata   = dirdata + "/**/*.parquet",  ### Using both train and val
                           dirout    = dirdata + "/meta/meta.json",
                           cols_class= cols_class
                         )
    log(dlabel.meta_dict)


def data_toxic_load_datasplit(dirin="./ztmp/data/cats/toxicity"):
    """ 
        In [140]: df.head(1).T                                                                0
        comment_text	CS BEFORE YOU PSS AROUND ON MY WORK
        id	0002bcb3da6cb337
        identity_hate	0
        insult	1
        obscene	1
        severe_toxic	1
        threat	0
        toxic	1
        labels	0,1,1,1,0,1
    """
    df = pd_read_file(dirin + "/train", )
    log_pd(df)
    assert df[["text", "labels"]].shape

    df_val = pd_read_file(dirin + "/val", )
    log_pd(df_val)
    assert df_val[["text", "labels"]].shape

    assert len(df_val) > 1 and df.shape[1] >= 2
    assert len(df) > 1 and df.shape[1] >= 2
    return df, df_val


def data_toxicity_load_metadict(dirmeta="./ztmp/data/cats/toxicity/meta/meta.json"):
    labeldata = LABELdata()
    I2L, L2I, NLABEL_TOTAL, meta_dict = labeldata.load_metadict(dirmeta=dirmeta)

    return labeldata, meta_dict




#################################################################################################
######## Dataloder Custom  Arxiv dataset #####################################################
def data_arxiv_create_norm(dirin="./ztmp/data/cats/arxiv/raw"):
    """ 
         python nlp/cats/multilabel.py data_arxiv_create_norm  --dirin "./ztmp/data/cats/arxiv/raw" 

         labels format: 



    """
    dirdata = dirin.split("raw")[0]

    flist = glob_glob(dirin)
    if len(flist) < 1:
        from utilmy.util_download import download_kaggle
        url = "https://www.kaggle.com/datasets/spsayakpaul/arxiv-paper-abstracts"
        download_kaggle(url, dirout=dirdata + "/download")

    df = pd_read_file(dirin, )
    log(df.head(5).T, df.columns, df.shape)
    cols = list(df.columns)
    assert df[["titles", "terms"]].shape


    ### train/test split
    cols = list(df.columns)
    if "cat1" not in cols:
        ##### Creating FAKE Labels
        df["terms"] = df["terms"].apply(lambda x: x.replace("[", "").replace("]", ""))  # ['cs.CV', 'cs.AI', 'cs.LG']

        df["terms"] = df["terms"].apply(lambda x: x.replace(" ", ""))  # ['cs.CV', 'cs.AI', 'cs.LG']

        df["label2"] = df["terms"].apply(lambda x: sorted(x.split(",")))  # ['cs.CV', 'cs.AI', 'cs.LG']
        df["cat1"] = df["label2"].apply(lambda x: x[0].split(".")[0])  # "cs"
        df["cat2"] = df["label2"].apply(lambda x: x[0].split(".")[-1])  # "CV"
        df["cat3"] = df["label2"].apply(lambda x: x[1].split(".")[0] if len(x) > 1 else "NA")  # "cs"
        df["cat4"] = df["label2"].apply(lambda x: x[1].split(".")[-1] if len(x) > 1 else "NA")  # "AI"


        ### FINAL labels is CONCATENAD List of string
        df["labels"] = df.apply(lambda x: x["cat1"] + "," + x["cat2"] + "," + x["cat3"] + "," + x["cat4"], axis=1)
        df["labels"] = df["labels"].apply(lambda x: x.replace("'", ""))

    df = df.rename(columns={"titles": "text"})

    ### Column we need
    assert df[["text", "labels"]].shape
    n_train = int(len(df) * 0.8)
    df_val  = df.iloc[n_train:, :]
    df      = df.iloc[:n_train, :]
    n_val   = len(df_val)



    pd_to_file(df,     f"{dirdata}/train/df_{n_train}.parquet", show=1)
    pd_to_file(df_val, f"{dirdata}/val/df_{n_val}.parquet", show=1)


    log("############# Create Label Mapper")
    dlabel = LABELdata()
    dlabel.create_metadict(dirdata=dirdata + "/train/*.parquet",
                           dirout=dirdata + "/meta/meta.json")
    log(dlabel.meta_dict)
    
    ### Check if label column is well defined
    ### "" or NA        male,NA,NA,red     
    dlabel().pd_validate_dataframe(df)



def data_arxiv_load_datasplit(dirin="./ztmp/data/cats/arxiv"):
    """ 
        In [140]: df.head(1).T                                                                0
        abstracts                                               None
        summaries  Stereo matching is one of widely used tech...
        terms                                        'cs.CV','cs.LG'
        titles     Survey on Semantic Stereo Matching / Semantic ...
        label2                                    ['cs.CV', 'cs.LG']
        cat1                                                     'cs
        cat2                                                     CV'
        cat3                                                     'cs
        cat4                                                     LG'
        labels                                           cs,CV,cs,LG


    """
    df = pd_read_file(dirin + "/train", )
    log_pd(df)
    assert df[["text", "labels"]].shape


    df_val = pd_read_file(dirin + "/val", )
    log_pd(df_val)
    assert df_val[["text", "labels"]].shape

    assert len(df_val) > 1 and df.shape[1] >= 2
    assert len(df) > 1 and df.shape[1] >= 2
    return df, df_val



def data_arxiv_load_metadict(dirmeta="./ztmp/data/cats/arxiv/meta/meta.json"):
    labeldata = LABELdata()
    # I2L, L2I, NLABEL_TOTAL, meta_dict =  dlabel.load_metadict(dirmeta=dirmeta)
    # return I2L, L2I, NLABEL_TOTAL, meta_dict

    I2L, L2I, NLABEL_TOTAL, meta_dict = labeldata.load_metadict(dirmeta=dirmeta)

    return labeldata, meta_dict





########################################################################################
##################### Data Validator ###################################################
def log_pd(df, n=2):
    log(df.head(n), "/n", list(df.columns), "/n", df.shape)


def label_check(df):
    LABELdata().pd_validate_dataframe(df)

#################################################################################################
######## Dataloder Common #######################################################################
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




def data_DEFAULT_load_datasplit(dirin="./ztmp/data/cats/arxiv"):
    """ 
        In [140]: df.head(1).T                                                                0
        text : str
        labels                                           cs,CV,cs,LG


    """
    df = pd_read_file(dirin + "/train", )
    log_pd(df)
    assert df[["text", "labels"]].shape


    df_val = pd_read_file(dirin + "/val", )
    log_pd(df_val)
    assert df_val[["text", "labels"]].shape

    assert len(df_val) > 1 and df.shape[1] >= 2
    assert len(df) > 1 and df.shape[1] >= 2
    return df, df_val



def data_DEFAULT_load_metadict(dirmeta="./ztmp/data/cats/arxiv/meta/meta.json"):
    """ load the JSON meta dict pre-built
    
    """
    labeldata = LABELdata()
    I2L, L2I, NLABEL_TOTAL, meta_dict = labeldata.load_metadict(dirmeta=dirmeta)

    return labeldata, meta_dict



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



#################################################################################
######################## Train ##################################################
def run_train(cfg=None, cfg_name="class_deberta", dirout="./ztmp/exp", dirdata="ztmp/data/cats/toxicity", istest=1):
    """ 
       python nlp/cats/multilabel.py run_train  --dirout ztmp/exp   --cfg config/traina/train1.yaml --cfg_name class_deberta 

      Multi class Multi Labels   ( type of text, author category, ...)
       Class columnns
              
            classA,       classB,        classC,      classD

             LA_1,        LB_2
             LA_2,        LB_3  
             LA_3,        LB_3          ...      ...
             
       Simpligy notation:  merge by ","

              labels ","

                 LA_1,LB_3,LC_9
                 LA_9,LB_3,LC_4
                 ....

                 LA_4,LB_1,LC_12

        Labels --> list of string.


    """
    log("\n######  Params: Setup Default   #######################################")
    if "config":
        cc = Box()
        cc.model_name = 'microsoft/deberta-v3-base'
        cc.problem_type = "multi_label_classification"

        #### Data name
        cc.dataloader_name = "data_DEFAULT_load_datasplit"
        cc.datamapper_name = "data_DEFAULT_load_metadict"

        cc.n_train = 6 if istest == 1 else 1000000000
        cc.n_val = 2 if istest == 1 else 1000000000

        ############# Train Args
        aa = Box({})
        aa.output_dir                  = f"{dirout}/log_train"
        aa.per_device_train_batch_size = 32
        aa.gradient_accumulation_steps = 1
        aa.optim                       = "adamw_hf"
        aa.save_steps                  = min(100, cc.n_train - 1)
        aa.logging_steps               = min(50, cc.n_train - 1)
        aa.learning_rate               = 1e-5
        aa.max_grad_norm               = 2
        aa.max_steps                   = -1
        aa.num_train_epochs            = 1
        aa.warmup_ratio                = 0.2  # 20%  total step warm-up
        # lr_schedulere_type='constant'
        aa.evaluation_strategy = "epoch"
        aa.logging_strategy    = "epoch"
        aa.save_strategy       = "epoch"
        cc.hf_args_train = copy.deepcopy(aa)

        ############# Model Args
        cc.hf_args_model = {}
        cc.hf_args_model.model_name   = cc.model_name
        cc.hf_args_model.problem_type = cc.problem_type


    log("\n###### Params: Config Load   ########################################")
    cfg0 = config_load(cfg)
    cfg0 = cfg0.get(cfg_name, None) if cfg0 is not None else None
    
    #### Override cc DEFAULT by YAML config  #####################################
    cc = exp_config_override(cc, cfg0, cfg, cfg_name)


    log("\n###### Experiment Folder   #########################################")
    cc = exp_create_exp_folder(task="class_deberta", dirout=dirout, cc=cc)
    log(cc.dirout);
    del dirout

    log("\n###### Model : Training params ######################################")
    args = TrainingArguments(**dict(cc.hf_args_train))


    log("\n###### User Data Load   #############################################")
    from utilmy import load_function_uri
    ### String names --> Create Python function object
    dataloader_fun = load_function_uri(cc.dataloader_name, globals())
    datamapper_fun = load_function_uri(cc.datamapper_name, globals())

    df, df_val = dataloader_fun(dirdata)  ## = dataXX_load_prepro()
    labelEngine, meta_dict = datamapper_fun(f"{dirdata}/meta/meta.json")  ## Label to Index, Index to Label
    # L2I, I2L, NLABEL_TOTAL, meta_dict = datamapper_fun()  ## Label to Index, Index to Label

    df, df_val = df.iloc[:cc.n_train, :], df_val.iloc[:cc.n_val, :]
    log(df_val.shape)

    if "params_data":
        cc.data = {}
        cc.data.cols = df.columns.tolist()
        cc.data.cols_required = ["text", "labels"]
        # cc.data.cols_remove   = ['overflow_to_sample_mapping', 'offset_mapping', ] + columns
        # cc.data.nclass        = NCLASS  ### Number of NER Classes.
        cc.data.meta_dict = meta_dict

        NLABEL_TOTAL = cc.data.meta_dict['NLABEL_TOTAL']
        I2L = cc.data.meta_dict['I2L']  ### label to Index Dict
        L2I = cc.data.meta_dict['L2I']  ### Index to Label Dict
        cc.data.nlabel_total = NLABEL_TOTAL  ### Number of NER Classes.
        cc.data.sequence_max_length = 128

        cc.hf_args_model.num_labels = NLABEL_TOTAL  ## due to BOI notation

 
    log("\n###### Dataloader setup  #######################################")
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
    tokenizer.pad_token = tokenizer.eos_token

    dataset_train = data_tokenize_split(df, tokenizer, labelEngine, cc, )
    dataset_valid = data_tokenize_split(df_val, tokenizer, labelEngine, cc, filter_rows=False) ### No filtering, prevent len(df_val) <> len(dataset_valid)


    data_collator = DataCollatorClassification(tokenizer=tokenizer)
    batch = data_collator([dataset_train[0], dataset_train[1]])
    log(batch)

    compute_metrics = metrics_callback_train

    log("\n######### Model : Init #########################################")
    model = AutoModelForSequenceClassification.from_pretrained(cc.model_name,
                                                               ### All labels are projected in OneHot
                                                               num_labels=cc.hf_args_model.num_labels,
                                                               id2label=I2L,
                                                               label2id=L2I,
                                                               problem_type="multi_label_classification")

    # for i in model.deberta.parameters():
    #   i.requires_grad=False

    log("\n######### Model : Training start ##############################")
    trainer = Trainer(model, args,
                      train_dataset=dataset_train,
                      eval_dataset=dataset_valid,
                      data_collator=data_collator,
                      tokenizer=tokenizer,
                      compute_metrics=compute_metrics,
                      )

    json_save(cc, f'{cc.dirout}/config.json')
    trainer_output = trainer.train()
    trainer.save_model(f"{cc.dirout}/model")

    cc['metrics_trainer'] = trainer_output.metrics
    log(str(cc)[:100])
    json_save(cc, f'{cc.dirout}/meta.json', show=0)
    json_save(cc, f'{cc.dirout}/model/meta.json', show=0)  ### Required when reloading for inference

    log("\n######### Model : Eval Predict  ######################################")
    # assert len(df_val) == len(dataset_valid)
    preds_proba, labels, _ = trainer.predict(dataset_valid)
    df_val = pd_predict_format(df_val, preds_proba, labels, labelEngine)
    assert df_val[["text", "labels", "pred_labels", "pred_proba"]].shape
    pd_to_file(df_val, f'{cc.dirout}/dfval_pred_labels.parquet', show=1)

    log("\n######### Model : Eval Metrics #######################################")
    metrics_calc_full(df_val, metric_list=["accuracy", "f1", "precision", "recall"],
                      dirout=f'{cc.dirout}/dfval_pred_metrics.csv', cc=cc)


def pd_predict_format(df_val: pd.DataFrame, preds_score: list, labels: list,  labelEngine=None) -> pd.DataFrame:
    """ preds_proba: (batch, seq, NCLASS*2+1)    [-3.52225840e-01  5.51

        labels:      (batch,seq)   [[ 0   0   1   1   0    1   1    0   0   0   ]
                                    [ 0   0   1   1   0    1   1    0   0   0   ]]
        pred_labels: (batch, seq)  [[ 1  0  0  1   0  1  0  1  1  0  1 ]
                                    [ 1  0  0  1   0  1  0  1  1  0  1 ] ]

     
     BE CAREFUL Many  cases :

         Softmax :  1 single Label per prediction class:  np.argmax(preds_proba, axis=-1)
  
         Sigmoid :  Manay Label per prediction class :     1 if proba > 0.5 else 0

    """
    def score_to_proba(score):
        return 1 / (1 + np.exp(-score))
    
    preds_proba =score_to_proba(preds_score)

    def labels_calc_softmax():
        ### SoftMax : 1 label for all of labels ( only one  1  per list)
        pred_labels = np.argmax(preds_proba, axis=-1)
        return pred_labels

    def labels_calc_softmax_multi(label_idx_list):
        ### SoftMax : 1 label for for each class group,
        pred_labels = []
        for label_idx in label_idx_list:
            pi = np.argmax(preds_proba[label_idx], axis=-1)
            pred_labels.append(pi)

        return pred_labels

    def labels_calc_sigmoid(proba_threshold=0.5):
        ### Multi-label, mutli class : Each Label is Indepedent        
        pred_labels = [[1 if pi > proba_threshold else 0 for pi in yproba_list] for yproba_list in list(preds_proba)]
        return pred_labels

    def labels_calc_sigmoid_pair(proba_threshold=0.5):
        ### Pair are dependant one_hot
        pred_labels = []
        for yproba_list in list(preds_proba):
            pi0=yproba_list[0]
            pred_labels_i=[]
            for pi1 in yproba_list[1:]:
                if pi1 > pi0:
                    pred_labels_i.extend([0,1])
                else:    
                    pred_labels_i = [1,0]
                pi0 = pi1    
            pred_labels.append(pred_labels_i) 
            
        return pred_labels


    pred_labels = labels_calc_sigmoid(proba_threshold=0.5)


    log("\npred_proba: ", len(preds_proba[0]) ,str(preds_proba)[:50], )
    log("labels: ",       str(labels)[:50])
    log("pred_class: ",   str(pred_labels)[:50], "\n\n")

    assert len(preds_proba) == len(df_val) and len(pred_labels) == len(df_val)
    df_val['pred_score']  = list(preds_score)
    df_val['pred_proba']  = list(preds_proba)
    df_val['pred_labels'] = list(pred_labels)  ### 2D array into List of List  ## ValueError: Expected a 1D array, got an array with shape (2, 25)

    # df_val['pred_class_list_records'] = pd_predict_convert_class_to_records(df_val,)
    return df_val


################################################################################
########## Metrics Helper    ###################################################
def metrics_callback_train(p):
    from sklearn.metrics import f1_score, accuracy_score, precision_recall_fscore_support

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    pthreshold = 0.5
    ##### Softmax
    # preds = p.predictions.argmax(-1)

    ##### sigmoid   
    preds_2d = []
    for logit_list in p.predictions:
        preds_2d.append([1 if sigmoid(logit) > pthreshold else 0 for logit in logit_list])

    labels_2d = p.label_ids

    dd = {}
    dd["accuracy"] = accuracy_score(labels_2d, preds_2d)
    dd["precision"], dd["recall"], dd["f1"], support = precision_recall_fscore_support(labels_2d, preds_2d,
                                                                                       average='weighted')

    return dd


def metrics_calc_full(df=None, metric_list=None, dirout=None, dirin=None, cc=None, dirmeta=None):
    """ Calcualte metrics per column class using numpy, sklearn.

       export dexp="ztmp/exp/240616/000715-class_deberta-12000" 
       pycat metrics_calc_full --dirin "$dexp/dfval_pred_labels.parquet"  --dirout "$dexp/dfmetrics_v1.csv"  --dirmeta "$dexp/config.json"


       dirin = "ztmp/exp/20240524/214636-class_deberta-6/dfval_pred_labels.parquet"
       df    = pd_read_file(dirin)
       dfm   = metrics_calc_full(df, metric_list=["accuracy", "f1"], dirout=None)       
       
       
       
    """
    from utils.util_metrics import metrics_eval
    
    if isinstance(dirin, str):
        df = pd_read_file(dirin)
    assert df[[ "pred_labels", "labels", "pred_proba"]].shape 

    if metric_list is None:
        metric_list = ["accuracy", "f1", "precision", "recall", "confusion_matrix"]
        
    #### Fetch Mapping OneHot to Label global #########################
    if cc is not None:
        I2L =cc["data"]["meta_dict"]["I2L"] 
           
    elif isinstance(dirmeta, str):
        cc = json_load(dirmeta)
        I2L =cc["data"]["meta_dict"]["I2L"] 
        
    else:
        n_labels = len(df['labels'].values[0])
        I2L = { str(icol): f"onehot_{icol}" for  icol in range(n_labels) }        
    log("cols_I2L:", str(I2L)[:100] )
       
       
    def np_to_single_array(array_array):
        return np.array([list(arr) for arr in array_array])

    pred_2d = np_to_single_array(df["pred_labels"].values)
    true_2d = np_to_single_array(df["labels"].values)
    pred_proba_2d = np_to_single_array(df["pred_proba"].values)
    assert pred_2d.shape == true_2d.shape

    n_labels = len(pred_2d[0])
    dfall    = pd.DataFrame()  ### Metrics
    for icol in range(n_labels):
        dfi = metrics_eval(ypred=pred_2d[:, icol],
                           ytrue=true_2d[:, icol],
                           ypred_proba=pred_proba_2d[:, icol],
                           metric_list=metric_list)

        #### Need to map One Hot colid to class name using I2L
        dfi["class_name"] = I2L[ str(icol) ]
        dfall = pd.concat((dfall, dfi))

    dfall.index = np.arange(0, len(dfall))
    dfall       = dfall[ sorted(list(dfall.columns)) ] #### by Alphabet order
    assert dfall[["class_name", "metric_name", "metric_val", "n_sample"]].shape

    if dirout is not None:
        pd_to_file(dfall, dirout, sep="\t", show=1)

    return dfall





################################################################################
########## Run Inference  ######################################################
def run_infer_file(cfg:str=None, dirmodel="ztmp/exp/240520/235015/model/", 
                cfg_name    = "multilabel_predict_v1",
                dirdata     = "ztmp/data/cats/toxicity/val/",
                coltext     = "text",
                dirout      = "ztmp/data/ner/predict/",
                nrows        = 10000,
                do_metrics = False
                  ):
    """Run prediction using pre-trained 

    ### Usage
        export pycat="python nlp/cats/multilabel.py "

        export dexp="ztmp/exp/240616/000715-class_deberta-12000"  
        pycat run_infer_file --nrows 10 --dirmodel "$dexp/model"  --dirdata "$dexp/dfval_pred_labels.parquet"  --dirout "$dexp/predict"

        ### config
           pycat run_infer_file --cfg config/train.yml     --cfg_name "multilabel_predict_v1"


    Params:
            cfg (dict)    : Configuration dictionary (default is None).
            dirmodel (str): path of pre-trained model 
            dirdata (str) : path of input data 
            coltext (str) : Column name of text
            dirout (str)  : path of output data 

        #log(model.predict("My name is John Doe and I love my car. I bought new car in 2020."))

    """
    cfg0 = config_load(cfg,)
    cfg0 = cfg0.get(cfg_name, None) if isinstance(cfg0, dict) else None 
    if  isinstance( cfg0, dict) : 
        dirmodel = cfg0.get("dirmodel", dirmodel)
        dirdata  = cfg0.get("dirdata",  dirdata)
        dirout   = cfg0.get("dirout",   dirout)
        nrows    = cfg0.get("nrows",    nrows)
            
    # Model init
    model               = AutoModelForSequenceClassification.from_pretrained(dirmodel,)
    tokenizer           = AutoTokenizer.from_pretrained(dirmodel)
    tokenizer.pad_token = tokenizer.eos_token
    data_collator       = DataCollatorClassification(tokenizer)
    trainer             = Trainer(model,data_collator  = data_collator,)

    ##### Label init
    labelEngine = LABELdata()
    labelEngine.load_metadict( dirmodel + "/meta.json")  ### only ['data']["meta_dict"]
    
    log("##### cc config", dirmodel)
    cc = json_load(dirmodel + "/meta.json") ### Extra data
    cc = Box(cc)
    
    
    flist = exp_get_filelist(dirdata)
    log(f"\n######### Model : Predict start  #########################")
    for ii,fi in enumerate(flist) :
        df = pd_read_file(fi,nrows=nrows)
        # del df["labels"]

        df['text'] = df[coltext]
        if 'labels' not in df.columns:
            df['labels'] = [ "," * labelEngine.NLABEL_TOTAL ] * len(df)
            
        ##### Fake label to easy use previous function 
        dataset_valid = data_tokenize_split(df, tokenizer, labelEngine, cc, filter_rows=False)
        
        log(f"\n##### Predict: {ii}  ##############################")
        preds_score_2d, labels_2d, _ = trainer.predict(dataset_valid)
        
        df = pd_predict_format(df, preds_score_2d, labels_2d, labelEngine)
        assert df[[  "pred_proba", "pred_labels"     ]].shape
        pd_to_file(df, dirout + f"/df_predict_{ii}.parquet", show=1)

        if do_metrics:
            log("\n f######### Model : Eval Metrics {ii} ##############################")
            metrics_calc_full(df, metric_list=["accuracy", "f1", "precision", "recall", "confusion_matrix"],
                            dirout=f'{cc.dirout}/metrics/dfval_pred_metrics_{ii}.csv', cc=cc)            

    log(df.head(1).T)
    log("########## Model : Predict End #########################")


def run_infer_live(cfg: str = None, cfg_name="cats_multilabel_infer",
                    dirmodel="ztmp/models/gliclass/small",
                    dirdata="ztmp/data/text.csv",
                    coltext="text",
                    dirout="ztmp/data/class/predict/",
                    device="cpu",
                    batch_size=8,
                    nmax=10,
                    ):
    """Run prediction using a pre-trained  Deberta model.

     ### Usage
       alias pycat="python nlp/cats/multilabel.py "
       export dirmodel="./ztmp/exp/20240525/174321-class_deberta-6/model"

          pycat run_infer_batch --dirmodel $dirmodel  --dirdata "ztmp/data/cats/arxiv/val/*"  --dirout ztmp/out/class/deberta_arxiv/

          pycat run_infer_batch --cfg config/train.yaml     --cfg_name "cats_deberta_infer_v1"

     Args:
         cfg (dict)    : Configuration dictionary (default is None).
         dirmodel (str): path of pre-trained model
         dirdata (str) : path of input data
         coltext (str) : Column name of text
         dirout (str)  : path of output data

       #log(model.predict("My name is John Doe and I love my car. I bought a new car in 2020."))
       #df["class_list_pred"] = df[coltext].apply(lambda x: model.predict(x, flat_class=True, threshold=0.5, multi_label=False))

    """
    from transformers import pipeline

    log("\n#### User config   ####################################################")
    cfg0 = config_load(cfg, )
    cfg0 = cfg0.get(cfg_name, {}) if isinstance(cfg0, dict) else {}

    dirmodel = cfg0.get("dirmodel", dirmodel)
    dirdata = cfg0.get("dirdata", dirdata)
    dirout = cfg0.get("dirout", dirout)
    dirmeta = dirmodel + "/meta.json"
    batch_size = cfg0.get("batch_size", batch_size)

    task = "text-classification"
    # device = torch_get_device(device)

    log("\n#### Model pre-trained config   #######################################")
    cc = config_load(dirmeta)
    log(str(cc)[:80])
    class_cols: list = cc.data.get("class_cols", None)
    class_cols = ["gender", "color", "style", ] if class_cols is None else class_cols

    log("\n#### Model Load  ######################################################")
    ###  tasks are [ 'conversational',  'document-question-answering', 'feature-extraction', 'fill-mask', 'mask-generation', 'ner', 'object-detection', 'question-answering', 'sentiment-analysis', 'summarization', 'table-question-answering', 'text-classification', 'text-generation', 'text-to-audio', 'text-to-speech', 'text2text-generation', 'token-classification', 'translation',  'vqa', 'zero-shot-audio-classification', 'zero-shot-classification', 'translation_XX_to_YY']"
    pipe = pipeline(task=task, model=dirmodel, tokenizer=dirmodel, device=device)
    log(str(pipe)[:80])

    log("\n#### Inference Start loop  ############################################")
    flist = exp_get_filelist(dirdata)
    for ii, fi in enumerate(flist):
        df = pd_read_file(fi, nrows=nmax)
        log(ii, fi, df.shape)

        ### {'label': 'DC', 'score': 0.5918803811073303} per row
        pred_list_records = pipe(df[coltext].tolist(), batch_size=batch_size)
        df["pred_list_records"] = pred_list_records

        # assert df[[ "text", "labels", "pred_labels", "pred_proba"     ]].shape
        pd_to_file(df, f'{dirout}/df_pred_labels_{ii}.parquet', show=1)
    log("\n#### Inference End ##################################################")




################################################################################
########## Eval   ##############################################################
def run_eval(cfg:str=None, dirmodel="ztmp/exp/240520/235015/model/", 
                cfg_name    = "multilabel_predict_v1",
                dirdata     = "ztmp/data/cats/toxicity/val/",
                coltext     = "text",
                dirout      = "ztmp/data/ner/predict/",
                nrows        = 10000,
                  ):
    """Run prediction using pre-trained 
    ### Usage
        export pycat="python nlp/cats/multilabel.py "

        export dexp="ztmp/exp/240616/000715-class_deberta-12000"  
        pycat run_eval  --nrows 10 --dirmodel "$dexp/model"  --dirdata "$dexp/dfval_pred_labels.parquet"  --dirout "$dexp/predict"

        pycat run_eval  --nrows 100000 --dirmodel "$dexp/model"  --dirdata "$dexp/dfval_pred_labels.parquet"  --dirout "$dexp/predict"

        pycat run_eval  --cfg config/train.yml     --cfg_name "multilabel_predict_v1"


    """
    run_infer_file(cfg=cfg, dirmodel=dirmodel, 
                cfg_name    = cfg_name,
                dirdata     = dirdata,
                coltext     = coltext,
                dirout      = dirout,
                nrows        = nrows,
                do_metrics = True
                  )



def run_eval2(cfg: str = None,
              cfg_name="cats_gliclass_predict",
              dirmodel="ztmp/models/gliclass/small",
              dirdata="ztmp/data/text.csv",
              coltext="text",
              dirout="ztmp/data/class/predict/",
              device="cpu"
              ):
    """Run prediction using a pre-trained  Deberta model.

     ### Usage
       alias pycat="python nlp/cats/multilabel.py "


       dirmodel="./ztmp/exp/20240525/174321-class_deberta-6/model"

       pycat run_infer_batch --dirmodel $dirmodel  --dirdata "ztmp/data/cats/arxiv/val/*"  --dirout ztmp/out/class/deberta_arxiv/

       pycat run_infer_batch --cfg config/train.yaml     --cfg_name "cats_deberta_infer_v1"

     Args:
         cfg (dict)    : Configuration dictionary (default is None).
         dirmodel (str): path of pre-trained model
         dirdata (str) : path of input data
         coltext (str) : Column name of text
         dirout (str)  : path of output data


       #log(model.predict("My name is John Doe and I love my car. I bought a new car in 2020."))
       #df["class_list_pred"] = df[coltext].apply(lambda x: model.predict(x, flat_class=True, threshold=0.5, multi_label=False))

    """
    cfg0 = config_load(cfg, )
    cfg0 = cfg0.get(cfg_name, {}) if isinstance(cfg0, dict) else {}

    dirmodel = cfg0.get("dirmodel", dirmodel)
    dirdata  = cfg0.get("dirdata", dirdata)
    dirout   = cfg0.get("dirout", dirout)
    dirmeta  = dirmodel + "/meta.json"

    log("\n### Inference config   #####################################################")
    cc = config_load(dirmeta)
    log(str(cc)[:80])

    class_cols: list = cc.data.get("class_cols", None)
    class_cols = ["gender", "color", "style", ] if class_cols is None else class_cols

    log("\n### Model Load  ############################################################")
    model = AutoModelForSequenceClassification.from_pretrained(dirmodel, )
    tokenizer = AutoTokenizer.from_pretrained(cc.model_name)
    tokenizer.pad_token = tokenizer.eos_token

    labelEngine = LABELdata()
    labelEngine.load_metadict(dirmeta=dirmeta)
    log(str(model)[:20])

    def preprocess_func(row):
        #### Text tokenizer
        out = tokenizer(row["text"])

        return out

    model.eval()
    flist = exp_get_filelist(dirdata)
    for ii, fi in enumerate(flist):
        df = pd_read_file(fi)
        log(ii, fi, df.shape)

        pred_list = torch_model_predict(model, df["text"].values, device="cpu", tokenizer=tokenizer, show=1)
        df["pred_labels"] = pred_list

        # dataset_valid = data_tokenize_split(df, tokenizer=tokenizer,labelEngine=labelEngine, cc=cc )
        # ds = Dataset.from_pandas(df[["text"  ]])
        # ds = ds.map(preprocess_func, batched=True, return_tensors="pt")
        # encoded_input = tokenizer(text)
        # encoded_input["input_ids"] = encoded_input.pop("input_ids")  # Add input_ids to  encoded_input
        # encoded_input = {k: v.to(device) for k, v in encoded_input.items()}
        # encoded_input = {k: v.to(device) for k, v in ds.items()}
        # X= [ tokenizer(txt, return_tensors="pt") for txt in df["txt"].values       ]

        # preds_proba, labels, _ = model(**X)
        # df = pd_predict_format(df, preds_proba, labels, cc=cc)
        # assert df[["text", "labels", "pred_labels", "pred_proba"]].shape
        # pd_to_file(df, f'{dirout}/df_pred_labels_{ii}.parquet', show=1)



def apple():
    """
    1. Install PyTorch with MPS support:
        ```bash
        pip install torch torchvision torchaudio
        ```

    2. Set the environment variable to enable MPS fallback:
        ```bash
        export PYTORCH_ENABLE_MPS_FALLBACK=1
       ```

            For more details, refer to the [Hugging Face documentation](https://huggingface.co/docs/accelerate/en/usage_guides/mps) and [PyTorch documentation](https://huggingface.co/docs/transformers/en/perf_train_special).

            Citations:
            [1] https://huggingface.co/docs/accelerate/en/usage_guides/mps
            [2] https://discuss.huggingface.co/t/is-or-will-be-gpu-accelerating-supported-on-mac-device/7554
            [3] https://huggingface.co/docs/transformers/en/perf_train_special
            [4] https://forums.developer.apple.com/forums/thread/683922
            [5] https://discuss.huggingface.co/t/m2-max-gpu-utilization-steadily-dropping-while-running-inference-with-huggingface-distilbert-base-cased/35995
            [6] https://github.com/huggingface/text-embeddings-inference/issues/18
            [7] https://huggingface.co/docs/diffusers/en/optimization/mps
            [8] https://forums.developer.apple.com/forums/thread/693678
            [9] https://github.com/huggingface/diffusers/issues/292



    """
    
      
    ## 3. Use the `mps` device in your Hugging Face code:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    model.to(device)

    inputs = tokenizer("Hello, my dog is cute", return_tensors="pt").to(device)
    outputs = model(**inputs)



########################################################################################
####### Tooling ########################################################################
def data_load_convert_todict(dirin=".ztmp/arxiv_data.csv", fun_name="dataset_arxiv", label_nunique=None):
    """  Create custom category from raw label
         ['cs.CV', 'cs.AI', 'cs.LG']

    """
    from utilmy import load_function_uri
    dataset_loader_fun = globals()[fun_name]
    df, meta_dict = dataset_loader_fun(dirin)

    label_nunique = meta_dict.get("label_nunique")  ## number of unique categories per label
    if label_nunique is None:
        label_nunique = {"cat1": 3, "cat2": 5, "cat3": 6, "cat4": 7, }

    ####### Big OneHot Encoded  ######################################
    colslabel = [key for key in label_nunique.keys()]
    n_class_total = sum([label_nunique[key] for key in label_nunique.keys()])

    for collabel in colslabel:
        df[f"{collabel}_onehot"] = cat_to_onehot(df[collabel].values, ndim=label_nunique[collabel])

    df["cat_all_onehot"] = df.apply(lambda x: sum([x[ci + "_onehot"] for ci in colslabel]), axis=1)

    # Convert DataFrame to a dictionary
    data = {
        "text": df["text"].tolist(),
        "labels": df["cat_all_onehot"].values.tolist(),
    }
    return data, label_nunique, n_class_total


def cat_to_onehot(cat_val: list, ndim=None):
    """ 
        # Example usage
        categories = ['2', '0', '1', '2']  # Example category indices as strings
        ndim = 3  # Number of unique categories
        encoded = encode_categories(categories, ndim)
        print(encoded)

    """
    from sklearn.preprocessing import OneHotEncoder
    import numpy as np

    ndim = ndim if ndim is not None else len(np.unique(cat_val))

    # Ensure  input is an array
    categories = np.array(cat_val).reshape(-1, 1)

    # Create  OneHotEncoder with  specified number of dimensions
    encoder = OneHotEncoder(categories=[np.arange(ndim)], sparse=False)
    onehot = encoder.fit_transform(categories)
    return onehot


def pd_predict_convert_class_to_records(df_val: pd.DataFrame, offset_mapping: list,
                                        col_classlist="pred_class_list", col_text="text") -> pd.DataFrame:
    """Convert predicted classes into span records for NER.

    Args:
        df_val (pd.DataFrame): DataFrame containing input data. It should have following columns:
            - col_classlist (str): Column name for predicted classes.
            - col_text (str): Column name for text.
        offset_mapping (list): List of offset mappings.

    Returns:
        list: List of span records for NER. Each span record is a dictionary with following keys:
            - text (str): text.
            - class_list (list): List of named entity records. Each named entity record is a dictionary with following keys:
                - type (str)            : type of named entity.
                - predictionstring (str): predicted string for named entity.
                - start (int)           : start position of named entity.
                - end (int)             : end position of named entity.
                - text (str)            : text of named entity.

    """

    # print(df_val)
    # assert df_val[[ "text", "input_ids", "offset_mapping", "pred_class_list"  ]]
    def get_class(c):
        if c == NCLASS * 2:
            return 'Other'
        else:
            return I2L[c][2:]

    def pred2span(pred_list, df_row, viz=False, test=False):
        #     example_id = example['id']
        n_tokens = len(df_row['offset_mapping'][0])
        #     print(n_tokens, len(example['offset_mapping']))
        classes = []
        all_span = []
        for i, c in enumerate(pred_list.tolist()):
            if i == n_tokens - 1:
                break
            if i == 0:
                cur_span = df_row['offset_mapping'][0][i]
                classes.append(get_class(c))
            elif i > 0 and (c == pred_list[i - 1] or (c - NCLASS) == pred_list[i - 1]):
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
            span_start = span[0]
            span_end = span[1]
            before = text[:span_start]
            token_start = len(before.split())
            if len(before) == 0:
                token_start = 0
            elif before[-1] != ' ':
                token_start -= 1

            num_tkns = len(text[span_start:span_end + 1].split())
            tkns = [str(x) for x in range(token_start, token_start + num_tkns)]
            predstring = ' '.join(tkns)
            predstrings.append(predstring)

        #### Geclassate Record format 
        row = {"text": text, "class_list": []}
        es = []
        for class_type, span, predstring in zip(classes, all_span, predstrings):
            if class_type != 'Other':
                e = {
                    'type': class_type,
                    'value': predstring,
                    'start': span[0],
                    'end': span[1],
                    'text': text[span[0]:span[1]]
                }
                es.append(e)
        row["class_list"] = es

        return row

    #### Convert
    pred_class = df_val[col_classlist].values
    valid = df_val[[col_text]]
    valid['offset_mapping'] = offset_mapping
    valid = valid.to_dict(orient="records")

    ### pred_class : tuple(start, end, string)
    predicts = [pred2span(pred_class[i], valid[i]) for i in range(len(valid))]

    return [row['class_list'] for row in predicts]

    # pd_to_file( predicts, dirout + '/predict_class_visualize.parquet' )
    # pred = pd.read_csv("nguyen/20240215_171305/predict.csv")
    # pred
    # pred = pred[["text", "class_list"]]
    # eval(pred.class_tag.iloc[0])
    # pred["class_list"] = pred["class_list"].apply(eval)






###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()






def zz_run_eval3(dirmodel, device="cpu", dirdata=".ztmp/data/arxiv_data/eval/", dataloader_name="dataset_arxiv", topk=3):
    """Eval

    python multilabel.py --dirmodel "./ztmp/pretrained/" --dirdata ".ztmp/data/arxiv_data/eval/"

    Args:
        dirmodel (str):  directory path of  model to be evaluated.
        device (str, optional):  device on which to run  evaluation. Defaults to "cpu".
        dirdata (str, optional):  directory path of  data for evaluation. Defaults to ".ztmp/data/arxiv_data/eval/".
        dataloader_name (str, optional):  name of  dataloader. Defaults to "dataset_arxiv".
        topk (int, optional):  number of top labels to consider. Defaults to 3.
    """
    model = DebertaForSequenceClassification.from_pretrained(dirmodel)

    log("##### Load Data")
    data, class_info, n_class_total = data_load_convert_todict(dirin=dirdata, fun_name=dataloader_name, )
    train_dataset, test_dataset, tokenizer = data_tokenize_split(data)
    class_names = class_info["class_name"]

    log("##### Inference start")
    model.eval()
    text_list = [example["text"] for example in test_dataset]
    pred_cat = []
    preds_lsit = torch_model_predict(model, text_list, device="cpu", tokenizer=None, show=1)


def torch_model_predict(model, text_list, device="cpu", tokenizer=None, show=1):
    pred_list = []
    for text in text_list:
        encoded_input = tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=128
        )
        encoded_input["input_ids"] = encoded_input.pop("input_ids")  # Add input_ids to  encoded_input

        encoded_input = {k: v.to(device) for k, v in encoded_input.items()}

        output = model(**encoded_input)
        preds = torch.sigmoid(output.logits).squeeze().detach().numpy()

        pred_list.append(preds)

        # top_labels  = np.argsort(preds)[-topk:]  # Get  top N labels
        # pred_labels = [class_names[i] for i in top_labels]  # Get  corresponding labels
        # pred_cat.append(pred_labels)

    if show > 0:
        #### Print abstracts with predicted labels
        for text, preds in zip(text_list, pred_list):
            print(f"Input: {text}\nPrediction: {preds}\n")
            break

    return pred_list





""" logs 

(py39) \W$        pycat metrics_calc_full --dirin "$dexp/dfval_pred_labels.parquet"  --dirout "$dexp/dfmetrics_v1.csv"  --dirmeta "$dexp/config.json"
cols_I2L: {'0': 'identity_hate_NO', '1': 'identity_hate', '2': 'insult', '3': 'insult_NO', '4': 'obscene', '5': 'obscene_NO', '6': 'severe_toxic', '7': 'severe_toxic_NO', '8': 'threat_NO', '9': 'threat', '10': 'toxic', '11': 'toxic_NO'}
ztmp/exp/240616/000715-class_deberta-12000/dfmetrics_v1.csv
        metric_name  metric_val  n_sample  n_sample_y1        class_name
0    accuracy_score    0.905393      3245       2938.0  identity_hate_NO
1          f1_score    0.950348      3245       2938.0  identity_hate_NO
2   precision_score    0.905393      3245       2938.0  identity_hate_NO
3      recall_score    1.000000      3245       2938.0  identity_hate_NO
4    accuracy_score    0.905393      3245        307.0     identity_hate
5          f1_score    0.000000      3245        307.0     identity_hate
6   precision_score    0.000000      3245        307.0     identity_hate
7      recall_score    0.000000      3245        307.0     identity_hate
8    accuracy_score    0.724499      3245       1592.0            insult
9          f1_score    0.695089      3245       1592.0            insult
10  precision_score    0.760448      3245       1592.0            insult
11     recall_score    0.640075      3245       1592.0            insult
12   accuracy_score    0.698921      3245       1653.0         insult_NO
13         f1_score    0.682070      3245       1653.0         insult_NO
14  precision_score    0.738028      3245       1653.0         insult_NO
15     recall_score    0.633999      3245       1653.0         insult_NO
16   accuracy_score    0.824961      3245       1677.0           obscene
17         f1_score    0.823821      3245       1677.0           obscene
18  precision_score    0.858436      3245       1677.0           obscene
19     recall_score    0.791890      3245       1677.0           obscene
20   accuracy_score    0.802773      3245       1568.0        obscene_NO
21         f1_score    0.774489      3245       1568.0        obscene_NO
22  precision_score    0.865354      3245       1568.0        obscene_NO
23     recall_score    0.700893      3245       1568.0        obscene_NO
24   accuracy_score    0.903852      3245        312.0      severe_toxic
25         f1_score    0.000000      3245        312.0      severe_toxic
26  precision_score    0.000000      3245        312.0      severe_toxic
27     recall_score    0.000000      3245        312.0      severe_toxic
28   accuracy_score    0.906317      3245       2933.0   severe_toxic_NO





(py39) (py39) \W$       pycat run_infer_batch --dirmodel $dirmodel  --dirdata "ztmp/data/cats/arxiv/val/*"  --dirout ztmp/out/class/deberta_arxiv/

Config: Using /Users/macair/conda3/envs/py39/lib/python3.9/site-packages/utilmy/configs/myconfig/config.yaml
Config: Loading  /Users/macair/conda3/envs/py39/lib/python3.9/site-packages/utilmy/configs/myconfig/config.yaml
Config: Cannot read file /Users/macair/conda3/envs/py39/lib/python3.9/site-packages/utilmy/configs/myconfig/config.yaml 'str' object has no attribute 'suffix'
Config: Using default config
{'field1': 'test', 'field2': {'version': '1.0'}}

### Inference config   #####################################################
Config: Loading  ztmp/exp/20240525/174321-class_deberta-6/model/meta.json
{'model_name': 'microsoft/deberta-v3-base', 'dataloader_name': 'data_arxiv_load'

### Model Load  ############################################################
<transformers.pipelines.text_classification.TextClassificationPipeline object at

### Start Inference loop  ############################################################
nFiles:  1
0 ztmp/data/cats/arxiv/val/df_2000.parquet (10, 10)
ztmp/out/class/deberta_arxiv//df_pred_labels_0.parquet
                                           abstracts  ...                             pred_list_records
0  We present DeepMVI, a deep learning method for...  ...  {'label': 'DC', 'score': 0.5918803811073303}
1  We introduce Neural Contextual Anomaly Detecti...  ...  {'label': 'DC', 'score': 0.5875549912452698}
2  An innovations sequence of a time series is a ...  ...  {'label': 'DC', 'score': 0.5880179405212402}
3  In order to mitigate spread of COVID-19, W...  ...  {'label': 'DC', 'score': 0.5901156663894653}
4  While previous distribution shift detection ap...  ...  {'label': 'DC', 'score': 0.5917407274246216}
5  We predict emergence of extreme events in ...  ...  {'label': 'DC', 'score': 0.5919176340103149}
6  spread of COVID-19 has coincided with ...  ...  {'label': 'DC', 'score': 0.5906561017036438}
7  Until recently, most accurate methods for ...  ...  {'label': 'DC', 'score': 0.5906267762184143}
8  Intelligent diagnosis method based on data-dri...  ...  {'label': 'DC', 'score': 0.5890864729881287}
9  Extracting interaction rules of biological...  ...   {'label': 'DC', 'score': 0.590703547000885}

[10 rows x 11 columns]
(py39) (py39) \W$ 



"""







    
# Custom metric for evaluation
def zz_compute_metrics(eval_pred):
    ### not working
    logits = eval_pred.predictions
    labels = eval_pred.label_ids
    predictions = (torch.sigmoid(torch.Tensor(logits)) > 0.5).int()
    f1 = f1_score(torch.Tensor(labels).int().cpu().numpy(), predictions.cpu().numpy(), average='samples')
    return {"f1": f1}


def zz_metrics_calc_callback_train_v2(eval_pred):
    """  Durinh HugginFace training 
        Not working with evaluate

            import evaluate
            import numpy as np

            clf_metrics = evaluate.combine(["accuracy", "f1", "precision", "recall"])

            def sigmoid(x):
               return 1/(1 + np.exp(-x))

        def compute_metrics(eval_pred):

            predictions, labels = eval_pred
            predictions = sigmoid(predictions)
            predictions = (predictions > 0.5).astype(int).reshape(-1)
            return clf_metrics.compute(predictions=predictions, references=labels.astype(int).reshape(-1))
            references=labels.astype(int).reshape(-1))

    """
    # global L2I, I2L

    # metric = datasets.load_metric("seqeval")
    metric = evaluate.combine(["accuracy", "f1", "precision", "recall"])
    # pred_proba, labels = xtuple

    pred_logits = eval_pred.predictions
    labels = eval_pred.label_ids

    # preds = np.argmax(preds_proba, axis=-1)
    pred_labels = (torch.sigmoid(torch.Tensor(pred_logits)) > 0.5).int()

    pred_labels = pred_labels.detach().cpu().numpy()
    labels = np.array(labels, dtype="int32")  # [ [int(x) for x in vlist ] for vlist  in labels ]

    #####
    pred_labels = pred_labels.tolist()
    labels = labels.tolist()

    # Remove ignored index (special tokens)
    # true_preds  =  [I2L[p ] for (p, l) in zip(preds, labels) if l != -100]
    # true_labels =  [I2L[l ] for (_, l) in zip(preds, labels) if l != -100]
    # results = metric.compute(predictions=true_preds, references=true_labels)

    results = metric.compute(predictions=pred_labels, references=labels,
                             average='weighted')

    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
        "accuracy": results["overall_accuracy"],
    }






def zz_data_tokenize_split_v2(data: dict, max_length=128, model_id="microsoft/deberta-base", ):
    # Tokenization
    tokenizer = DebertaTokenizer.from_pretrained(model_id)

    def preprocess_function(examples):
        output = tokenizer(examples["text"], truncation=True, padding=True, max_length=max_length)
        # output["input_ids"] = output.pop("input_ids")  # Add input_ids to  output
        return output

    # Load  dataset
    ds = Dataset.from_dict(data)

    # Encode texts
    ds = ds.map(preprocess_function, batched=True)

    # Remove labels with only a single instance
    label_counts = Counter([tuple(label) for label in ds["labels"]])
    valid_labels = [label for label, count in label_counts.items() if count > 1]
    ds = ds.filter(lambda example: tuple(example["labels"]) in valid_labels)

    # Split dataset into training and validation sets with stratification
    text_train, text_test, labels_train, labels_test = train_test_split(
        ds["text"],
        ds["labels"],
        test_size=0.2,
        random_state=42,
        stratify=ds["labels"],
    )

    train_dataset = Dataset.from_dict(
        {"text": text_train,
         "labels": labels_train,
         "input_ids": ds["input_ids"][: len(text_train)],
         "attention_mask": ds["attention_mask"][: len(text_train)],
         }
    )

    test_dataset = Dataset.from_dict(
        {"text": text_test,
         "labels": labels_test,
         "input_ids": ds["input_ids"][len(text_train):],
         "attention_mask": ds["attention_mask"][len(text_train):],
         }
    )
    return train_dataset, test_dataset, tokenizer


"""
#### Multilabel datasets
Dataset: knowledgator/events_classification_biotech 
Total records: 2759
atleast 2 labels: 1380


Dataset: https://www.kaggle.com/datasets/shivanandmn/multilabel-classification-dataset?select=train.csv
total: 20972
Number of labels: 6
Records with atleast 2 labels:4793
---
Dataset: goemotions (https://github.com/google-research/google-research/tree/master/goemotions)
Total: 70000
Records with atleast 2 labels: 10082
Number of labels: 27 + Neutral.
---
dataset: https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge/data
Total: 159571
Number of labels:  6
Records with atleast 2 labels: 9865
---

dataset: CMU movie corpus (https://www.cs.cmu.edu/~ark/personas)
records: 42,306 records with movie plotline as text 
labels: genre

Note: should work after cleaning the dataset
"""

"""
Findings/Suggestions:
1. There is a mismatch between numlabels and number of labels in meta.json. 
    Possible cause: NA already being taken into account in dataset so +1 shouldnt be required???
    this is still a problem. I suggest we let the NA increment happen organically based on data instead of manually adding it.
2. Arxiv function are misleading and led to more confusion. 
Our requirement is to generate one-hot labels of the form 1,0,1,1 while arxiv function generates cs,CV,cs,LG etc.
This leads to confusion and further delay if developer use it as a reference. Would be better to remove/comment it or 
explicitly mention that it"s not to be used as a reference while writin dataloader for new dataset    
"""
