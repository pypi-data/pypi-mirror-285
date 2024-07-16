

#### NER Task ###############################################
#### Code for NER Classification using Transformer #################################
from datasets import load_dataset, Dataset
from datasets import Dataset, load_metric
# If issue dataset: please restart session and run cell again
from transformers import ( AutoModelForCausalLM, PhiForCausalLM,
   AutoTokenizer, BitsAndBytesConfig, HfArgumentParser, AutoTokenizer,
   TrainingArguments, Trainer, GenerationConfig, AutoModelForSeq2SeqLM)


from transformers.tokenization_utils_base import PreTrainedTokenizerBase, PaddingStrategy
from transformers import AutoModelForMultipleChoice, TrainingArguments, Trainer
from dataclasses import dataclass
from seqeval.metrics import f1_score, precision_score, recall_score, classification_report

#### Dataset setup + transformation Class
dataset = Dataset.from_pandas(df)
dataset = dataset.map(tokenize_and_align_labels)


valid  =  Dataset.from_pandas(df_test)
valid   = valid.map(tokenize_and_align_labels)




from transformers import DataCollatorForTokenClassification
@dataclass
class DataCollatorForLLM:
   ### Data Collator : Padding and organize the multiple labels.
   ###  NER location of label ???
   ###  Label alignment for NER: 
           B
                   country     city             
          capital of US is Washihgton. 
   tokenizer:   PreTrainedTokenizerBase
   padding:     Union[bool, str, PaddingStrategy] = True
   max_length:  Optional[int] = None
   pad_to_multiple_of: Optional[int] = None




   def __call__(self, features):
       #### Labels: list of list (one per label) 
       label_name        = 'label' if 'label' in features[0].keys() else 'labels'
       labels            = [feature.pop(label_name) for feature in features]
       max_length_labels = max([len(i) for i in labels])
       labels_pad        = np.zeros((len(labels), max_length_labels, )) + -100 ## Default -100 
       for index in range(len(labels)):
           labels_pad[index, : len(labels[index])] = labels[index]




       #### How do you reconcile the position of label and the position of sentence token ?
       ### Tokenizer Class which manage this:  Alignment between Sentence Token, Label.
       batch_size         = len(features)
       flattened_features = features
       batch              = self.tokenizer.pad(
           flattened_features,
           padding    = self.padding,
           max_length = self.max_length,    #### Longer than max_length -->Error.
           pad_to_multiple_of= self.pad_to_multiple_of,
           return_tensors    = 'pt',
       )
       batch['labels'] = torch.from_numpy(labels_pad).long()


       return batch


##### 
columns = df.columns.tolist()
dataset_train = dataset.remove_columns(['overflow_to_sample_mapping', 'offset_mapping', ] + columns)
dataset_valid = valid.remove_columns(['overflow_to_sample_mapping', 'offset_mapping',]+columns)


batch = DataCollatorForLLM(tokenizer)([dataset_train[0], dataset_train[1]])




######
Fine Tuning: 2-3 hours for 50K dataset ?    Epoch: 5-10 
    --> Reduce LRate = 1E-4, 1E-5  : 
    --> Exponential Scheduler for LR ? (for fine tuning is OK).
    --> Early stopping:  Val loss, Val metrics  (F1 score ) ?
                         Val_loss > Val_prev{[:10 batch] or Moving Average.

          No fine tuning :    75 % F1 score on NER
        With Fine tuning :    85%  F1 SCORE ON NER (depend on dataset)




https://towardsdatascience.com/make-the-most-of-your-small-ner-data-set-by-fine-tuning-bert-98a2c8b544f


###### Embedding  of of the sentence: 
   --Classification using only the embedding  

    2 Layer MLP  --->  Input the vector embedding
          --> Classifier at end


Vector is compute separately (store in database)
   _--> retrain the 2 layer MLP when vector system changes.
Cheap way to do classication


sentence          labels : EntityName separated by space. (Special token for ) 
my name is  CXYXT,    “B ITer ET SpecialNoLabel ”

-----------------------------------------------------------------------------------






chunk_tags : Syntax chunk : Type of sentence NPhrase, VerbPrhase,  


POS_TAG: Noun, verb, individual word


NER_TAG: name entity.


all use  using the IOB (Inside, Outside, Beginning) tagging format.




#### NER Classfication
    Multiple Label : Chunk, POS NER, Multiple class per Label
    per token position.




India -> ind ia
         B-Ci I-ci   NER are also splitted into token parts: Start_city, mid_city, end_city


NER_token_ID --> in a separate adictionnary.


Do you do to build NER (aleasy some pre-dfined) ?




In my case, I need to the NER manually (by programming)
   LList of capital, country
       synthetic sentence   " the capital of {country} is {city} "       labels = {    {}


NER_Tags --> Class label per  word
               sub-word1 --> Label : start_city
               sub-word2 --> Label : end_city
               .... 


India :   Pre-trained did you use ? English BERT for english NER
    TRANSFO Collator Class --> batch sentence, 


 Indi language : no words separation,  token  --> subword
   


https://huggingface.co/datasets/conll2003




sentence_transformers --> Embedding of sentence.




########################################################################
#######################################################################
Here are someme -> https://huggingface.co/docs/transformers/main_classes/model#transformers.modeling_utils.ModuleUtilsMixin

Check this out -> https://huggingface.co/transformers/v3.0.2/model_doc/auto.html

AutoConfig
AutoTokenizer
AutoModel
AutoModelForPreTraining


AutoModelWithLMHead        --> OK
AutoModelForSequenceClassification   ---> Full Sentence

AutoModelForTokenClassification    --> NER  Token Level
AutoModelForQuestionAnswering



############################################################################ 
from transformers import AutoModelForTokenClassification, TrainingArguments, Trainer
# from transformers.models.qwen2.modeling_qwen2 import
model = AutoModelForTokenClassification.from_pretrained(model_name, 
         num_labels= NCLASS*2 + 1)  #### label column ?  POS, NER, CHUNK


### NER
metric = load_metric("seqeval")


def compute_metrics(p):
   predictions, labels = p
   predictions = np.argmax(predictions, axis=2)

   # Remove ignored index (special tokens)
   true_predictions = [
      [i2l[p] for (p, l) in zip(prediction, label) if l != -100]
       for prediction, label in zip(predictions, labels)  ]   
   
   true_labels = [
       [i2l[l] for (p, l) in zip(prediction, label) if l != -100]
       for prediction, label in zip(predictions, labels) ]


   results = metric.compute(predictions=true_predictions, references=true_labels)
   return {
       "precision": results["overall_precision"],
       "recall": results["overall_recall"],
       "f1": results["overall_f1"],
       "accuracy": results["overall_accuracy"],
   }


dataset_valid[0]
# for i in model.deberta.parameters():
#   i.requires_grad=False




https://www.kaggle.com/code/kelde9/sentences-embedding-visualization-how-to-do-it
Use Snetence transformer --> Visualization for embe


Only huggingFace library
https://huggingface.co/sentence-transformers




DeepSpeed


#### More pred-defined Losses per Task
https://www.sbert.net/docs/package_reference/losses.html

--> For Fine Tuning, with specific task
No Token level in sentence Level.









