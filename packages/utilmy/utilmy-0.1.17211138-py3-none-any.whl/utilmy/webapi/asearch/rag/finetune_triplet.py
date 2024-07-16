""" 

Personal dataset of triplet ( I have build with GPT)

Input format:
    context,  head, relation, tail.





---> Convert into Rebel Format
         preprocessing_standardize_dataset(

   --> we re-use the news dataset into the training....



"""
import os

import evaluate
from box import Box
from datasets import load_dataset, load_metric, DatasetDict, Dataset
from transformers import BartTokenizer, BartForConditionalGeneration, Seq2SeqTrainingArguments, Seq2SeqTrainer, \
    AutoTokenizer, AutoModelForSeq2SeqLM
import numpy as np

from engine_kg import dbsql_fetch_text_by_doc_ids
from utilmy import log, pd_read_file, pd_to_file
from utils.utils_base import torch_getdevice

# initialize base model and tokenizer
device = torch_getdevice()

tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")
model.to(device)

def preprocessing_get_head_location(row, coltext="context", colhead="head"):
    # print(type(row))
    # print(row)
    try:
        return row[coltext].index(row[colhead])
    except Exception as err:
        print(row)
        return 100000


def preprocessing_transform_relations_to_text_sequence(triplets):
    """
    convert list of triplets to a single string
    eg:
        input:[
        {'head': 'Carlyle Looks Toward Commercial Aerospace', 'type': 'owned by', 'tail': 'Carlyle Group', 'head_location': 0},
        {'head': 'Carlyle Group', 'type': 'owner of', 'tail': 'Carlyle Looks Toward Commercial Aerospace', 'head_location': 86}
        ]
        output: <triplet> Carlyle Looks Toward Commercial Aerospace <subj> Carlyle Group <obj> owned by <triplet> Carlyle Group <subj> Carlyle Looks Toward Commercial Aerospace <obj> owner of
    """
    # Sort triplets by head_location
    triplets = sorted(triplets, key=lambda t: t['head_location'])

    lin_triplets = ""

    # Iterate over sorted triplets
    current_head = None
    for triplet in triplets:
        head = triplet['head']
        tail = triplet['tail']
        relation_type = triplet['type']

        if head != current_head:
            # if current_head is not None:
            #     lin_triplets += "</triplet>"
            lin_triplets += f" <triplet> {head}"
            current_head = head

        lin_triplets += f" <subj> {tail} <obj> {relation_type}"
    lin_triplets = lin_triplets.strip()
    return lin_triplets


def preprocessing_standardize_dataset(
        datadir="ztmp/bench/ag_news/kg_triplets/*/*.parquet",
        outputdir="ztmp/bench/ag_news/ft_data.parquet", nrows=-1):
    """

      What we are doing here:
      convert agnews triplet data into rebel like dataset
            1. load dataset containing triplets in the format:  text_id,  head, relation, tail
            2. generate text from text_id using db
            3. aggregate triplet belonging to the same text_id into a single string
            Refer formatting algorithm here: https://github.com/Babelscape/rebel/blob/main/docs/EMNLP_2021_REBEL__Camera_Ready_.pdf

    Usage: python3 -u rag/ft2.py preprocessing_standardize_dataset --datadir "ztmp/bench/ag_news/kg_triplets/*/*.parquet" --output-dir "ztmp/bench/ag_news/ft_data.parquet" --nrows 10000
    
     Reverse engineer previous output of rebel relation names
       -->
      input : text_id, head, tail, type
      output: context: text from which triplet was generated
            triplets: triplet string of form: <triplet> head <subj> tail <obj> type
    """

    ### we are loading previous Output of Rebel triplet Prediction 
    df = pd_read_file(datadir)
    assert df[[ 'head', 'tail', 'type' 'text_id']].shape
    if nrows > 0:
        df = df.iloc[:nrows]


    # print(df.columns)
    #### actual text is used as Context (ie rebel wording)
    df["context"] = df["text_id"].apply(lambda x: dbsql_fetch_text_by_doc_ids(text_ids=[x])[0]["text"])


    df["head_location"] = df[["head", "context"]].apply(
        lambda x: preprocessing_get_head_location(x, coltext="context", colhead="head"), axis=1)

    # collect triplet components into single column
    df["triplet"] = df.apply(
        lambda x: {"head": x["head"], "type": x["type"], "tail": x["tail"], "head_location": x["head_location"]},
        axis=1)

    # group by text_id, and aggregate triplets into list
    df = df.groupby(["text_id", "context"]).agg({"triplet": lambda x: list(x)}).reset_index()
    # convert list of triplets to a rebel compatible string
    df["triplets"] = df["triplet"].apply(preprocessing_transform_relations_to_text_sequence)
    
    df = df[["context", "triplets"]]
    pd_to_file(df, outputdir, show=1)




def train_tokenize(examples, text_col="context", target_col="triplets", max_length=512, truncation=True):
    """
    convert text and triplets into token embeddings
    """
    inputs = examples[text_col]
    targets = examples[target_col]
    model_inputs = tokenizer(inputs, max_length=max_length, padding=True, truncation=True)

    # Setup the tokenizer for targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=max_length, padding=True, truncation=True)

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def ft_compute_metrics(eval_pred):
    """
    pasted as it is from chatgpt. Need to pick a metric deiberately
    """
    # metric = evaluate.load("rouge")
    metric = load_metric("rouge")
    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    # Replace -100 in the labels as we can't decode them
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Some simple post-processing
    decoded_preds = ["\n".join(pred.strip().split()) for pred in decoded_preds]
    decoded_labels = ["\n".join(label.strip().split()) for label in decoded_labels]

    result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
    result = {key: value.mid.fmeasure * 100 for key, value in result.items()}

    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in predictions]
    result["gen_len"] = np.mean(prediction_lens)
    return result


def ft_train(datasetdir="ztmp/bench/ag_news/ft_data.parquet", outputdir="ztmp/bench/ft_relex_model", nrows=-1):
    """
    Load a dataset from a parquet file, preprocess the data, tokenize it, and train a model using Seq2SeqTrainer.
    Args:
        datasetdir (str): The directory path to the dataset in parquet format.
        outputdir (str): The directory path to save the trained model.
        nrows (int): Number of rows to consider from the dataset. If -1, all rows are processed.
    Returns:
        None
    """

    # load dataset from parquet file
    df = pd_read_file(datasetdir)

    if nrows > 0:
        df = df.iloc[:nrows]
    dataset = Dataset.from_pandas(df)
    train_val_test = dataset.train_test_split(test_size=0.1)
    training_dataset = train_val_test["train"]
    test_val_dataset = train_val_test["test"].train_test_split(test_size=0.1)
    test_dataset = test_val_dataset["train"]
    validation_dataset = test_val_dataset["test"]
    dataset = DatasetDict(
        {
            "train": training_dataset,
            "test": test_dataset,
            "validation": validation_dataset
        }
    )

    tokenized_datasets = dataset.map(train_tokenize, batched=True, batch_size=None)

    # Define training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=outputdir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=3,
        predict_with_generate=True,
    )
    # Initialize the Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        compute_metrics=ft_compute_metrics,
    )

    # Train the model
    cc =Box({})
    cc.datasetdir = datasetdir
    cc.checkpoint =None
    trainer.train(resume_from_checkpoint= cc.checkpoint)
    trainer.save_model(outputdir )

    evals = trainer.evaluate()
    cc['trainer_eval']    = str(evals)

    from utilmy import json_save 
    json_save(cc, f"{outputdir}/meta.json")


    # Save the model
    #model.save_pretrained()
    #tokenizer.save_pretrained(outputdir)


if __name__ == '__main__':
    import fire

    fire.Fire()
