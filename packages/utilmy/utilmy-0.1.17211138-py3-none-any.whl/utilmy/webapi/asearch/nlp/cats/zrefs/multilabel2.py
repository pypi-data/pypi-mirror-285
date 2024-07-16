""" 
### Install
    pip install fire utilmy


    git clone 
    git checkout devtorch

    cd webapi/asearch/nlp
    mkdir -p ztmp
    python mutilabel.py run_train --device "cpu"



    ttps://www.kaggle.com/datasets/spsayakpaul/arxiv-paper-abstracts

    For label = "cs.ML"
    Cat1 : cs
    Cat2:  ML



### Fine Tuning Strategies using LLM and SetFit

    https://medium.com/@xmikex83/using-large-language-models-to-train-smaller-ones-ee64ff3e4bd3

    https://huggingface.co/MoritzLaurer/deberta-v3-large-zeroshot-v2.0






"""
import os,  pandas as pd, numpy as np, ast
from box import Box


from sklearn.preprocessing import MultiLabelBinarizer
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score
from datasets import Dataset
from sklearn.model_selection import train_test_split
from collections import Counter

from transformers import ( DebertaTokenizer, DebertaForSequenceClassification, 
Trainer, TrainingArguments, TrainerCallback, )
import torch


from transformers import (
    DebertaTokenizer,
    DebertaForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset
import torch

from utilmy import (pd_read_file,log, glob_glob, config_load, os_makedirs, 
                    pd_to_file, date_now,  json_load, json_save)



#################################################################################################
######## Dataloder Customize ####################################################################
def dataset_arxiv(dirin):

    flist = glob_glob(dirin)
    if len(flist)< 1: 
        #### Download from https://www.kaggle.com/datasets/spsayakpaul/arxiv-paper-abstracts
        kaggle_donwload("https://www.kaggle.com/datasets/spsayakpaul/arxiv-paper-abstracts", dirout= dirin )


    df = pd_read_file(dirin, sep="\t")
    log(df.head(5).T, df.columns, df.shape)

    ##### Custom to Arxiv dataset
    df["label2"] = df["terms"].apply(lambda x:  sorted(x.split(",")) )  # ['cs.CV', 'cs.AI', 'cs.LG']
    df["cat1"] = df["label2"].apply(lambda x: x[0].split(".")[0])  # "cs"
    df["cat2"] = df["label2"].apply(lambda x: x[0].split(".")[1])  # "CV"
    df["cat3"] = df["label2"].apply(lambda x: x[1].split(".")[0] if len(x)>0 else "NA" )  # "cs"
    df["cat4"] = df["label2"].apply(lambda x: x[1].split(".")[1] if len(x)>0 else "NA")  # "AI"

    meta_dict = {"label_nunique" : {
                 "cat1": 3, "cat2": 5, "cat3": 6, "cat4": 7, }}

    return df, meta_dict 
















#################################################################################################
######## Dataloder Common #######################################################################
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
    colslabel     = [  key for key in label_nunique.keys()]       
    n_class_total = sum([  label_nunique[key] for key in label_nunique.keys()])

    for collabel in colslabel:    
       df[ f"{collabel}_onehot"] = cat_to_onehot(df[collabel].values , ndim= label_nunique[collabel])

    df["cat_all_onehot"] = df.apply(lambda x :  sum( [x[ci+"_onehot"] for ci in colslabel ] )  ,axis=1 )


    # Convert DataFrame to a dictionary
    data = {
        "text":    df["text"].tolist(),
        "labels":  df["cat_all_onehot"].values.tolist(),
    }
    return data, label_nunique, n_class_total




def cat_to_onehot(cat_val:list, ndim=None):
    """ 
        # Example usage
        categories = ['2', '0', '1', '2']  # Example category indices as strings
        ndim = 3  # Number of unique categories
        encoded = encode_categories(categories, ndim)
        print(encoded)

    """
    from sklearn.preprocessing import OneHotEncoder
    import numpy as np    

    ndim= ndim if ndim is not None else len(np.unique(cat_val))

    # Ensure  input is an array
    categories = np.array(cat_val).reshape(-1, 1)
    
    # Create  OneHotEncoder with  specified number of dimensions
    encoder = OneHotEncoder(categories=[np.arange(ndim)], sparse=False)    
    onehot = encoder.fit_transform(categories)
    return onehot






def data_tokenize_split(data:dict, max_length=128, model_id="microsoft/deberta-base",):
    # Tokenization
    tokenizer = DebertaTokenizer.from_pretrained(model_id)

    def preprocess_function(examples):
        output = tokenizer(examples["text"], truncation=True, padding=True, max_length= max_length)
        # output["input_ids"] = output.pop("input_ids")  # Add input_ids to  output
        return output

    # Load  dataset
    ds = Dataset.from_dict(data)

    # Encode texts
    ds = ds.map(preprocess_function, batched=True)

    # Remove labels with only a single instance
    label_counts = Counter([tuple(label) for label in ds["labels"]])
    valid_labels = [label for label, count in label_counts.items() if count > 1]
    ds           = ds.filter(lambda example: tuple(example["labels"]) in valid_labels)

    # Split dataset into training and validation sets with stratification
    text_train, text_test, labels_train, labels_test = train_test_split(
        ds["text"],
        ds["labels"],
        test_size=0.2,
        random_state=42,
        stratify=ds["labels"],
    )

    train_dataset = Dataset.from_dict(
        {   "text": text_train,
            "labels": labels_train,
            "input_ids": ds["input_ids"][: len(text_train)],
            "attention_mask": ds["attention_mask"][: len(text_train)],
        }
    )

    test_dataset = Dataset.from_dict(
        {   "text": text_test,
            "labels": labels_test,
            "input_ids": ds["input_ids"][len(text_train) :],
            "attention_mask": ds["attention_mask"][len(text_train) :],
        }
    )
    return train_dataset, test_dataset, tokenizer



def run_train(cfg=None, cfgname="train_deberta", device="cpu", model_id = "microsoft/deberta-base",
              dataloader_name="dataset_arxiv"):

    cfg1 = config_load(cfg)
    if cfg1 is None:
        cc = Box({})
        cc.dirout = "./ztmp/results"
        cc.num_train_epochs = 10 
    else:
        cc = Box(cfg1[cfgname])            

    cc.dirmodel = cc.output_dir + "/model/"
    os_makedirs(cc.dirmodel)
    log(cc.dirmodel)


    device = torch.device(device)

    #### Load data
    data, class_info, n_class_total  = data_load_convert_todict(fun_name= dataloader_name)
    train_data, test_data, tokenizer = data_tokenize_split(data, model_id=model_id)
    del data

    #### Load model 
    model = DebertaForSequenceClassification.from_pretrained(model_id, num_labels=len(n_class_total))
    model.to(device)

    #### Collect loss and f1-score for plotting
    mm = Box({})
    mm.losses, mm.training_loss, mm.f1_scores = [], [],[]

    #### Define TrainingArguments
    training_args = TrainingArguments(
        output_dir= cc.dirout,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs= cc.num_train_epochs,
        weight_decay=0.01,
        logging_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
    )

    # Custom callback to log losses and f1-scores
    class CustomCallback(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kwargs):
            if logs is not None:
                mm.losses.append(logs.get("eval_loss", 0.0))
                mm.f1_scores.append(logs.get("eval_f1", 0.0))

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=test_data,
        compute_metrics=compute_metrics,
        callbacks=[CustomCallback()],
    )

    ### Train  model
    json_save(cfg1, cc.dirout + "/config.json")
    trainer.train()

    ### Save  model and tokenizer
    model.save_pretrained(cc.dirmodel )
    tokenizer.save_pretrained(cc.dirmodel)

    ### Metrics
    json_save(mm, cc.dirout + "/metrics.json")



def run_eval(dirmodel, device="cpu", dirdata= ".ztmp/data/arxiv_data/eval/" ,dataloader_name="dataset_arxiv", topk=3):
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
    data, class_info, n_class_total        = data_load_convert_todict(dirin= dirdata, fun_name=dataloader_name,)
    train_dataset, test_dataset, tokenizer = data_tokenize_split(data)
    class_names = class_info["class_name"]


    log("##### Inference start")
    model.eval()
    text_list = [example["text"] for example in test_dataset]
    pred_cat  = []

    for text in text_list:
        encoded_input = tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=128
        )
        encoded_input["input_ids"] = encoded_input.pop("input_ids")  # Add input_ids to  encoded_input

        encoded_input = {k: v.to(device) for k, v in encoded_input.items()}

        output = model(**encoded_input)
        preds  = torch.sigmoid(output.logits).squeeze().detach().numpy()

        top_labels  = np.argsort(preds)[-topk:]  # Get  top N labels
        pred_labels = [class_names[i] for i in top_labels]  # Get  corresponding labels
        pred_cat.append(pred_labels)

    # Print abstracts with predicted labels
    for text, labels in zip(text_list, pred_cat):
        print(f"Abstract: {text}\nPredicted Labels: {labels}\n")



# Custom metric for evaluation
def compute_metrics(eval_pred):
    logits = eval_pred.predictions
    labels = eval_pred.label_ids
    predictions = (torch.sigmoid(torch.Tensor(logits)) > 0.5).int()
    f1 = f1_score(torch.Tensor(labels).int().cpu().numpy(), predictions.cpu().numpy(), average='samples')
    return {"f1": f1}






###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()





