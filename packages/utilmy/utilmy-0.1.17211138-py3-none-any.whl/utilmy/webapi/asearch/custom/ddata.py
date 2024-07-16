# -*- coding: utf-8 -*-
""" dataloader definition 

   ### Install
     pip install --upgrade utilmy fire python-box
     pip install datasets fastembed simsimd seqeval


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



### Usage Legal Doc dataset
    cd asearch     
    export pyner="python nlp/ner/ner_deberta.py "
    export dirdata="./ztmp/data/ner/legaldoc"

    pyner data_legalDoc_json_to_parquet  --dir_json $dirdata/raw/NER_VAL.json     --dirout  $dirdata/val/df_val.parquet
    pyner data_legalDoc_json_to_parquet  --dir_json $dirdata/raw/NER_TRAIN.json   --dirout  $dirdata/train/df_train.parquet

    pyner data_legalDoc_create_metadict  --dirin $dirdata     --dir_meta  $dirdata/meta/meta.json


    pyner run_train --dirout ./ztmp/exp/deberta_legal_doc --cfg config/train.yml --cfg_name model_deverta_legal_doc



"""

if "Import":
    import json,re, os, pandas as pd, numpy as np,copy
    from dataclasses import dataclass
    from typing import Optional, Union
    from box import Box
    import datasets 
    from datasets import Dataset, load_metric

    import spacy, torch
    from utilmy import (date_now, date_now, pd_to_file, log,log2, log_error, pd_read_file, json_save, 
                        config_load, pprint, pd_read_file, glob_glob)


    ### PTYHONPATH="$(pwd)"
    from utils.util_exp import (exp_create_exp_folder, exp_config_override, exp_get_filelist, log_pd)    


    #### cd search ; export PYTHONPATH="$(pwd):$PYTHONPATH"
    from nlp.ner.ner_deberta import nerdata_validate_dataframe, NERdata





######################################################################################################
################## Custom Data : Legal Data ##########################################################
""" 
    cd asearch 
    export PYTHONPATH="$(pwd)"
    
    alias pyner="python nlp/ner/ner_deberta.py "
    export dirdata="./ztmp/data/ner/legaldoc"

    #### Legal Doc dataset Prep 
       pyner data_legalDoc_json_to_parquet  --dir_json $dirdata/raw/NER_VAL.json     --dirout  $dirdata/val/df_val.parquet
       pyner data_legalDoc_json_to_parquet  --dir_json $dirdata/raw/NER_TRAIN.json   --dirout  $dirdata/train/df_train.parquet

       pyner data_legalDoc_create_metadict  --dirin $dirdata     --dir_meta  $dirdata/meta/meta.json

    ### Train
       pyner run_train --dirout ./ztmp/exp/ --cfg config/train.yml --cfg_name ner_deberta_legaldoc




"""
def data_legalDoc_convert_to_gliner_format(cfg=None, dirin=r"ztmp/data/ner/legaldoc/raw/", dirout=r""):
  """ Convert data to GLINER
        Input : csv or parquet file

        #### evaluation only support fix entity types (but can be easily extended)
        data  = json_load(dirdata)
        eval_data = {
            "entity_types": ['court', 'petitioner', 'respondent', 'judge', 'lawyer', 'date', 'organization', 'geopolitical entity', 'statute', 'provision', 'precedent', 'case_number', 'witness', 'OTHER_PERSON'],
            "samples": data[:10]
        }


        Target Frormat
        [
        {
            "tokenized_text": ["State", "University", "of", "New", "York", "Press", ",", "1997", "."],
            "ner": [ [ 0, 5, "Publisher" ] ]
        }
        ],
  
  """
  def find_indices_in_list(text, start_pos, end_pos):
        words = text.split(" ")
        cumulative_length = 0
        start_index = None
        end_index = None

        for i, word in enumerate(words):
            word_length = len(word) + 1  # Add 1 for space character
            cumulative_length += word_length

            if start_index is None and cumulative_length > start_pos:
                start_index = i

            if cumulative_length > end_pos:
                end_index = i
                break

        return start_index, end_index

  def convert_to_target(data):     
        lowercase_values = {
        'COURT'       : 'court',
        'PETITIONER'  : 'petitioner',
        'RESPONDENT'  : 'respondent',
        'JUDGE'       : 'judge',
        'LAWYER'      : 'lawyer',
        'DATE'        : 'date',
        'ORG'         : 'organization',
        'GPE'         : 'geopolitical entity',
        'STATUTE'     : 'statute',
        'PROVISION'   : 'provision',
        'PRECEDENT'   : 'precedent',
        'CASE_NUMBER' : 'case_number',
        'WITNESS'     : 'witness',
        'OTHER_PERSON': 'OTHER_PERSON'
        }

        targeted_format = []

        for value in data:
            tokenized_text = value['data']['text'].split(" ")      
            ner_tags = []

            for results in value["annotations"][0]['result']:
                ner_list = []
                start, end = find_indices_in_list(value['data']['text'], results['value']['start'],results['value']['end'])
                
                ner_list.append(start)
                ner_list.append(end)
                
                for label in results['value']['labels']:
                    ner_tags.append(ner_list + [lowercase_values[label]])

            targeted_format.append({"tokenized_text" : tokenized_text, "ner":ner_tags})

        return targeted_format

  with open(dirin,'r') as f:
      data = json.load(f)

  data = convert_to_target(data)

  #df["tokenized_text"] = df["text"].apply(lambda x: x.split())
  # 
  #   data= df[[ "tokenized_text", "ner"]].to_json(dirout, orient="records")
  log(str(data)[:100])
  json_save(data, dirout)



def data_legalDoc_json_to_parquet(dir_json, dirout):
    """  LegalDoc to parquet : need to call it 2 times 1 for train, 1 for val
    
       rawJSON --> parquer format ( text, ner_list )
    
    """
    from utilmy import json_load, os_makedirs, pd_to_file
    data = json_load(dir_json)

    ######### Converter ####################################
    datasets = []
    for sample in data:
        annotations = sample['annotations']
        text        = sample['data']['text']
        
        text = text.replace("\n","*")
        #### Convert to parquer format
        row = dict(text=text, ner_list=[])
        for annotation in annotations:
            for ddict in annotation['result']:
                row['ner_list'].append(
                    {
                         'start': ddict['value']['start'], 
                         'end'   : ddict['value']['end'], 
                         'class'  : ddict['value']['labels'][0], 
                         "value" : ddict['value']['text']
                    }
                )
        datasets.append(row)

    data_df= pd.DataFrame(datasets)
    pd_to_file(data_df, dirout, show=1)

    log("#######  Extract NER Tag  ##########################")    
    tag_list = []
    for index, row in data_df.iterrows():
        for tag in row['ner_list']:
            type_of_tag = tag["class"]
            if type_of_tag not in tag_list:
                tag_list.append(type_of_tag)
    tag_list = sorted(tag_list)
    log("tag_list", tag_list)


def data_legalDoc_create_metadict(dirin, dir_meta):
    """ 
    """
    log("#### Create meta_dict ###############################")
    nertag_list = [
        'COURT'      , 'PETITIONER' , 'RESPONDENT' , 'JUDGE'      , 'LAWYER'     , 'DATE'       , 'ORG'        , 'GPE'        , 'STATUTE'    , 
        'PROVISION'  , 'PRECEDENT'  , 'CASE_NUMBER', 'WITNESS'    , 'OTHER_PERSON'
    ]

    nerlabelEngine = NERdata(nertag_list=nertag_list,)
    log("init done")
    nerlabelEngine.metadict_init()
    log("metadict_init")
    nerlabelEngine.metadict_save(dir_meta)


############################################################################################
def data_legalDoc_load_metadict(dirmeta="./ztmp/data/ner/legaldoc/meta/meta.json"):
    nerlabelEngine = NERdata(dirmeta=dirmeta)
    I2L, L2I, NLABEL_TOTAL, meta_dict =  nerlabelEngine.metadict_load(dirmeta=dirmeta)
    return nerlabelEngine, meta_dict 

####  training loader functions  ####################################
def data_legalDoc_load_datasplit(dirin="./ztmp/data/ner/legaldoc"):
    """ Data Loader for training. """ 
    flist = glob_glob(dirin + "/train/*.parquet", verbose=1)
    log("flist: ",flist)
    df = pd_read_file(flist, )
    log(df)
    assert df[[ "text", "ner_list"  ]].shape, f'{df.columns}'
    assert len(df)>1     and df.shape[1]>= 2 


    df_val = pd_read_file(dirin + "/val", )
    log(df_val)
    assert df_val[[ "text", "ner_list"  ]].shape
    assert len(df_val)>1 and df.shape[1]>= 2

    nerdata_validate_dataframe(df, df_val)
    return df, df_val






#########################################################################################
####### Custom dataset : NERGeo data ####################################################
######### Create Split Data, meta.json
if "create normalized NERGEO":
    def data_NERgeo_create_datasplit():
        """ 
        python nlp/ner/ner_deberta.py data_NERgeo_create_datasplit

        Sample data:

                query	answer	answerfull	answer_fmt
            0	find kindergarten and tech startup in Crack...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Cracker Barrel Old Cou...
            1	This afternoon, I have an appointment to Mitsu...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Mitsuwa Marketplace',c...
            2	find train and embassy near by Brooklyn Bri...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Brooklyn Bridge Park S...
            3	This afternoon, I have an appointment to Nowhe...	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Nowhere',city='New Yor...
            4	This afternoon, I have an appointment to Wawa....	b'{"name":"search_places","args":{"place_name"...	b'{"name":"search_places","args":{"place_name"...	search_places(location='Wawa',country='US',loc...


        """
        dirout0='./ztmp/out/ner_geo'
        dt = date_now(fmt="%Y%m%d_%H%M%S")
        dirout= os.path.join(dirout0, dt)
        os.makedirs(dirout)


        ##### Load Data #################################################
        #cd ./ztmp/
        #git clone https://github.com/arita37/data2.git   data
        #cd data
        #git checkout text
        dirtrain = "./ztmp/data/ner/ner_geo/df_10000_1521.parquet"
        dirtest  = "./ztmp/data/ner/ner_geo/df_1000.parquet"
        dirout   = "./ztmp/data/ner/ner_geo/"

        df        = pd_read_file(dirtrain)#.sample(2000)
        log(df)
        df_test   = pd_read_file(dirtest)#.head(100)
        log(df_test)

        cols0 = [ "query",	"answer",	"answerfull",	"answer_fmt"]
        assert df[cols0].shape
        assert df_test[cols0].shape

        colsmap= {"query": "text",}
        df      = df.rename(columns= colsmap)
        df_test = df.rename(columns= colsmap)


        #### Data Enhancement ##########################################
        ex= []
        for i in range(200):
            r = df.sample(1).iloc[0].to_dict()
            query = r["text"]
            s = np.random.randint(len(query))
            if np.random.random()>0.5:
                query = query + f', around {s}km. '
            else:
                query = f'around {s} km. ' + query
            r["text"] = query
            ex.append(r)

        # query = query + ", around 8km."
        df  = pd.concat([df, pd.DataFrame(ex)])

        df["ner_list"]      = df.apply(data_NERgeo_fun_prepro_text_predict,      axis=1)
        df_test["ner_list"] = df_test.apply(data_NERgeo_fun_prepro_text_predict, axis=1)
        log( df.head() )
        log( df_test.sample(1).to_dict())


        assert df[["text", "ner_list" ]].shape    
        assert df_test[["text", "ner_list" ]].shape    

    ###### External validation ##################################### 
        nerdata_validate_dataframe(df)
        nerdata_validate_dataframe(df_test)

        pd_to_file(df,      dirout + "/train/df_train.parquet", show=1)
        pd_to_file(df_test, dirout + "/val/df_val.parquet", show=1)


    def data_NERgeo_create_label_metadict(dirdata:str="./ztmp/data/ner/ner_geo/"):
        """ 
        python nlp/ner/ner_deberta_v3.py data_NERgeo_create_label_metadict
        """

        log("############# Create Label Mapper")
        # dirdata = dirin.split("raw")[0]    
        nertag_list = ['location', 'city', 'country', 'location_type', 'location_type_exclude']
        nerlabelEngine = NERdata(nertag_list=nertag_list,)
        
        nerlabelEngine.metadict_init()
        nerlabelEngine.metadict_save(dirdata + "/meta/meta.json")



    ########## Custom dataset NERgeo
    def data_NERgeo_predict_generate_text_fromtags(dfpred, dirout="./ztmp/metrics/"):
        """  Generate text from TAGS

        """
        if isinstance(dfpred, str):
           dfpred= pd_read_file(dfpred)
        assert dfpred[[ "ner_list", "pred_ner_list"  ]].shape


        def create_answer_from_tag(tag):
            # name=f'location={}'
            tag=sorted(tag, key=lambda x:x['start'])
            final_answer = ""
            list_location_type = []
            list_location_exclude = []
            for t in tag:
                text  =t.get('text') if 'text' in t else t.get("value")

                if t["class"]not in ['location_type', 'location_type_exclude']:
                   key = t["class"]
                   final_answer += f'{key}={text}\n'

                elif t["class"] == 'location_type':
                   list_location_type.append(text)

                elif t["class"] == 'location_type_exclude':
                   list_location_exclude.append(text)

            if len(list_location_type):
                text = " and ".join(list_location_type)
                final_answer += f'location_type={text}\n'

            if len(list_location_exclude):
                text = " and ".join(list_location_exclude)
                final_answer += f'list_location_exclude={text}\n'
            return final_answer

        #####  Generate nornalized answer from tag
        dfpred['text_true_str'] = dfpred["ner_list"].apply(create_answer_from_tag)
        dfpred['text_pred_str'] = dfpred["pred_ner_list"].apply(create_answer_from_tag)

        pd_to_file(dfpred, dirout + '/dfpred_text_generated.parquet', show=1)


    def data_NERgeo_fun_prepro_text_predict(row):
        """
        # Location, address, city, country, location_type, type_exclude
        # Location_type=\[(.*?)\],location_type_exclude=\[(.*?)\]

        """
        text  = row['answer_fmt']
        query = row["text"]
        # location = re.findall(r"location='(.*?)'", p[0])
        pattern = r"location='(.*?)',"
        matches = re.findall(pattern, text)
        values = []
        if len(matches):
            assert len(matches) == 1, matches
            values.append(
                {
                    "class":'location',
                    'value': matches[0],
                    'start': query.index(matches[0]),
                    'end' : query.index(matches[0]) + len(matches[0])
                }
            )

        pattern = r"city='(.*?)',"
        matches = re.findall(pattern, text)
        if len(matches):
            assert len(matches) == 1, matches
            values.append(
                {
                    "class":'city',
                    'value': matches[0],
                    'start': query.index(matches[0]),
                    'end' : query.index(matches[0]) + len(matches[0])
                }
            )
        pattern = r"country='(.*?)',"
        matches = re.findall(pattern, text)
        if len(matches):
            assert len(matches) == 1, matches

            values.append(
                {
                    "class":'country',
                    'value': matches[0],
                    'start': query.index(matches[0]),
                    'end' : query.index(matches[0]) + len(matches[0])
                }
            )

        pattern = r"location_type=\[(.*?)\]"
        matches = re.findall(pattern, text)
        if len(matches):
            assert len(matches) == 1, matches
            if len(matches[0].strip()):
                for i in matches[0].split(","):
                    x = i.strip()
                    if x[0] == "'" and x[-1] == "'":
                        x=x[1:-1]
                    if x not in query:
                        log(x, query)
                    values.append(
                        {
                            "class":'location_type',
                            'value': x,
                            'start': query.index(x),
                            'end' : query.index(x) + len(x)
                        }
                    )

        pattern = r"location_type_exclude=\[(.*?)\]"
        matches = re.findall(pattern, text)
        if len(matches):
            assert len(matches) == 1, matches
            if len(matches[0].strip()):
                for i in matches[0].split(","):
                    x = i.strip()
                    if x[0] == "'" and x[-1] == "'":
                        x=x[1:-1]
                    values.append(
                        {
                        "class":'location_type_exclude',
                        'value': x,

                        'start': query.index(x),
                        'end' : query.index(x) + len(x)
                        }
                    )
        return values


    def data_NERgeo_fun_extract_from_answer_full(row):
        """  
            #             address': '4700 Gilbert Ave',
            #    'city': 'Chicago',
            #    'country': 'United States',
            #    'location_type': 'hot dog stand and viewpoint',
            #    'location_type_exclude': [],
            #     query = row["text"]

        """
        dict_i4 = json.loads(row['answerfull'])['args']
        query = row["text"]
        values =[]
        for key, value in dict_i4.items():
            if key=='place_name':
                key='location'
            if key =='radius' or key=='navigation_style':continue
            if key =='location_type':
                value = value.split("and")
                value = [i.strip() for i in value]
                values.extend([{
                    "class":key,
                    'value': i,
                    'start': query.index(i),
                    'end': query.index(i) + len(i)
                } for i in value])
            elif key =='location_type_exclude':
                if isinstance(value, str):
                    value = value.split("and")
                    value = [i.strip() for i in value]
                    values.extend([{
                        "class":key,
                        'value': i,
                        'start': query.index(i),
                        'end': query.index(i) + len(i)
                    } for i in value])
                else:
                    assert len(value) == 0
            else:
                if value.strip() not in query:
                    log(value, 'x', query, 'x', key)
                values.append(
                    {
                        "class": key,
                        'value': value.strip(),
                        'start': query.index(value.strip()),
                        'end': query.index(value.strip()) + len(value.strip())
                    }
                )
        return values


    def data_NERgeo_fun_answer_clean(ss:str):
      ss = ss.replace("search_places(", "")
      return ss



######### Data Loader for Train
def data_NERgeo_load_datasplit(dirin="./ztmp/data/ner/ner_geo"):
    """ 



    """ 
    df = pd_read_file(dirin + "/train")
    log(df)
    assert df[[ "text", "ner_list"  ]].shape
    assert len(df)>1     and df.shape[1]>= 2 


    df_val = pd_read_file(dirin + "/val", )
    log(df_val)
    assert df_val[[ "text", "ner_list"  ]].shape
    assert len(df_val)>1 and df.shape[1]>= 2


    nerdata_validate_dataframe(df, df_val)
    return df, df_val


def data_NERgeo_load_metadict(dirmeta="./ztmp/data/ner/ner_geo/meta/meta.json"):
    nerlabelEngine = NERdata(dirmeta=dirmeta)    
    I2L, L2I, NLABEL_TOTAL, meta_dict =  nerlabelEngine.metadict_load(dirmeta=dirmeta)

    return nerlabelEngine, meta_dict 





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

    
    
def data_anews_create_norm(dirin="./ztmp/data/cats/toxicity/raw/*.csv"):
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
    
    

        to    
                text:    "My name is John Doe and I love my car. I bought a new car in 2020."
                labels:  identity_hate_NO,insult,obscene,severe_toxic,threat_NO,toxic


    """
    from asearch.nlp.cats.multilabel import LABELdata    
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
    
    from asearch.nlp.cats.multilabel import LABELdata
    labeldata = LABELdata()
    I2L, L2I, NLABEL_TOTAL, meta_dict = labeldata.load_metadict(dirmeta=dirmeta)

    return labeldata, meta_dict







###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()













