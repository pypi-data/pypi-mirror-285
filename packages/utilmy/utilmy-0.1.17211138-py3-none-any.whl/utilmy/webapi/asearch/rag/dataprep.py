""" Various data preparation for Index/Search



    ### Usage:
        alias pydata="python rag/dataprep.py  "

        #### Generate synthetic questions from answers using LLM

            pydata generate_synthetic_question  --dirdata ztmp/bench --dataset ag_news --nfile 10 --nquery 5 --prompt_id "20240505-514"


    ### Folder structure
    ztmp/exp/
            /YMD_HMS/
                info.json  : meta data about  results.
                /query_model/  DPSY model
                /out/  df_synthetic_query.csv

            expriment: training, optimization, .... (anything which is kinf of "optimized")

            ### Copy  one which is most interesting to  latest one.
            copy  ztmp/exp/YMS_HMS/   ztmp/bench/ag_news/query/latest/


    ztmp/data/   ### All parquet have SAME columns names (mapping is done before saving on disk)
            cats/
                agnews/ train / df.parquet
                data2/ ...

           ner/legaldoc/ raw/
                         train/
                         test/
                         meta/

    ztmp/bench/
            /ag_news/query/df_synthetic_queries_20220201_120000.csv


    #### Data Structure





"""
import glob
import os, copy, random, fire, pandas as pd, numpy as np
from box import Box
import datasets



from utilmy import (pd_read_file, pd_to_file, os_makedirs, glob_glob, date_now,
                    json_load, json_save)
from utilmy import log, log2


from rag.llm import (
    PromptStorage,
    prompt_compress,
    prompt_create_actual,
    llm_get_answer
)



################################################################################
def test_hf_dataset_to_parquet():
    """test function for converting Hugging Face datasets to Parquet files"""
    name = "ag_news"
    splits = ["train", "test"]
    dataset_hf_to_parquet(name, dirout="hf_datasets", splits=splits)
    # read parquet files
    for split in splits:
        assert os.path.exists(f"hf_datasets/{name}_{split}.parquet")
        # pd = pd_read_file(f"hf_datasets/{dataset_name}_{split}.parquet")
        # print(pd.columns)





################################################################################
########## Synthetic questions for Questions, Anaswers benchmark  ##############
def generate_synthetic_question(dirdata: str = "./ztmp/data/cats/agnews/train/", 
                             dirout: str    = "ztmp/bench",
                             prompt_id: str = "",
                             nfile: int     = 1, nquery: int = 1,
                             subsample      = 1):
    """Generate synthetic questions via LLM
      python dataprep.py generate_synthetic_question --dataset "ag_news" --nfile 1 --nquery 1
      
    """
    global turbo

    #### Export path of  synthetic queries
    dt      = date_now(fmt="%Y%m%d_%H%M%S", returnval="str")
    dirout2 = f"{dirout}/df_synthetic_questions_{dt}.parquet"

    log("####### Load Answers data as Context for the LLM  ")
    df_context = generate_synthetic_question_loadata(dirdata=dirdata, nfile=nfile, nrows=nquery, subsample=1)

    log("####### Load Custom Post-processor ")
    llm_output_cleaner_fun  = generate_synthetic_question_llmcleaner


    #########################################################################################
    log("#######  Load prompt template from storage")
    prompt0     = PromptStorage()  ### using ENV variables prompt_dirstorage = "prompts/prompt_hist.csv"
    prompt_dict = prompt0.get_prompt(prompt_id=prompt_id)  ## user decide whihc om
    model_id    = prompt_dict.get("model_id", "gpt-3.5-turbo")


    log("###### Generate Synthetic questions from answer ")
    queries = []
    for i, row in df_context.iterrows():
        prompt_values = {"document": row["body"]}
        # print(prompt_values)
        prompt_actual = prompt_create_actual(prompt_dict["prompt_template"], prompt_values)
        answer        = llm_get_answer(prompt=prompt_actual, model=model_id)

        # answer =  llm_output_clean_custom_v1(answer)
        # queries = answer.split(sep="@@")
        query = llm_output_cleaner_fun(answer)
        queries.append(query)


    df_context["query"] = queries
    df_context = df_context[["id", "title", "body", "query"]]
    df_context = df_context.explode("query")      # explode df_query based on query list
    pd_to_file(df_context, f"{dirout2}", show=1)


def generate_synthetic_question_loadata(dirdata: str = "./ztmp/data/cats/agnews/train/", 
                                        nfile=1, nrows=1000, subsample=1):
    log("###### Load Reference answer data  ")
    # diranswer = f"{dirdata}/agnews/train/df*.parquet"
    df = pd_read_file(dirdata, nfile=nfile)  ##  Real Dataset

    log("###### Data : Filter out rows with body length < 100 words")
    df["len"] = df["body"].apply(lambda x: len(x.split()))
    df = df[df["len"] > 100]
    log(df.shape)
    nquery   = min(nrows, len(df))
    df_context = df.sample(nquery) if subsample > 0 else df
    log(df_context)

    return df_context


def generate_synthetic_question_llmcleaner(query: str, sep="@@"):
    """hacky way to clean queries. Ideally should be separated by separator only.
    """
    import re
    query = query.replace("\n", "")
    query_list = query.split("?")

    # remove sep
    query_list = [q.replace(sep, "") for q in query_list]

    # remove numbered prefix via regex
    query_list = [re.sub(r"^[0-9]*\.", "", q) for q in query_list]
    query_list = [q.strip() for q in query_list]
    query_list = [q for q in query_list if len(q) > 0]
    query_list = [f"{q}?" for q in query_list]

    return query_list
    # result = sep.join(query_list)
    # return result





###################################################################################
###################################################################################
def dataset_hf_to_parquet(
        name, dirout: str = "hf_datasets", splits: list = None, mapping: dict = None
):
    """Converts a Hugging Face dataset to a Parquet file.
    Args:
        dataset_name (str):  name of  dataset.
        dirout (str):  output directory.
        mapping (dict):  mapping of  column names.     : None.
    """
    dataset = datasets.load_dataset(name)
    # print(dataset)
    if splits is None:
        splits = ["train", "test"]

    for key in splits:
        split_dataset = dataset[key]
        output_file = f"{dirout}/{name}/{key}.parquet"
        df = pd.DataFrame(split_dataset)
        log(df.shape)
        if mapping is not None:
            df = df.rename(columns=mapping)

        # Raw dataset in parquet
        pd_to_file(df, output_file)


def dataset_kaggle_to_parquet(
        name, dirout: str = "kaggle_datasets", mapping: dict = None, overwrite=False
):
    """Converts a Kaggle dataset to a Parquet file.
    Args:
        dataset_name (str):  name of  dataset.
        dirout (str):  output directory.
        mapping (dict):  mapping of  column names.     : None.
        overwrite (bool):  whether to overwrite existing files.     : False.
    """
    import kaggle
    # download dataset and decompress
    kaggle.api.dataset_download_files(name, path=dirout, unzip=True)

    df = pd_read_file(dirout + "/**/*.csv", npool=4)
    if mapping is not None:
        df = df.rename(columns=mapping)

    pd_to_file(df, dirout + f"/{name}/parquet/df.parquet")


def dataset_agnews_schema_v1(
        dirin="./**/*.parquet", dirout="./norm/", batch_size=50000
) -> None:
    """Standardize schema od a dataset"""
    flist = glob_glob(dirin)

    cols0 = ["text", "label"]

    for ii, fi in enumerate(flist):
        df = pd_read_file(fi, npool=1)
        log(ii, df[cols0].shape)

        #### New columns
        ### Schame : [ "id", "dt", ]
        n = len(df)
        dtunix = date_now(returnval="unix")
        df["text_id"] = [uuid_int64() for i in range(n)]
        df["dt"] = [int(dtunix) for i in range(n)]


        df["title"] = df["text"].apply(lambda x: x[:50])
        df["cat1"] = df["label"]
        del df["label"]
        df["cat2"] = ""
        df["cat3"] = ""
        df["cat4"] = ""
        df["cat5"] = ""

        fname = fi.split("/")[-1]
        fout = fname.split(".")[0]  # derive target folder from source filename

        dirouti = f"{dirout}/{fout}"
        pd_to_file_split(df, dirouti, ksize=batch_size)


def dataset_reformat_files(dirin="ztmp/bench/norm/ag_news/*/*.parquet", rename_map: dict = None):
    """
    rename columns
    """
    if rename_map is None:
        rename_map = {"id": "text_id", "body": "text"}
    flist = glob.glob(dirin)
    log(f"reformat #{len(flist)} files")
    for i, fl in enumerate(flist):
        df = pd_read_file(fl)
        if not set(rename_map.keys()).intersection(set(df.columns)):
            continue
        log(f"reformatting: {fl}")
        df.rename(columns=rename_map, inplace=True)
        pd_to_file(df, fl, show=0)
        # break




def pd_to_file_split(df, dirout, ksize=1000):
    kmax = int(len(df) // ksize) + 1
    for k in range(0, kmax):
        log(k, ksize)
        dirouk = f"{dirout}/df_{k}.parquet"
        pd_to_file(df.iloc[k * ksize: (k + 1) * ksize, :], dirouk, show=0)



def pd_fake_data(nrows=1000, dirout=None, overwrite=False, reuse=True) -> pd.DataFrame:
    from faker import Faker

    if os.path.exists(str(dirout)) and reuse:
        log("Loading from disk")
        df = pd_read_file(dirout)
        return df

    fake = Faker()
    dtunix = date_now(returnval="unix")
    df = pd.DataFrame()

    ##### id is integer64bits
    df["id"] = [uuid_int64() for i in range(nrows)]
    df["dt"] = [int(dtunix) for i in range(nrows)]

    df["title"] = [fake.name() for i in range(nrows)]
    df["body"] = [fake.text() for i in range(nrows)]
    df["cat1"] = np_str(np.random.randint(0, 10, nrows))
    df["cat2"] = np_str(np.random.randint(0, 50, nrows))
    df["cat3"] = np_str(np.random.randint(0, 100, nrows))
    df["cat4"] = np_str(np.random.randint(0, 200, nrows))
    df["cat5"] = np_str(np.random.randint(0, 500, nrows))

    if dirout is not None:
        if not os.path.exists(dirout) or overwrite:
            pd_to_file(df, dirout, show=1)

    log(df.head(1), df.shape)
    return df


def pd_fake_data_batch(nrows=1000, dirout=None, nfile=1, overwrite=False) -> None:
    """Generate a batch of fake data and save it to Parquet files.

    python engine.py  pd_fake_data_batch --nrows 100000  dirout='ztmp/files/'  --nfile 10

    """

    for i in range(0, nfile):
        dirouti = f"{dirout}/df_text_{i}.parquet"
        pd_fake_data(nrows=nrows, dirout=dirouti, overwrite=overwrite)



def np_str(v):
    return np.array([str(xi) for xi in v])




def uuid_int64():
    """## 64 bits integer UUID : global unique"""
    import uuid
    return uuid.uuid4().int & ((1 << 64) - 1)



##########################################################################################
if __name__ == '__main__':
    import fire
    fire.Fire()
