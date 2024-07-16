"""  

Docs:

        Multilabel strategies
        SetFit will initialise a multilabel classification head from sklearn - following options are available for multi_target_strategy:

        "one-vs-rest": uses a OneVsRestClassifier head.
        "multi-output": uses a MultiOutputClassifier head.
        "classifier-chain": uses a ClassifierChain head.
        See scikit-learn documentation for multiclass and multioutput classification for more details.

        Initializing SetFit models with multilabel strategies
        Using default LogisticRegression head, we can apply multi target strategies like so:

        Copied
        from setfit import SetFitModel

        model = SetFitModel.from_pretrained(
            model_id, # e.g. "BAAI/bge-small-en-v1.5"
            multi_target_strategy="multi-output",
        )
        With a differentiable head it looks like so:

        Copied
        from setfit import SetFitModel

        model = SetFitModel.from_pretrained(
            model_id, # e.g. "BAAI/bge-small-en-v1.5"
            multi_target_strategy="one-vs-rest"
            use_differentiable_head=True,
            head_params={"out_features": num_classes},
        )

        https://github.com/huggingface/setfit/blob/main/notebooks/text-classification_multilabel.ipynb
         
Docs:


git clone https://github.com/arita37/myutil.git
cd myutil
git checkout devtorch

git pull --all


#### Model to use Deberta V3 for multi label classifier
  
https://github.com/rohan-paul/LLM-FineTuning-Large-Language-Models/blob/main/Other-Language_Models_BERT_related/Deberta-v3-large-For_Kaggle_Competition_Feedback-Prize/deberta-v3-large-For_Kaggle_Competition_Feedback-Prize.ipynb

https://github.com/rohan-paul/LLM-FineTuning-Large-Language-Models/blob/main/Other-Language_Models_BERT_related/DeBERTa_Fine_Tuning-for_Amazon_Review_Dataset_Pytorch.ipynb



#### Gliner






### Working folder
cd utilmy/webapi/asearch/nlp/


### in your Local PC : store dataset big ffiles
   mkdir -p ztmp
  ztmp/data/... Big Files...

   "ztmp" is gitignore ---> Wont commit ok, in your local

   dirdata="ztmp/data/#

   utilmy/webapi/asearch/nlp/ztmp/  --> wont be committed.



### working files

    sentiment.py
    ner.py


#### Dataset :
   News dataset
        https://huggingface.co/datasets/ag_news




        https://zenn.dev/kun432/scraps/1356729a3608d6

        https://huggingface.co/datasets/big_patent


  NER and Classification on News Dataset.


##### Task
     https://huggingface.co/datasets/ag_news
   AgNews ---> Add new label columns Manually label2, label3
         put random category.
         Small dataset ---> code working.  100 samples is enough.
         

   1) Fine tuning for classification on newsDatast
       Use  Sentence Transformers  ( deberta V3  or)
        Add task Head to fine tune
       text --> category

     English only.
     Save model + fine tune part on disk

     Generate embedding for text.
          ( I have only in fine tuned embedding)

      Dataset
        id,
        text,



        label1,  Integer cat
        label2,  Integer cat
        label3,  Integer cat

          model.predict(text) --->  { "label1": "cat", "label2": "subcat", "label3": "subsubcat" }


     Mutil Label classifier Head Classifier :
        label1 :  cata, catb, catc
        label2 :  subcat1, subcat2, subcat3
        label3 :  subsubcat1, subsubcat2, subsubcat3



1) sentences transformers   : More customization for Loss.



2) setfit library : very fast fine tuning with only Classifier loss
  for LLM,
      Sentence Transformers is generally better for a wide range of tasks
      involving sentence embeddings and similarity measures due to its flexibility
      and extensive model support.

      SetFit, however, is optimized for simplicity and efficiency
      in fine-tuning text classification models on small datasets.
      Choose Sentence Transformers for versatility and broader applications, or SetFit for efficient text classification with limited data.

      Sentence Transformers: https://www.sbert.net/
      SetFit: https://huggingface.co/docs/setfit/index



pip install utilmy python-box fire


df =  pd_read_file("/**/myfile.parquet")

pd_to_file(df, "myfolder/myfile.parquet")


Do not spend time on accuracy
  jsut need code working.



https://colab.research.google.com/github/NielsRogge/Transformers-Tutorials/blob/master/BERT/Fine_tuning_BERT_(and_friends)_for_multi_label_text_classification.ipynb


"""


from datasets import load_dataset
from setfit import SetFitModel, Trainer, TrainingArguments, sample_dataset



def train():
    # Load a dataset from Hugging Face Hub
    dataset = load_dataset("sst2")

    # Simulate few-shot regime by sampling 8 examples per class
    train_dataset = sample_dataset(dataset["train"], label_column="label", num_samples=8)
    eval_dataset = dataset["validation"].select(range(100))
    test_dataset = dataset["validation"].select(range(100, len(dataset["validation"])))

    # Load a SetFit model from Hub
    model_id=         "sentence-transformers/paraphrase-mpnet-base-v2"

    model = SetFitModel.from_pretrained(
            model_id, # e.g. "BAAI/bge-small-en-v1.5"
            multi_target_strategy="one-vs-rest",
            use_differentiable_head=True,
            head_params={"out_features": num_classes},
        )

    model = SetFitModel.from_pretrained(

        labels=["negative", "positive"],
    )

    args = TrainingArguments(
        batch_size=16,
        num_epochs=4,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        metric="accuracy",
        column_mapping={"sentence": "text", "label": "label"}  # Map dataset columns to text/label expected by trainer
    )

    # Train and evaluate
    trainer.train()
    metrics = trainer.evaluate(test_dataset)
    print(metrics)
    # {'accuracy': 0.8691709844559585}

    ## Push model to Hub
    ## trainer.push_to_hub("tomaarsen/setfit-paraphrase-mpnet-base-v2-sst2")

    # Download from Hub
    model = SetFitModel.from_pretrained("tomaarsen/setfit-paraphrase-mpnet-base-v2-sst2")
    # Run inference
    preds = model.predict(["i loved spiderman movie!", "pineapple on pizza is worst 🤮"])
    print(preds)
    # ["positive", "negative"]

from datasets import Dataset
import pandas as pd

def pandas_to_hf_dataset(df: pd.DataFrame) -> Dataset:
    return Dataset.from_pandas(df)



from datasets import Dataset

def save_hf_dataset(dataset: Dataset, path: str):
    dataset.save_to_disk(path)

# Example usage:
# dataset = Dataset.from_dict({'column1': [1, 2], 'column2': ['a', 'b']})
# save_hf_dataset(dataset, "path/to/save/dataset")




from utilmy import pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob
from utilmy import log, log2


def test123(val=""):
   print("ok")




import torch
import torch.nn as nn
from transformers import BertModel
from sentence_transformers import SentenceTransformer

class MultiLabelMultiClassModel(nn.Module):
    def __init__(self, num_labels_list):
        super().__init__()
        self.bert = SentenceTransformer('bert-base-uncased').bert
        self.classification_heads = nn.ModuleList([
            nn.Linear(self.bert.config.hidden_size, num_labels) for num_labels in num_labels_list
        ])

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        logits = [head(pooled_output) for head in self.classification_heads]
        return logits

# Example usage:
model = MultiLabelMultiClassModel(num_labels_list=[3, 4])  # Assuming 3 classes for first label set, 4 for second
input_ids = torch.tensor([[101, 1024, 102]])  # Example input
attention_mask = torch.tensor([[1, 1, 1]])    # Example attention mask
logits = model(input_ids, attention_mask)





###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




