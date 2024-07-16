""" Generate synthetic questions from answers

    using LLM 

    ### Usage:

        alias pyllm="python query.py       "

        # Prompt Optimization
            pyllm prompt_find_best --dirout ztmp/exp/


        # Generating synthetic queries
            pyllm generate_synthetic_question  --dirdata ztmp/bench --dataset ag_news --nfile 10 --nquery 5 --prompt_id "20240505-514"



    ### summarize

        A) DSPy : initial prompt ---> Optim --> final prompt (Saved in DPSy model file).
            Optimizer (ie Prompt engineering)  Not inference.

        Prompt IS Model dependant : QWaen, GPT 3.6 , GPT 4.0  (can be similar.... but not same.)

        Append to promnpt storage csv



        B) At inference (Deterimnistic in Prompt)
        1 fixed promp_template
            filed with { value }
                --> send to API XXXX
                --> Get  answers
    
    Inference Structure:
        csv file on disk as Storage of ALL promptS (for all kind of tasks/queries)

        id_prompt, prompt_template, prompt_examples, prompt_arg, prompt_origin, task_name, model_name_full, dt,  api_endpoint, info_json,  ...
                                                                                            Openai/GPT3.5
                                                                                                Qwen 8gb 

        prompt_store(pomrpt, )  ### append to csv 


        prompt_template:
            You are and assistant.  Query is {queries}.  side info is {side_info}


        prompt_args:
            { "args" : { 
                    "queries":   ("str", "this is an query"),
                    "side_info": ("str", "this is an side info"),
            }         


        prompt_example:
            [ " You are and assistant.  Query is Who is presndient.  side info is  my side info.  ", ... ]

            --> history of all prompts --> You have all --> Crooss easily, debug, transparent.


        ### At inference
        Pick one prompt from csv --  by ID
        fill  { value }  
            --> send it to  API




    ### Ressources

        https://github.com/microsoft/LMOps
                


    ### Folder structure

    ztmp/exp/
            /YMD_HMS/
                info.json  : meta data about  results.
                /query_model/  DPSY model
                /out/  df_synthetic_query.csv

            expriment: training, optimization, .... (anything which is kinf of "optimized")

            ### Copy  one which is most interesting to  latest one.
            copy  ztmp/exp/YMS_HMS/   ztmp/bench/ag_news/query/latest/


    ztmp/hf_dataset/   ### All parquet have SAME columns names (mapping is done before saving on disk)
            data/ 
                agnews/ train / df.parquet
                data2/ ...

            meta/ agnews.json
                otherdata.json
                data2.json

    ztmp/bench/
            /ag_news/query/df_synthetic_queries_20220201_120000.csv


    ztmp/norm/
        /ag_news/  train/  df1.parquet


"""
import os, copy, random, fire
import re

import pandas as pd
from box import Box

from openai import OpenAI
import dspy

from utilmy import (pd_read_file, pd_to_file, os_makedirs, glob_glob, date_now,
                    json_load, json_save)
from utilmy import log, log2

global turbo


#########################################################################################
### Prompt Search/Egnineering  ##########################################################
def prompt_find_best(dirdata: str = "./ztmp/bench/norm/", dataset: str = "ag_news",
                     dirout: str = "./ztmp/exp",
                     nfile: int = 1, nquery: int = 1, ):
    """ Optimize  Prompt using DPSY

        python query.py prompt_find_best --dataset "ag_news" --nfile 1 --nquery 1
      
        Args:
            dirdata (str):  path containing  data.
            dataset (str):  dataset to be used for finding  best prompt.
            dirout (str):  output path for storing results.
            nfile (int):  number of files to process.
            nquery (int):  number of queries to generate.

    """
    global turbo

    info = Box({})
    info.name = "prompt_find_best"
    info.description = "prompt find best"
    info.uri_code = "query.py::prompt_find_best"

    model_id = "gpt-3.5-turbo"

    dt = date_now(fmt="%Y%m%d/%H%M%S", returnval="str")
    dirout2 = f"{dirout}/{dt}"
    dirout_model = f"{dirout2}/query_model"
    dirout_query = f"{dirout2}/out/df_synthetic_query.csv"

    log("#######  Create DSPy optimizer ")
    dspy_init(model_name=model_id)
    q_model = DspyQuestionGenerator()
    os_makedirs(dirout2)
    q_model.save(dirout_model)


    log("#######  Load Data ")
    dirdata2 = f"{dirdata}/{dataset}/*/df*.parquet"    #### ag_news/train/df.parquet
    df = pd_read_file(dirdata2, nfile=nfile)  ##  Real Dataset
    # filter out rows with body length < 100 words
    df["len"] = df["body"].apply(lambda x: len(x.split()))
    df        = df[df["len"] > 100]
    nquery    = min(nquery, len(df))
    df_query  = df.sample(nquery)


    log("#######  Generate synthetic queries using DPSy ")  #
    df_query["queries"] = df_query["body"].apply(lambda x: q_model(x).answer)
    df_query = df_query[["id", "body", "queries"]]
    pd_to_file(df_query, f"{dirout_query}", show=1)

    log("#######  Insert best Prompt into PromptStorage")
    """ Template from DSPy
    ======
        You are a helpful assistant. Given  following document, 
        generate a list of synthetic questions that could be answered 
        by referring to  information provided in  document. 
        ....
        ---
        Follow  following format.
        Document: a document to generate queries from
        Queries: list of 10 queries separated by '@@'.
        ---
        Document: {document}
        Queries: 

    """
    ### {document} is defined when we define  DPSy DspyGenerateSyntheticQueries class. 
    prompt_template = q_model.get_prompt_template()
    prompt_actual = prompt_template.replace("{document}", " This an example of document ")

    pstore = PromptStorage()  ### prompts/prompt_hist.csv
    pstore.append(model_id=model_id, task_name="synthetic_query_generation",
                  prompt_examples=[prompt_actual],
                  prompt_args={"document": ("str", "reference text where  question is generated from")},
                  prompt_template=prompt_template)

    json_save(dict(info), f"{dirout2}/info.json")

    # Debug print last llm query/output, for debugging purposes
    turbo.inspect_history(n=1)


def dspy_init(model_name="gpt-3.5-turbo"):
    global turbo
    # initialize dspy module
    # model_name = "gpt-4"
    turbo = dspy.OpenAI(model=model_name)
    dspy.settings.configure(lm=turbo)


def test_dpsy_optimization(dirstorage="ztmp/bench/ag_news/query/prompt_hist.csv"):
    ### DSPy
    dspy_init(model_name="gpt-3.5-turbo")
    question_generator = DspyQuestionGenerator(sep="あ")
    template = question_generator.get_prompt_template()
    assert len(template) > 0


# build signature and specify  PROMPT input and output details in docstrings and description
class DspyGenerateSyntheticQueries(dspy.Signature):
    """You are a helpful assistant. Given  following document,
       generate a list of synthetic questions that could be answered by referring to  information provided in  document.
       Ensure that  questions are clear, concise, and that their answers can be directly inferred from  document text.
    """
    document = dspy.InputField(desc="a document to generate queries from")
    queries = dspy.OutputField(desc="list of 10 queries separated by '@@'.")


class DspyQuestionGenerator(dspy.Module):
    def __init__(self, sep="あ"):
        super().__init__()
        self.generate_answer = dspy.Predict(DspyGenerateSyntheticQueries)
        self.sep = sep

    def forward(self, document):
        prediction = self.generate_answer(document=document)
        if self.sep not in prediction.queries:
            queries = prediction.queries.split("\n")
            # remove numbered prefix from queries
            # queries = [q.split(". ")[1] for q in queries]
            prediction.queries = self.sep.join(queries)

        # queries = prediction.queries.split("")
        return dspy.Prediction(document=document, answer=prediction.queries)

    def get_prompt_template(self):
        """
        hacky way to get  prompt template out of dspy program
        """
        self.forward(document=" quick brown fox jumps.")
        # print(repr(question_generator))
        p_template = turbo.history[-1]['prompt'].replace(" quick brown fox jumps.", "{document}")
        return p_template


#######################################################################################
### Prompt storage  ###################################################################
class PromptStorage:
    def __init__(self, dirstorage: str = None,
                 sep="あ",  ### Using unicode Japanese character....
                 sep_prompt="う"):  ### Using Unicode Japanese character....
        self.df = None
        ### Fixes column names
        self.cols = ["prompt_id", "prompt_template", "prompt_examples", "prompt_args", "prompt_origin", "task_name",
                     "model_id", "dt", "api_endpoint", "info_json"]
        self.sep = sep  # note sep is expected to be single char by scv reader
        self.sep_prompt = sep_prompt

        if isinstance(dirstorage, str):
            self.dirstorage = dirstorage
        else:
            self.dirstorage = os.environ.get("prompt_dirstorage", "ztmp/prompt_hist.csv")

        self.load()

    def promptid_create(self):
        """Generate a unique prompt ID.
        Returns:
            str:  generated prompt ID in  format "YYYYMMDD-random_number".
        """
        ymd = date_now(fmt="%Y%m%d")
        prompt_id = f"{ymd}-{random.randint(100, 999)}"
        return prompt_id

    def load(self):
        """Load from dirstorage
        """
        if not os.path.exists(self.dirstorage):
            self.df = pd.DataFrame(columns=self.cols)
            return
        self.df = pd_read_file(self.dirstorage, sep=self.sep, engine="python")
        assert self.df[self.cols].shape

    def append(self, prompt_template, model_id, prompt_args, prompt_examples="", task_name="", info_json=""):
        """Append a new prompt to  prompt storage.

        Args:
            prompt_template (str):  template for  prompt.
            model_id (str):  ID of  model.
            prompt_args (dict):  arguments for  prompt.
            prompt_examples (Optional[str]):  examples for  prompt.     : None.
            task_name (Optional[str]):  name of  task.     : None.
            info_json (Optional[str]): Additional information in JSON format.     : None.
        """
        dfnew = {ci: "" for ci in self.cols}

        ### Codeium  and Phind in VScode
        dfnew["prompt_id"] = self.promptid_create()
        dfnew["prompt_template"] = prompt_template
        dfnew["model_id"] = model_id
        dfnew["prompt_args"] = prompt_args
        dfnew["dt"] = date_now(fmt="%Y-%m-%d %H:%M:%S")

        if isinstance(prompt_examples, list):
            prompt_examples = self.sep_prompt.join(prompt_examples)

        dfnew["prompt_examples"] = prompt_examples
        dfnew["task_name"] = task_name
        dfnew["info_json"] = info_json
        dfnew = pd.DataFrame(dfnew)

        self.df = pd.concat([self.df, dfnew], ignore_index=True)
        self.save()
        return dfnew

    def save(self):
        """Save to dirstorage
        """
        pd_to_file(self.df, self.dirstorage, sep=self.sep, index=False)

    def get_prompt(self, prompt_id: str, ) -> dict:
        dfi = self.df[self.df["prompt_id"] == prompt_id]
        ddict = dfi.to_dict(orient="records")[0]
        return ddict


def test_prompt_storage():
    #### Using Prompt 
    template = "ok"
    # make random dirtmp
    tmp_storage = f"ztmp/{random.randint(100, 999)}.csv"
    prompt_storage = PromptStorage(dirstorage=tmp_storage)
    prompt_args = {"args": {
        "document": ("str", "this is  document from which you want to generate queries")
    }}
    #
    prompt_storage.append(prompt_template=template, model_id="gpt-3.5-turbo",
                          task_name="synthetic_query_generation",

                          prompt_args=prompt_args)
    prompt_storage.save()
    temp_df = pd_read_file(tmp_storage)
    assert len(temp_df) == 1
    os.remove(tmp_storage)
    # print(prompt_storage.df)


#########################################################################################
###  Inference: query new create ########################################################
def prompt_create_actual(prompt_template: str, prompt_values: dict):
    """Generate an actual prompt by replacing placeholders in  template with values from  prompt_values dictionary.
    Args:
        prompt_template (str):  template prompt containing placeholders.
        prompt_values (dict): A dictionary containing key-value pairs representing  values to replace  placeholders.

    Returns:
        str:  actual prompt with placeholders replaced by their corresponding values.
    """
    prompt_actual = copy.deepcopy(prompt_template)
    for key, val in prompt_values.items():
        prompt_actual = prompt_actual.replace(f"{{{key}}}", val)
    return prompt_actual


def llm_get_answer(prompt, model="gpt-3.5-turbo", max_tokens=1000):
    """
    """
    client = OpenAI()

    response = client.chat.completions.create(model=model,
                                              messages=[{"role": "user", "content": prompt}],
                                              max_tokens=max_tokens)
    return response.choices[0].message.content


def llm_prompt_compress(text:str)->str:
   """ Prompt Compression for long text

      ### Usage  
        pip install git+https://github.com/microsoft/autogen.git@main  --no-cache
        pip install "llmlingua<0.3"   ### Long context

        python rag/query.py llm_prompt_compress --text "write a long poem with many words."

      ### Infos 
        https://github.com/microsoft/autogen.git
        
        https://microsoft.github.io/autogen/docs/topics/handling_long_contexts/compressing_text_w_llmligua

        https://github.com/microsoft/autogen
        import tempfile

        import fitz  # PyMuPDF
        import requests

        from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
        from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor

        AUTOGEN_PAPER = "https://arxiv.org/pdf/2308.08155"


        def extract_text_from_pdf():
            # Download the PDF
            response = requests.get(AUTOGEN_PAPER)
            response.raise_for_status()  # Ensure the download was successful

            text = ""
            # Save the PDF to a temporary file
            with tempfile.TemporaryDirectory() as temp_dir:
                with open(temp_dir + "temp.pdf", "wb") as f:
                    f.write(response.content)

                # Open the PDF
                with fitz.open(temp_dir + "temp.pdf") as doc:
                    # Read and extract text from each page
                    for page in doc:
                        text += page.get_text()

            return text

        # Example usage
        pdf_text = extract_text_from_pdf()

        llm_lingua = LLMLingua()
        text_compressor = TextMessageCompressor(text_compressor=llm_lingua)
        compressed_text = text_compressor.apply_transform([{"content": pdf_text}])

        

   """  
   from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
   from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor
   llm_lingua = LLMLingua()
   text_compressor = TextMessageCompressor(text_compressor=llm_lingua)
   ddict = text_compressor.apply_transform([{"content": text}])
   return ddict[0]["content"]



def llm_output_clean_custom_v1(query: str, sep="@@"):
    """
    hacky way to clean queries. Ideally should be separated by separator only.
    """
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

















################################################################################
def generate_synthetic_question(dirdata: str = "ztmp/bench", dataset: str = "ag_news",
                             dirout: str    = "ztmp/bench",
                             prompt_id: str = "",
                             nfile: int     = 1, nquery: int = 1,
                             subsample      = 1):
    """Generate synthetic queries via LLM

      python query.py generate_synthetic_question --dataset "ag_news" --nfile 1 --nquery 1
      
    """
    global turbo

    #### Export path of  synthetic queries
    dt = date_now(fmt="%Y%m%d_%H%M%S", returnval="str")
    dirout2 = f"{dirout}/{dataset}/query/df_synthetic_queries_{dt}.parquet"


    log("#######  Load prompt template from storage")
    prompt0 = PromptStorage()  ### using ENV variables prompt_dirstorage="prompts/prompt_hist.csv"
    prompt_dict = prompt0.get_prompt(prompt_id=prompt_id)  ## user decide whihc om
    model_id = prompt_dict.get("model_id", "gpt-3.5-turbo")


    log("###### Load Reference answer data  ")
    diranswer = f"{dirdata}/norm/{dataset}/*/df*.parquet"
    df = pd_read_file(diranswer, nfile=nfile)  ##  Real Dataset


    log("###### Data : Filter out rows with body length < 100 words")
    df["len"] = df["body"].apply(lambda x: len(x.split()))
    df = df[df["len"] > 100]
    log(df.shape)
    nquery   = min(nquery, len(df))
    df_query = df.sample(nquery) if subsample > 0 else df

    log("##### Load custom processor ")
    llm_output_cleaner_fun  = llm_output_clean_custom_v1


    log("###### Generate Synthetic questions from answer ")
    query = []
    for i, row in df_query.iterrows():
        prompt_values = {"document": row["body"]}
        # print(prompt_values)
        prompt_actual = prompt_create_actual(prompt_dict["prompt_template"], prompt_values)
        answer = llm_get_answer(prompt=prompt_actual, model=model_id)

        # answer =  llm_output_clean_custom_v1(answer)
        # queries = answer.split(sep="@@")
        queries = llm_output_cleaner_fun(answer)
        query.append(queries)


    df_query["query"] = query
    df_query = df_query[["id", "title", "body", "query"]]
    # explode df_query based on query list
    df_query = df_query.explode("query")

    pd_to_file(df_query, f"{dirout2}", show=1)





##########################################################################################
if __name__ == '__main__':
    fire.Fire()
