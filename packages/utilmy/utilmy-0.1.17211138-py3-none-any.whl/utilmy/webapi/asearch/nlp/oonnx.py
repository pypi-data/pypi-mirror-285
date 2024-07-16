# -*- coding: utf-8 -*-
"""export_model_to_onnx.ipynb
Docs:

    ### INSTALL
        pip install -q -U bitsandbytes peft accelerate  transformers==4.37.2
        pip install datasets fastembed simsimd transformers==4.37.2  utilmy  onnxruntime
        pip install -q seqeval


    #### export
        alias pyonnx="python nlp/oonnx.py "
        export dexp="./ztmp/exp/240616/130347-ner_deberta-5000"
               
        pyonnx export_onnx --dirmodel $dexp/model --dirout $dexp/model/export_onnx
    

    #### Tests 
        export dexp="./ztmp/exp/240616/130347-ner_deberta-5000"

        pyonnx test_onnx_runtime --dironnx $dexp/model/export_onnx/  --query_str 'On specific query by Bench abouton deposit side of Hongkong Bank account'

        pyonnx test_onnx_create --dirmodel /home/tuenv2/export_onnx/ 


"""
if "import":
    import warnings; warnings.filterwarnings("ignore")
    # If issue dataset: please restart session and run cell again
    from transformers import (
        AutoModelForTokenClassification, TrainingArguments, Trainer,
        AutoTokenizer,
    )
    import os, torch, numpy as np
    from dataclasses import dataclass
    import onnxruntime

    from utilmy import json_load, json_save, log, log2, log_error



###################################################################################################
def test_onnx_runtime(dironnx: str="./ztmp/export_onnx", query_str: str='find restaurant neraby US'):
    tokenizer       = AutoTokenizer.from_pretrained(dironnx)
    id2label        = json_load( dironnx + "/classes_index.json")
    dirmodel_onnx   = dironnx + '/model.onnx' 
    assert os.path.isfile(dirmodel_onnx), f'dirmodel_onnx: {dirmodel_onnx} not exits'


    ort_session = onnxruntime.InferenceSession(dirmodel_onnx, 
                    providers=["CPUExecutionProvider"])

    def to_numpy(tensor):
        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


    ##### compute ONNX Runtime output prediction
    query = tokenizer_query(query_str, tokenizer)
    x     = torch.tensor(query['input_ids']).long().reshape([ 1, -1])

    ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(x)}
    ort_outs   = ort_session.run(None, ort_inputs)[0]

    log(ort_outs)
    log(id2label)
    query['query'] = query_str
    value_pre_dict = pred2span(ort_outs[0], query, id2label['id2label'])
    log(value_pre_dict)


def test_onnx_create(dirmodel: str='ztmp/hf_pretrained/ner_model'):
    model = AutoModelForTokenClassification.from_pretrained(dirmodel)
    log(model)



###################################################################################################
@dataclass
class Wrapper:
  ner_softmax="ner_softmax"
  class_sigmoid="class_sigmoid"


class onnxModel_Softmax(torch.nn.Module):
    def __init__(self, super_model):
        super().__init__()
        self.model = super_model

    def forward(self, x):
        output = self.model(x).logits
        return torch.argmax(output, -1)



class onnxModel_Sigmoid(torch.nn.Module):
    def __init__(self, super_model):
        super().__init__()
        self.model = super_model

    def forward(self, x):
        output = self.model(x).logits
        return torch.argmax(output, -1)



###################################################################################################
def export_onnx(dirmodel: str=None,  dirout:str=None, 
                query_0='find restaurant around US',
                model_wrapper="ner_softmax", device="cpu"):
    """ 

         python nlp/oonnx.py  export_onnx  --dirmodel "./ztmp/mypretrained/"  --dirout "ztmp/out/onnx/deberta/"

    """
    dirmodel = 'tuenguyen/token_classification_model'if dirmodel is None else dirmodel
    # drive/checkpoint-314
    os.makedirs(dirout, exist_ok=True)


    log("######## model Load  #########################################")
    if model_wrapper ==  Wrapper.ner_softmax:     
        model     = AutoModelForTokenClassification.from_pretrained(dirmodel)
        tokenizer = AutoTokenizer.from_pretrained(dirmodel)        
        model_class_export = onnxModel_Softmax(model)

    else:
        model     = AutoModelForTokenClassification.from_pretrained(dirmodel)
        tokenizer = AutoTokenizer.from_pretrained(dirmodel)
                
        from utilmy import load_function_uri
        onnxModel_Class = load_function_uri(model_wrapper) ## "onnxModel_Sigmoid"
        model_class_export = onnxModel_Class(model)
                


    log("######## model Input Check  #########################################")        
    o = tokenizer_query(query_0, tokenizer)
    X = torch.tensor(o['input_ids']).long().reshape([ 1, -1]).to(device)
    torch_out = model_class_export(X)


    log("######## model Export  #########################################")
    torch.onnx.export( model_class_export,               # model being run
                    x,                         # model input (or a tuple for multiple inputs)
                    f'{dirout}/model.onnx',   # where to save model (can be a file or file-like object)
                    export_params=True,        # store trained parameter weights inside model file
                    opset_version=15,          # ONNX version to export model to
                    do_constant_folding=True,  # whether to execute constant folding for optimization
                    input_names = ['input'],   # model's input names
                    output_names = ['output'], # model's output names
                    dynamic_axes={'input' : {0 : 'batch_size', 1:'seq_len'},    # variable length axes
                                    'output' : {0 : 'batch_size', 1:'seq_len'}})


    tokenizer.save_pretrained(dirout)
    json_save( {'id2label': model.config.id2label}     , dirout + "/classes_index.json")

    log("######## ONNX Runtime Reload-Check #########################################")
    ort_session = onnxruntime.InferenceSession(f'{dirout}/model.onnx', 
                               providers=["CPUExecutionProvider"])

    def to_numpy(tensor):
        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


    log("######## ONNX output prediction ############################################")
    ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(x)}
    ort_outs   = ort_session.run(None, ort_inputs)

    # compare ONNX Runtime and PyTorch results
    np.testing.assert_allclose(to_numpy(torch_out), ort_outs[0], rtol=1e-03, atol=1e-05)
    log("Exported model has been tested with ONNXRuntime, and result looks good!")
    log( ort_outs[0])










###################################################################################################
def tokenizer_query(query, tokenizer):
        o = tokenizer(query,
                        return_offsets_mapping=True,
                        return_overflowing_tokens=True)
        offset_mapping = o["offset_mapping"]
        o['input_ids'] = o['input_ids'][0]
        o['attention_mask'] = o['attention_mask'][0]
        return o



def pred2span(pred, example, id2label):
        
        NCLASS = len(id2label)
        pred_list = pred.tolist()
        n_tokens = len(example['input_ids'])
        classes = []
        all_span = []
        for i, c in enumerate(pred.tolist()):
            if i == n_tokens-1:
                break
            if i == 0:
                cur_span = list(example['offset_mapping'][0][i])
                classes.append(id2label[str(c)])
            elif i > 0 and (c == pred[i-1] or c-NCLASS == pred_list[i-1]):
                # We will go to next-token for current span: B-, I-, I-, I- 
                # Note: index_of_inside_word - NCLASS ===  index_of_begin_word 
                cur_span[1] = example['offset_mapping'][0][i][1]
            else:
                all_span.append(cur_span)
                cur_span = list(example['offset_mapping'][0][i])
                classes.append(id2label[str(c)])

        all_span.append(cur_span)

        text = example['query']
        predstrings = []
        for span in all_span:
            span_start = span[0]
            span_end = span[1]
            before = text[:span_start]
            token_start = len(before.split())
            if len(before) == 0: token_start = 0
            elif before[-1] != ' ': token_start -= 1
            num_tkns = len(text[span_start:span_end+1].split())
            tkns = [str(x) for x in range(token_start, token_start+num_tkns)]
            predstring = ' '.join(tkns)
            predstrings.append(predstring)

        row = {
            'query': text,
            'entity_tag': []
        }
        es = []
        for c, span, predstring in zip(classes, all_span, predstrings):
            if c!='Other':
                e = {
                    'type': c,
                    'predictionstring': predstring,
                    'start': span[0],
                    'end': span[1],
                    'text': text[span[0]:span[1]]
                }
                es.append(e)
        row['entity_tag'] = es


        return row



###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()



""" 


# export
python3 nlp/oonnx.py export_onnx --dirmodel tuenguyen/token_classification_model --dirout /home/tuenv2/export_onnx
# tuenguyen/token_classification_model : path of model after training: i.e log_training/checkpoint-314


# run test
python3 nlp/oonnx.py test_onnx --dirmodel_onnx /home/tuenv2/export_onnx/ --query_str 'find restaurant neraby US'
{'id2label': {'0': 'LABEL_0', '1': 'LABEL_1', '2': 'LABEL_2', '3': 'LABEL_3', '4': 'LABEL_4', '5': 'LABEL_5', '6': 'LABEL_6', '7': 'LABEL_7', '8': 'LABEL_8', '9': 'LABEL_9', '10': 'LABEL_10'}}
{'query': 'find restaurant neraby US', 'entity_tag': [{'type': 'LABEL_10', 'predictionstring': '0', 'start': 0, 'end': 4, 'text': 'find'}, {'type': 'LABEL_3', 'predictionstring': '1', 'start': 5, 'end': 15, 'text': 'restaurant'}, {'type': 'LABEL_8', 'predictionstring': '2', 'start': 16, 'end': 22, 'text': 'neraby'}, {'type': 'LABEL_2', 'predictionstring': '3', 'start': 23, 'end': 25, 'text': 'US'}]}


"""





    #     from tqdm import tqdm


#     predicts = []
#     for index, row in tqdm(df_test.iterrows()):
#     query = row.query
#     o = tokenizer_query(query)
#     o['query'] = query
#     x = torch.tensor(o['input_ids']).long().reshape([ 1, -1])
#     ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(x)}
#     ort_outs = ort_session.run(None, ort_inputs)
#     pred = ort_outs[0] # bs, seq_length
#     value_pre_dict = pred2span(pred[0], o)
#     predicts.append(value_pre_dict['entity_tag'])

#     df_test['predict_raw_tag'] = predicts



#     df_test

#     predicts[0]

#     def acc_metric(tags, preds):
#     tags = sorted(tags, key=lambda x:x['start'])
#     preds = sorted(preds, key=lambda x:x['start'])
#     acc = {}
#     acc_count = {}
#     for tag in tags:
#         value = tag['value']
#         tag_type = tag['type']
#         if tag_type not in acc:
#         acc[tag_type] = 0
#         acc_count[tag_type] = 0
#         acc_count[tag_type] += 1
#         for p in preds:
#         if p['type'] == tag_type and p['text'].strip() == value.strip():

#             acc[tag_type]+= 1
#     total_acc = sum(acc.values()) / sum(acc_count.values())
#     acc = {
#         k: v/acc_count[k] for k, v in acc.items()
#     }
#     acc['total_acc'] = total_acc
#     return acc

#     # acc_metric(df_test.entity_tag.iloc[0], predicts[0])
#     df_test['acc'] = df_test.apply(
#         lambda x: acc_metric(
#             x['entity_tag'],
#             x['predict_raw_tag']
#         ),
#         axis=1
#     )

#     df_test[(df_test['acc'].apply(lambda x:x['total_acc']<=0.8)) & (df_test['acc'].apply(lambda x:x['total_acc']>=0.6))][['predict_raw_tag', 'entity_tag', 'acc']].sample(1).to_dict()

#     df_test

