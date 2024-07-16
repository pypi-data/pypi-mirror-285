### multilable classification on toxicity dataset 
```
Commands/Steps run:
# 1. Download dataset files into "ztmp/data/cats/toxicity/raw" from https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data
pyclass data_toxic_create_norm
pyclass data_toxic_load_metadict
#  pyclass run_train  --dirout ztmp/exp --dirdata "ztmp/data/cats/toxicity"  --istest 0

###### User default Params   #######################################

###### Config Load   #############################################
Config: Using /home/ankush/workplace/fl_projects/myutil/utilmy/configs/myconfig/config.yaml
Config: Loading  /home/ankush/workplace/fl_projects/myutil/utilmy/configs/myconfig/config.yaml
Config: Cannot read file /home/ankush/workplace/fl_projects/myutil/utilmy/configs/myconfig/config.yaml 'str' object has no attribute 'suffix'
Config: Using default config
{'field1': 'test', 'field2': {'version': '1.0'}}
{'model_name': 'microsoft/deberta-v3-base', 'dataloader_name': 'data_DEFAULT_load_datasplit', 'datamapper_name': 'data_DEFAULT_load_metadict', 'n_train': 1000000000, 'n_val': 1000000000, 'hf_args_train': {'output_dir': 'ztmp/exp/log_train', 'per_device_train_batch_size': 16, 'gradient_accumulation_steps': 1, 'optim': 'adamw_hf', 'save_steps': 100, 'logging_steps': 50, 'learning_rate': 1e-05, 'max_grad_norm': 2, 'max_steps': -1, 'num_train_epochs': 1, 'warmup_ratio': 0.2, 'evaluation_strategy': 'epoch', 'logging_strategy': 'epoch', 'save_strategy': 'epoch'}, 'hf_args_model': {'model_name': 'microsoft/deberta-v3-base', 'problem_type': 'multi_label_classification'}, 'cfg': None, 'cfg_name': 'class_deberta'}

###### Experiment Folder   #########################################
ztmp/exp/20240615/075716-class_deberta-1000000000

###### Model : Training params ######################################

###### User Data Load   #############################################
        labels                                               text
0  0,1,1,1,0,1       COCKSUCKER BEFORE YOU PISS AROUND ON MY WORK
1  0,0,0,0,0,1  Hey... what is it..\n@ | talk .\nWhat is it...... /n ['labels', 'text'] /n (12980, 2)
        labels                                               text
0  0,1,1,0,0,1  DUDE. LATINUS. Don't you have a job or some sh...
1  0,1,1,0,0,1  Can any of you dumbasses read the entirely fir... /n ['labels', 'text'] /n (3245, 2)
(3245, 2)

###### Dataloader setup  #######################################
nlabel_total:  2
                                                   0
text    COCKSUCKER BEFORE YOU PISS AROUND ON MY WORK
labels                                    [1.0, 1.0]
Map: 100%|█████████████████████████████████████| 12980/12980 [00:00<00:00, 15394.78 examples/s]
Filter: 100%|██████████████████████████████████| 12980/12980 [00:01<00:00, 11624.08 examples/s]
Dataset({
    features: ['labels', 'input_ids', 'token_type_ids', 'attention_mask'],
    num_rows: 12980
})
nlabel_total:  2
                                                        0
text    DUDE. LATINUS. Don't you have a job or some sh...
labels                                         [1.0, 1.0]
Map: 100%|███████████████████████████████████████| 3245/3245 [00:00<00:00, 17695.09 examples/s]
Dataset({
    features: ['labels', 'input_ids', 'token_type_ids', 'attention_mask'],
    num_rows: 3245
})
{'labels': tensor([[1., 1.],
        [1., 1.]]), 'input_ids': tensor([[     1,   3978,  73113, 114172,  23431,   3773,    916,  33612,  66216,
           5067,   8862,  24100,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2],
        [     1,   5388,    260,    260,    260,    339,    269,    278,    260,
            260,   1944,   1540,   1072,    323,    458,    269,    278,    260,
            260,    260,    299,   3229,    596,    265,    347,  12671,  18008,
          74628,  43352,    260,    260,    260,   5710,    281,    397,    288,
          12086,    261,    934,    271,  28043,  77522,    328,   1098,  29606,
           9146,    356,    311,    328,   5387,    349,    841,  74873,    308,
          54712,    271,  46051,  33117,    263,   8936,  81599,  27444,    287,
           7731,    285,    271, 105752,    288,  12671,    302,   5606,    662,
           3376,  24666,    264,   1347,    322,    315,   2565,    354,    889,
            351,  47288,  11917,    260,    260,    260,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2,      2,      2,      2,      2,      2,      2,      2,
              2,      2]]), 'token_type_ids': tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0]]), 'attention_mask': tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0]])}

######### Model : Init #########################################
Some weights of DebertaV2ForSequenceClassification were not initialized from the model checkpoint at microsoft/deberta-v3-base and are newly initialized: ['classifier.bias', 'classifier.weight', 'pooler.dense.bias', 'pooler.dense.weight']
You should probably TRAIN this model on a down-stream task to be able to use it for predictions and inference.

######### Model : Training start ##############################
{'loss': 0.0717, 'grad_norm': 0.049192365258932114, 'learning_rate': 0.0, 'epoch': 1.0}        
{'eval_loss': 0.006116325035691261, 'eval_accuracy': 0.9984591679506933, 'eval_precision': 0.9992301779738236, 'eval_recall': 1.0, 'eval_f1': 0.9996147922166627, 'eval_runtime': 30.5047, 'eval_samples_per_second': 106.377, 'eval_steps_per_second': 13.309, 'epoch': 1.0}
{'train_runtime': 366.5817, 'train_samples_per_second': 35.408, 'train_steps_per_second': 2.215, 'train_loss': 0.07173129020653335, 'epoch': 1.0}                                             
100%|████████████████████████████████████████████████████████| 812/812 [06:06<00:00,  2.22it/s]
{'model_name': 'microsoft/deberta-v3-base', 'dataloader_name': 'data_DEFAULT_load_datasplit', 'datam

######### Model : Eval Predict  ######################################
100%|████████████████████████████████████████████████████████| 406/406 [00:31<00:00, 13.08it/s]

pred_proba:  [[6.6470704 7.232303 ]
 [6.661514  7.233134 ]
 [6.
labels:  [[1. 1.]
 [1. 1.]
 [1. 1.]
 ...
 [1. 1.]
 [1. 1.]

pred_class:  [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [ 


ztmp/exp/20240615/075716-class_deberta-1000000000/dfval_pred_labels.parquet
          labels  ... pred_labels
0     [1.0, 1.0]  ...      [1, 1]
1     [1.0, 1.0]  ...      [1, 1]
2     [1.0, 1.0]  ...      [1, 1]
3     [1.0, 1.0]  ...      [1, 1]
4     [1.0, 1.0]  ...      [1, 1]
...          ...  ...         ...
3240  [1.0, 1.0]  ...      [1, 1]
3241  [1.0, 1.0]  ...      [1, 1]
3242  [1.0, 1.0]  ...      [1, 1]
3243  [1.0, 1.0]  ...      [1, 1]
3244  [1.0, 1.0]  ...      [1, 1]

[3245 rows x 4 columns]

######### Model : Eval Metrics #######################################
ztmp/exp/20240615/075716-class_deberta-1000000000/dfval_pred_metrics.csv
          labels  ... pred_labels
0     [1.0, 1.0]  ...      [1, 1]
1     [1.0, 1.0]  ...      [1, 1]
2     [1.0, 1.0]  ...      [1, 1]
3     [1.0, 1.0]  ...      [1, 1]
4     [1.0, 1.0]  ...      [1, 1]
...          ...  ...         ...
3240  [1.0, 1.0]  ...      [1, 1]
3241  [1.0, 1.0]  ...      [1, 1]
3242  [1.0, 1.0]  ...      [1, 1]
3243  [1.0, 1.0]  ...      [1, 1]
3244  [1.0, 1.0]  ...      [1, 1]

[3245 rows x 4 columns]
```