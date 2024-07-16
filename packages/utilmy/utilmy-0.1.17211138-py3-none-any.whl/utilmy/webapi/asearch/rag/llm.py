""" LLM tooling

    #### Init
        cd webapi/asearch/
        export PYTHONPATH="$(pwd)"


    ### Usage:
        alias pyllm="python rag/llm.py       "

        # Prompt Optimization
            pyllm prompt_find_best --dirout ztmp/exp/

        # Generating synthetic queries
            pyllm generate_question  --dirdata ztmp/bench --dataset ag_news --nfile 10 --nquery 5 --prompt_id "20240505-514"




"""
import asyncio
import concurrent
from concurrent.futures import ThreadPoolExecutor
import json
import os, copy, random, fire, re, pandas as pd
import time
import traceback
from multiprocessing import Pool

from box import Box

from openai import OpenAI
import dspy
from pydantic import BaseModel

global turbo  ### Debugging DSPy optinmization

from utilmy import (pd_read_file, pd_to_file, os_makedirs, glob_glob, date_now,
                    json_load, json_save, config_load)
from utilmy import log, log2, log_error

#### Local Import
from utils.util_exp import (exp_config_override)


#########################################################################
####### LLM Swiss-knife Class to call quickly ###########################
def test_single_request():
    dirout = "ztmp/gpt_out/"
    llm1 = LLM('openai', 'gpt-3.5-turbo')
    llm1.get_save("What is capital of Germany?", dirout=dirout)  ### No blocker calll


def test_bulk():
    dirout = "ztmp/gpt_out/"
    llm1 = LLM('openai', 'gpt-3.5-turbo')
    llm1.get_save_bulk(["What is capital of Germany?",
                        "What is capital of France?",
                        "What is capital of Spain?",
                        "What is capital of India?",
                        ], dirout=dirout)


from utilmy import json_save


def get_client(service: str, api_key: str = None, api_url: str = None):
    if service == 'openai':
        api_key = api_key or os.environ.get('OPENAI_KEY', '')
        api_base = api_url or "https://api.openai.com/v1"
        client = OpenAI(api_key=api_key, base_url=api_base)
        # self.modelid = model

    # elif service == 'groq':
    #     api_key = api_key or os.environ.get('GROQ_KEY', '')
    #     api_base = api_url or "https://api.groq.com/openai/v1"
    #     client = OpenAI(api_key=api_key, base_url=api_base)
    #     # self.modelid = model
    #
    #
    # elif service == 'azure':
    #     from openai import AzureOpenAI
    #     # https://{your-resource-name}.openai.azure.com/
    #     endpoint = os.environ.get['AZURE_OPENAI_url']
    #     client = AzureOpenAI(api_key=api_key, api_version="2023-12-01-preview",
    #                               azure_endpoint=endpoint)
    # elif service == 'claude':
    #     api_key = api_key or os.environ.get['CLAUDE_KEY']
    #     api_base = api_url or "https://api.anthropic.com/v1"
    #     self.client = OpenAI(api_key=api_key, base_url=api_base)
    #     self.modelid = model

    return client


class promptRequest(BaseModel):
    """
    class to store prompt request. To simplify argument passing while parellizing
    """
    prompt: str
    service: str = "openai"
    modelid: str = "gpt-3.5-turbo"
    topk: int = 10
    logprobs: bool = True
    temperature: float = 0
    max_tokens: int = 30
    dirout: str = "ztmp/gpt_out"
    json_schema: object = None
    api_key: str = None
    dirout: str = None



def llm_get_sync(prompt_request: promptRequest):
    """
    separate llm call logic. Easy to parellize.
    1. create llm client here
    2. call llm
    example output object:
    {
    "id": "chatcmpl-9k9MR8TtV301n6xAzfbxWM2liX2dV",
    "choices": [
        {
            "finish_reason": "length",
            "index": 0,
            "logprobs": [{"content": {}}],
            "message": {
                "content": "Sachin Tendulkar is a former Indian cricketer who is widely regarded as one of the greatest batsmen in the history of the",
                "role": "assistant"}
        }
    ],
    "created": 1720786099,
    "model": "gpt-3.5-turbo-0125",
    "object": "chat.completion",
    "system_fingerprint": None,
    "usage": {
        "completion_tokens": 30,
        "prompt_tokens": 16,
        "total_tokens": 46,
        "prompt": "Tell me about Sachin Tendulkar"
    }
}
    """
    try:

        client   = get_client(service=prompt_request.service)
        response = client.chat.completions.create(model=prompt_request.modelid,
                                                  messages=[{"role": "user", "content": prompt_request.prompt}],
                                                  logprobs=prompt_request.logprobs,
                                                  top_logprobs=prompt_request.topk,
                                                  temperature=prompt_request.temperature,
                                                  max_tokens=prompt_request.max_tokens,
                                                  )

        dd = response.to_dict()

        dd['prompt'] = prompt_request.prompt
        return dd
    except Exception as e:
        log(traceback.format_exc())
        log(e)


# def zzz_llm_get_save_sync(prompt_request: promptRequest):
#     """
#     """
#     try:
#         dd = llm_get_sync(prompt_request)
#
#         dirout1 = self.dirout if dirout is None else dirout
#         ts, tag = int(time.time()), random.randint(10000, 99999)
#         fname = f"{dirout1}/{ts}_{tag}.json"
#         json_save(dd, fname)
#
#     except Exception as e:
#         log(traceback.format_exc())
#         log(e)


def llm_get_with_schema(prompt_request: promptRequest):
    """
    Async function to get an enforced schema based on the provided prompt and JSON schema.

    Note: GPT_JSON is a wrapper with lightweight dependencies: only OpenAI, pydantic, and backoff.
    It calls openai API on our behalf.



    Args:
        self: The object instance.
        prompt: The prompt to be used in the API call.
        json_schema: json schema to be enforced.
    sample output: {
      "response": {
        "first_name": "Sachin",
        "last_name": "Tendulkar",
        "year_of_birth": 1973,
        "num_seasons_in_nba": 0
      },
      "prompt": "Tell me about Sachin Tendulkar\nRespond with the following JSON schema: {json_schema}"
    }
    """
    from gpt_json import GPTJSON, GPTMessage, GPTMessageRole
    API_KEY = prompt_request.api_key if prompt_request.api_key is not None else os.environ.get('OPENAI_KEY', '')


    gpt_json = GPTJSON[prompt_request.json_schema](API_KEY, prompt_request.modelid,
                                                   model_max_tokens=prompt_request.max_tokens)

    actual_prompt = f"{prompt_request.prompt}\nRespond with the following JSON schema: {{json_schema}}"
    payload       = asyncio.run(gpt_json.run(
        messages=[
            GPTMessage(
                role=GPTMessageRole.USER,
                content=actual_prompt
            )
        ]
    ))
    # print(payload)
    # print(dict(payload))
    dd = {}
    dd["response"] = json.loads(payload.raw_response.content[0].text)
    dd["prompt"] = actual_prompt
    # print(json_response)
    return dd



class LLM(object):
    def __init__(self, service='openai', model="gpt-3.5-turbo",
                 dirout="ztmp/gpt_answer/",
                 api_key=None, api_url=None,
                 temperature=0,
                 max_tokens=2000,
                 **kw):
        """ Various util functions for quick LLM : One Liner method
            Portable class to any project.

             ll1 = LLM(service='groq', mdoel='llama3-70b', )

             ll1.get_save(prompt+'mypromt, dirout='ztmp/dirout/")

           Groq:  800 token /sec. for small Mistral.
                   70b llama3  300 token

           Groq2:  Text cleaning , LLM is very good,         

             20,000 calls to Groq (dataset toc lean up) -->  1 USD
                 text; 1500 token per call.

                 lllam3 70B
                 mistal 7B : 

                 
        """
        self.error_callback = None
        self.dirout = dirout
        self.service = service
        self.model = model
        self.api_key = api_key

        ### Output Control
        self.temperature = temperature
        self.max_tokens = max_tokens

        from openai import OpenAI

        if service == 'openai':
            api_key = api_key or os.environ.get('OPENAI_KEY', '')
            api_base = api_url or "https://api.openai.com/v1"
            self.client = OpenAI(api_key=api_key, base_url=api_base)
            self.modelid = model

        elif service == 'groq':
            api_key = api_key or os.environ.get('GROQ_KEY', '')
            api_base = api_url or "https://api.groq.com/openai/v1"
            self.client = OpenAI(api_key=api_key, base_url=api_base)
            self.modelid = model


        elif service == 'azure':
            from openai import AzureOpenAI
            # https://{your-resource-name}.openai.azure.com/
            endpoint = os.environ.get['AZURE_OPENAI_url']
            self.client = AzureOpenAI(api_key=api_key, api_version="2023-12-01-preview",
                                      azure_endpoint=endpoint)


        elif service == 'claude':
            api_key = api_key or os.environ.get['CLAUDE_KEY']
            api_base = api_url or "https://api.anthropic.com/v1"
            self.client = OpenAI(api_key=api_key, base_url=api_base)
            self.modelid = model

        from multiprocessing import Pool

    def get_save_async(self, prompt: str, dirout: str = None, output_schema: object = None):
        """

            ***Regarding using pool as class attribute or parellizing class method:***
            Pool needs to pickle (serialize) everything it sends to its worker-processes (IPC). Pickling actually only
            saves the name of a function and unpickling requires re-importing the function by name.
            For that to work, the function needs to be defined at the top-level, nested functions won't be importable by
            the child and already trying to pickle them raises an exception (more).
            Source: https://stackoverflow.com/questions/52265120/python-multiprocessing-pool-attributeerror



           Be careful : it cannot be used in terminal because the parent process is killed.
           2 ways: use in another process or use in terminal...


           I control myself the waiting time.

           for i in range
               LLM.get_save_async(...)


           ### I Control the waiting time. by mysefl.    


        for single request.Saves output in a json file

            No, we do not need to wait for the function to be executed when using pool.apply_async(). 
            It returns an AsyncResult object immediately, allowing asynchronous execution. To wait for the result, you can use:

            result.get() - Blocks until the result is ready
            result.wait() - Waits for the result without blocking
            result.ready() - Checks if the result is available


        """
        prompt_request = promptRequest(prompt=prompt, service=self.service, modelid=self.modelid,
                                       json_schema=output_schema)

        # synchronous call. parallelization responsibility on caller.
        if not output_schema:
            result = llm_get_sync(prompt_request)
        else:
            prompt_request.api_key = self.api_key  ### wokaround for JSON
            result = llm_get_with_schema(prompt_request)

        if dirout is not None:
            dirout1 = self.dirout if dirout is None else dirout
            ts, tag = int(time.time()), random.randint(10000, 99999)
            fname = f"{dirout1}/{ts}_{tag}.json"
            json_save(result, fname)
        # result.get()  ### no need since it is saving on disk.

    def get_batch(self, prompts: list, dirout: str = None, output_schema: object = None, max_workers=None):

        """
        multiple request
        saves output in a jsonl file
        """

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # If max_workers is None or not given, it will default to the number of processors on the machine,
            # multiplied by 5 assuming it"s being used for IO intensive tasks
            # Start the load operations and mark each future with its prompt
            func_to_be_used = llm_get_sync if not output_schema else llm_get_with_schema
            future_to_prompt = {executor.submit(func_to_be_used, promptRequest(prompt=prompt, service=self.service,
                                                                            modelid=self.modelid,
                                                                   json_schema=output_schema)): prompt for
                                prompt
                                in prompts}
            results = []
            for future in concurrent.futures.as_completed(future_to_prompt):
                url = future_to_prompt[future]
                try:
                    data = future.result()
                    # print(f"data: {data}")
                    results.append(data)
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))


        if dirout is not None:
            ###  1 json contans sub-json
            dirout1 = self.dirout if dirout is None else dirout
            ts, tag = int(time.time()), random.randint(10000, 99999)
            fname = f"{dirout1}/{ts}_{tag}.jsonl"

            with open(fname, 'w') as fp:
                for res in results:
                    fp.write(f"{res}" + '\n')  # json.dump(res)

        return results



    def zzz_get_save(self, prompt: str, dirout: str = None):
        result = self.pool0.apply_async(self.zzz_get_save_sync, (prompt, dirout))
        # result.get()  ### no need since it is saving on disk.

    def zzz_get_save_sync(self, prompt: str, dirout: str, topk=10, logprobs=True):
        import time, random
        from utilmy import json_save
        try:

            response = self.client.chat.completions.create(model=self.modelid,
                                                           messages=[{"role": "user", "content": prompt}],
                                                           logprobs=logprobs,
                                                           top_logprobs=topk,
                                                           temperature=self.temperature,
                                                           max_tokens=self.max_tokens,
                                                           )

            dd = response.to_dict()

            dd['prompt'] = prompt

            dirout1 = self.dirout if dirout is None else dirout
            ts, tag = int(time.time()), random.randint(10000, 99999)
            fname = f"{dirout1}/{ts}_{tag}.json"

            json_save(dd, fname)
            return fname

        except Exception as e:
            log(e)

    # def zzz_get_enforce_schema(self, prompt: str, json_schema=None):
    #     """
    #         llmformatenforcer
    #
    #         from lmformatenforcer import CharacterLevelParser, LMFormatEnforcer
    #             from openai import OpenAI
    #
    #             client = OpenAI()
    #             parser = CharacterLevelParser("JSON")
    #             enforcer = LMFormatEnforcer(parser)
    #
    #             response = client.chat.completions.create(
    #                 model="gpt-3.5-turbo",
    #                 messages=[{"role": "user", "content": "Generate JSON with name and age"}],
    #                 temperature=0,
    #                 max_tokens=100,
    #                 format_enforcer=enforcer
    #             )
    #
    #         https://github.com/noamgat/lm-format-enforcer
    #         !pip install transformers torch lm-format-enforcer huggingface_hub optimum
    #         !pip install auto-gptq --extra-index-url https://huggingface.github.io/autogptq-index/whl/cu118/
    #
    #         from pydantic import BaseModel
    #         from lmformatenforcer import JsonSchemaParser
    #         from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
    #         from transformers import pipeline
    #
    #         class AnswerFormat(BaseModel):
    #             first_name: str
    #             last_name: str
    #             year_of_birth: int
    #             num_seasons_in_nba: int
    #
    #         # Create a transformers pipeline
    #         hf_pipeline = pipeline('text-generation', model='TheBloke/Llama-2-7b-Chat-GPTQ', device_map='auto')
    #         prompt = f'Here is information about Michael Jordan in the following json schema: {AnswerFormat.schema_json()} :\n'
    #
    #         # Create a character level parser and build a transformers prefix function from it
    #         parser = JsonSchemaParser(AnswerFormat.schema())
    #         prefix_function = build_transformers_prefix_allowed_tokens_fn(hf_pipeline.tokenizer, parser)
    #
    #         # Call the pipeline with the prefix function
    #         output_dict = hf_pipeline(prompt, prefix_allowed_tokens_fn=prefix_function)
    #
    #         # Extract the results
    #         result = output_dict[0]['generated_text'][len(prompt):]
    #         print(result)
    #         # {'first_name': 'Michael', 'last_name': 'Jordan', 'year_of_birth': 1963, 'num_seasons_in_nba'
    #
    #
    #     """
    #     from lmformatenforcer import CharacterLevelParser, LMFormatEnforcer, JsonSchemaParser
    #     from openai import OpenAI
    #     if json_schema is None:
    #         json_schema = {
    #             "type": "object",
    #             "properties": {
    #                 "name": {"type": "string"},
    #                 "age": {"type": "integer"}
    #             },
    #             "required": ["name", "age"]
    #         }
    #
    #     parser = JsonSchemaParser(json_schema)
    #     enforcer = LMFormatEnforcer(parser)
    #     response = self.client.chat.completions.create(
    #         model=self.modelid,
    #         messages=[{"role": "user", "content": prompt}],
    #         temperature=self.temperature,
    #         max_tokens=self.max_tokens,
    #         format_enforcer=enforcer
    #     )
    #     dd = response.model_dump()
    #     return dd












#########################################################################
#######  Custom Prompt build signature and specify  PROMPT input and output details in docstrings and description
class Dspy_QuestionGeneratorPrompt(dspy.Signature):
    """You are a helpful assistant. Given  following document,
       generate a list of synthetic questions that could be answered by referring to  information provided in  document.
       Ensure that  questions are clear, concise, and that their answers can be directly inferred from  document text.
    """
    document = dspy.InputField(desc="a document to generate queries from")
    queries = dspy.OutputField(desc="list of 10 queries separated by '@@'.")


#########################################################################################
###### Prompt Search/Egnineering  ########################################################
def test_dpsy_optimization(dirstorage="ztmp/bench/ag_news/query/prompt_hist.csv"):
    ### DSPy
    dspy_init(model_name="gpt-3.5-turbo")
    question_generator = Dspy_Optimizer(sep="あ",
                                        dspy_promptclass_name="Dspy_QuestionGeneratorPrompt")
    template = question_generator.get_prompt_template()
    assert len(template) > 0


def prompt_find_best(cfg=None, cfg_name="prompt_optim_v1",
                     dirdata: str = "./ztmp/bench/norm/", dataset: str = "ag_news",
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

    log("#######  Config Load  ###############################")
    cfg0 = config_load(cfg)
    cfg0 = cfg0.get(cfg_name, {})

    cc = Box({})
    cc.name = "prompt_find_best"
    cc.description = "prompt find best using DSPY"
    cc.uri_code = "llm.py::prompt_find_best"
    cc.model_id = "gpt-3.5-turbo"
    cc.dspy_optimizer_name = "Dspy_Optimizer"
    cc.dspy_taskname = "synthetic_query_generation"

    cc.cfg_name = cfg_name
    cc.dirdata = dirdata
    cc.dataset = dataset
    cc.dirout = dirout

    dt = date_now(fmt="%Y%m%d/%H%M%S", returnval="str")
    dirout2 = f"{dirout}/{dt}"
    dirout_model = f"{dirout2}/query_model"
    dirout_query = f"{dirout2}/out/df_synthetic_query.csv"

    cc = exp_config_override(cfg0, cc)  #### Overrride

    log("#######  Create DSPy optimizer ######################################")
    dspy_init(model_name=cc.model_id)

    # from utilmy import load_function_uri
    # Dspy_Optimizer = load_function_uri(cc.dspy_optimizer_name)
    # q_model = Dspy_QuestionGeneratorOptimizer()
    q_model = Dspy_Optimizer()
    os_makedirs(dirout2)
    q_model.save(dirout_model)

    log("#######  Load Data  ################################################")
    dirdata2 = f"{dirdata}/{dataset}/*/df*.parquet"  #### ag_news/train/df.parquet
    df = pd_read_file(dirdata2, nfile=nfile)  ##  Real Dataset
    assert df[["id", "body"]].shape
    # filter out rows with body length < 100 words
    df["len"] = df["body"].apply(lambda x: len(x.split()))
    df = df[df["len"] > 100]
    nquery = min(nquery, len(df))
    df_query = df.sample(nquery)

    log("#######  Generate synthetic queries using DPSy #####################")  #
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
    ### {document} is defined when we define  DPSy Dspy_QuestionGeneratorPrompt class. 
    prompt_template = q_model.get_prompt_template()
    prompt_actual = prompt_template.replace("{document}", " This an example of document ")

    pstore = PromptStorage()  ### prompts/prompt_hist.csv
    pstore.append(model_id=cc.model_id,
                  task_name=cc.dspy_task_name,
                  prompt_examples=[prompt_actual],
                  prompt_args={"document": ("str", "reference text where  question is generated from")},
                  prompt_template=prompt_template)

    json_save(dict(cc), f"{dirout2}/cc.json")

    # Debug print last llm query/output, for debugging purposes
    turbo.inspect_history(n=1)


def dspy_init(model_name="gpt-3.5-turbo"):
    global turbo
    # initialize dspy module
    # model_name = "gpt-4"
    turbo = dspy.OpenAI(model=model_name)
    dspy.settings.configure(lm=turbo)


class Dspy_Optimizer(dspy.Module):
    def __init__(self, sep="あ", dspy_promptclass_name="Dspy_QuestionGeneratorPrompt"):
        """ Prompt Optimizer
        Args:
            sep (str, optional): The separator to use. Defaults to "あ".
            dspy_promptclass_name (str, optional): The name of the prompt class to use. Defaults to "Dspy_QuestionGeneratorPrompt".

        """
        super().__init__()

        try:
            from utilmy import load_function_uri
            Dspy_Prompt = load_function_uri(dspy_promptclass_name)
        except Exception as e:
            log_error(e)
            Dspy_Prompt = Dspy_QuestionGeneratorPrompt

        self.generate_answer = dspy.Predict(Dspy_Prompt)
        self.sep = sep

    def forward(self, doc: str):
        prediction = self.generate_answer(document=doc)
        if self.sep not in prediction.queries:
            queries = prediction.queries.split("\n")
            # remove numbered prefix from queries
            # queries = [q.split(". ")[1] for q in queries]
            prediction.queries = self.sep.join(queries)

        # queries = prediction.queries.split("")
        return dspy.Prediction(document=doc, answer=prediction.queries)

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


class PromptStorage:
    def __init__(self, dirstorage: str = None,
                 sep="あ",  ### Using unicode Japanese character....
                 sep_prompt="う"):  ### Using Unicode Japanese character....
        """Initializes a new instance of `PromptStorage` class.

        Args:
            dirstorage (str, optional): path to storage file. Defaults to None.
            sep (str, optional): separator character used in storage file. Defaults to "あ".
            sep_prompt (str, optional): separator character used in prompts. Defaults to "う".

        """
        self.df = None
        ### Fixes column names
        self.cols = ["prompt_id",  ### Unique ID for each prompt
                     "prompt_tags",  ### List of tags :  "questionNews, GPT4test" for easy search 
                     "prompt_template", "prompt_examples", "prompt_args",
                     "prompt_origin", "task_name",
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
            str:  generated prompt ID in  format "YYYYMMDD-HMS-random_number".
        """
        ymd = date_now(fmt="%Y%m%d-%H%M%S")
        prompt_id = f"{ymd}-{random.randint(10, 99)}"
        return prompt_id

    def load(self):
        """Load from dirstorage
        """
        if not os.path.exists(self.dirstorage):
            self.df = pd.DataFrame(columns=self.cols)
            return
        self.df = pd_read_file(self.dirstorage, sep=self.sep, engine="python")
        assert self.df[self.cols].shape

    def append(self, prompt_template, model_id, prompt_args, prompt_examples="",
               task_name="", info_json=""):
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

    def get_prompt(self, prompt_id: str = None, prompt_tags: str = None) -> dict:
        """Retrieves a prompt from `PromptStorage` based on provided `prompt_id` or `prompt_tags`.

            Args:
                prompt_id (str, optional): ID of prompt to retrieve. Defaults to None.
                prompt_tags (str, optional): A comma-separated string of tags to filter prompts by. Defaults to None.

            Returns:
                dict: A dictionary containing retrieved prompt information. 

            Example:
                >>> prompt_storage = PromptStorage()
                >>> prompt_storage.get_prompt(prompt_id="123")
                {'prompt_id': '123', 'prompt_tags': ['tag1', 'tag2'], 'prompt_template': 'Template for Prompt 123'}

                >>> prompt_storage.get_prompt(prompt_tags="tag1,tag3")
                [{'prompt_id': '456', 'prompt_tags': ['tag1', 'tag3'], 'prompt_template': 'Template for Prompt 456'},
                    {'prompt_id': '789', 'prompt_tags': ['tag1', 'tag4'], 'prompt_template': 'Template for Prompt 789'}]
        """

        if isinstance(prompt_id, str):
            dfi = self.df[self.df["prompt_id"] == prompt_id]
            ddict = dfi.to_dict(orient="records")[0]
            return ddict

        elif prompt_tags is not None:
            prompt_tags = prompt_tags if isinstance(prompt_tags, list) else prompt_tags.split(",")
            dfiall = pd.DataFrame()
            for tag in prompt_tags:
                dfi = self.df[self.df["prompt_tags"].str.contains(tag)]
                dfiall = pd.concat((dfiall, dfi))

            log(dfiall[["prompt_id", "prompt_tags", "prompt_template"]])
            return dfiall.to_dict(orient="records")


#########################################################################################
###  Inference: query LLM  ##############################################################
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


##### prompt Tooling ################
def prompt_compress(text: str) -> str:
    """ Prompt Compression for long text

       ### Usage
         pip install git+https://github.com/microsoft/autogen.git@main  --no-cache
         pip install "llmlingua<0.3"   ### Long context

         python rag/query.py prompt_compress --text "write a long poem with many words."

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
             # Download PDF
             response = requests.get(AUTOGEN_PAPER)
             response.raise_for_status()  # Ensure download was successful

             text = ""
             # Save PDF to a temporary file
             with tempfile.TemporaryDirectory() as temp_dir:
                 with open(temp_dir + "temp.pdf", "wb") as f:
                     f.write(response.content)

                 # Open PDF
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


########################################################################################
########## Custom Examples for question generation by LLM  #############################
def zex_generate_question(dirdata: str = "./ztmp/data/cats/agnews/train/",
                          dirout: str = "ztmp/bench",
                          prompt_id: str = "",
                          nfile: int = 1, nquery: int = 1,
                          subsample=1):
    """Generate synthetic queries via LLM

      python query.py generate_question --dataset "ag_news" --nfile 1 --nquery 1
      
    """
    global turbo

    #### Export path of  synthetic queries
    dt = date_now(fmt="%Y%m%d_%H%M%S", returnval="str")
    dirout2 = f"{dirout}/df_synthetic_questions_{dt}.parquet"

    log("####### Load Reference answer data as Context for LLM  ")
    df_context = zex_generate_question_loadata(dirdata=dirdata, nfile=nfile, nrows=nquery, subsample=1)

    log("####### Load Custom Post-processor ")
    llm_output_cleaner_fun = zex_generate_question_llmcleaner

    #########################################################################################
    log("#######  Load prompt template from storage")
    prompt0 = PromptStorage()  ### using ENV variables prompt_dirstorage = "prompts/prompt_hist.csv"
    prompt_dict = prompt0.get_prompt(prompt_id=prompt_id)  ## user decide whihc om
    model_id = prompt_dict.get("model_id", "gpt-3.5-turbo")

    log("###### Generate Synthetic questions from answer ")
    queries = []
    for i, row in df_context.iterrows():
        prompt_values = {"document": row["body"]}
        # print(prompt_values)
        prompt_actual = prompt_create_actual(prompt_dict["prompt_template"], prompt_values)
        answer = llm_get_answer(prompt=prompt_actual, model=model_id)

        # answer =  llm_output_clean_custom_v1(answer)
        # queries = answer.split(sep="@@")
        query = llm_output_cleaner_fun(answer)
        queries.append(query)

    df_context["query"] = queries
    df_context = df_context[["id", "title", "body", "query"]]
    # explode df_query based on query list
    df_context = df_context.explode("query")

    pd_to_file(df_context, f"{dirout2}", show=1)


####### Custom  ##############################################################################
def zex_generate_question_loadata(dirdata: str = "./ztmp/data/cats/agnews/train/",
                                  nfile=1, nrows=1000, subsample=1):
    log("###### Load Reference answer data  ")
    # diranswer = f"{dirdata}/agnews/train/df*.parquet"
    df = pd_read_file(dirdata, nfile=nfile)  ##  Real Dataset

    log("###### Data : Filter out rows with body length < 100 words")
    df["len"] = df["body"].apply(lambda x: len(x.split()))
    df = df[df["len"] > 100]
    log(df.shape)
    nquery = min(nrows, len(df))
    df_context = df.sample(nquery) if subsample > 0 else df
    log(df_context)

    return df_context


def zex_generate_question_llmcleaner(query: str, sep="@@"):
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


##########################################################################################
if __name__ == '__main__':
    fire.Fire()

"""





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
            [ " You are and assistant.  Query is Who is presndient.  side info is  my side cc.  ", ... ]

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
                cc.json  : meta data about  results.
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

{
    "id": "chatcmpl-9k9MR8TtV301n6xAzfbxWM2liX2dV",
    "choices": [
        {
            "finish_reason": "length",
            "index": 0,
            "logprobs": [{"content": {}}],
            "message": {
                "content": "Sachin Tendulkar is a former Indian cricketer who is widely regarded as one of the greatest batsmen in the history of the",
                "role": "assistant"}
        }
    ],
    "created": 1720786099,
    "model": "gpt-3.5-turbo-0125",
    "object": "chat.completion",
    "system_fingerprint": None,
    "usage": {
        "completion_tokens": 30,
        "prompt_tokens": 16,
        "total_tokens": 46,
        "prompt": "Tell me about Sachin Tendulkar"
    }
}
