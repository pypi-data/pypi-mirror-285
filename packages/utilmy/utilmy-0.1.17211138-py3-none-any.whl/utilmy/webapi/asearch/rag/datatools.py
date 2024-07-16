# -*- coding: utf-8 -*-
"""
#### Install
    pip install -r pip/py39_full.txt
    pip install fastembed==0.2.6 loguru --no-deps
    
    pip install llama-index
    pip install pyarrow


#### ENV variables
    export HF=
    export
    export torch_device='cpu'
    #### Test

        python  engine.py test_qdrant_dense
        python  engine.py test_qdrant_sparse
        python engine.py test_tantivy



#### Text chunking methods:
   https://docs.llamaindex.ai/en/stable/examples/node_parsers/semantic_chunking/?h=chunk


#### Dataset

    https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail

    https://zenn.dev/kun432/scraps/1356729a3608d6


    https://huggingface.co/datasets/big_patent


    https://huggingface.co/datasets/ag_news



#### Semantic Chunking

   Semantic Chunking considers relationships within text. It divides text into meaningful, semantically complete chunks. This approach ensures information's integrity during retrieval, leading to a more accurate and contextually appropriate outcome.
   Semantic chunking involves taking embeddings of every sentence in document, comparing similarity of all sentences with each other, and then grouping sentences with most similar embeddings together.
   By focusing on text's meaning and context, Semantic Chunking significantly enhances quality of retrieval. It's a top-notch choice when maintaining semantic integrity of text is vital.
   However, this method does require more effort and is notably slower than previous ones.
   On our example text, since it is quite short and does not expose varied subjects, this method would only generate a single chunk.

   https://www.sagacify.com/news/a-guide-to-chunking-strategies-for-retrieval-augmented-generation-rag

"""
import warnings
warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from box import Box  ## use dot notation as pseudo class
import pandas as pd, numpy as np, torch
from fastembed import TextEmbedding
import datasets
from utilmy import pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob
from utilmy import log, log2



#### Chunking methods
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

# from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding




############ Internals #################################################################
from rag.dataprep import (
    dataset_hf_to_parquet,
    dataset_kaggle_to_parquet,
    dataset_agnews_schema_v1,
    pd_to_file_split,
    pd_fake_data,
    pd_fake_data_batch,
)



######################################################################################
def test3():
    ### python engine2.py test_all

    # for testing chunking of dataframe:
    test_df = pd_fake_data()
    result = pd_create_chunk(test_df)
    print(result.head())


######################################################################################
def chunkfun_llama(each_row_text):
    doc_text = [Document(text = each_row_text)]

    splitter = SentenceSplitter(chunk_size=100, chunk_overlap=10,)
    chunks = splitter.get_nodes_from_documents(doc_text)

    return chunks


def pd_create_chunk(df, method="semantic", chunk_name="chunkfun_llama"):

    cols= ["id", "chunk_method", "chunk_text_list"]

    chunk_fun = globals()[chunk_name] 
    df["chunk_text_list"] = df["text"].apply(lambda x: chunk_fun(x))   
    
    df["chunk_method"] = chunk_name

    return df[cols]




def pd_create_chunk_old(df, method="semantic"):
    chunk_series = df["text"].apply(lambda x: chunkfun_llama(x))   

    result_list = []
    for each_row in range(0, len(chunk_series)):
        for each_chunk in chunk_series[each_row]:
            new_row = [each_row, each_chunk.id_, method, each_chunk.text]
            result_list.append(new_row)
    
    output_df = pd.DataFrame(result_list, columns=["id", "chunk_id", "chunk_method", "text_chunk"])
    return output_df



#############################################################################
def test3():
    df = pd_fake_data_batch(100)
    selected_df = df[["id_global", "body"]]      ## Input format which you provided ||| input : df[["id", "text"]]  |||  
    output_df = split_text_and_create_df(selected_df)
    print(output_df)    ## output would be ||| id, chunkid, chunk_method, body_text, chunk_cat1, chunk_cat1, chunk_cat1 |||
    ## "body text" which got divided into multiple chunks will get store into chunk_cat1, chunk_cat2, and so on" depends upon chun_size and body text length.


def split_text_and_create_df(df):
    from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

    char_text_splitter = CharacterTextSplitter(
        chunk_size=50, chunk_overlap=20, length_function=len, is_separator_regex=False,
    )
    recur_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=50, chunk_overlap=20, length_function=len, is_separator_regex=False,
    )

    character_splitter_output = []
    recursive_character_splitter_output = []

    for idx, row in df.iterrows():
        id_val = row[df.columns[0]]
        body_text = row[df.columns[1]]

        chunks = char_text_splitter.split_text(body_text)
        for i, chunk in enumerate(chunks):
            character_splitter_output.append({
                'id': id_val,
                'chunk_id': i,
                'chunk_method': 'CharacterTextSplitter',
                'body': chunk,
                'chunk_cat1': chunk,
                'chunk_cat2': None,
                'chunk_cat3': None
            })

        chunks = recur_text_splitter.split_text(body_text)
        for i, chunk in enumerate(chunks):
            recursive_character_splitter_output.append({
                'id': id_val,
                'chunk_id': i,
                'chunk_method': 'RecursiveCharacterTextSplitter',
                'body': chunk,
                'chunk_cat1': chunk,
                'chunk_cat2': None,
                'chunk_cat3': None
            })

    character_splitter_df = pd.DataFrame(character_splitter_output)
    recursive_character_splitter_df = pd.DataFrame(recursive_character_splitter_output)

    output_df = pd.concat([character_splitter_df, recursive_character_splitter_df], ignore_index=True)   

    return output_df








###################################################################################
def test1():
    text = "Now is winter of our discontent ....(text files)"
    character_splitter, recursive_character_splitter = use_character_text_splitters(text)
    print(character_splitter[0])
    print(recursive_character_splitter[0])

    semantic_nodes = use_semantic_splitter("/content/Jiten Bhalavat-Resume.pdf")
    print(semantic_nodes[0].text)

    sentence_nodes1, sentence_nodes2 = use_sentence_splitters("/content/Jiten Bhalavat-Resume.pdf")

    os.environ["OPENAI_API_KEY"] = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def use_character_text_splitters(text):
    char_text_splitter = CharacterTextSplitter(
        separator=" ", chunk_size=100, chunk_overlap=50, length_function=len, is_separator_regex=False
    )
    recur_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100, chunk_overlap=20, length_function=len, is_separator_regex=False
    )

    character_splitter = char_text_splitter.create_documents([text])
    recursive_character_splitter = recur_text_splitter.create_documents([text])

    return character_splitter, recursive_character_splitter


def use_semantic_splitter(file_path):
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    embed_model = OpenAIEmbedding()
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )
    nodes = splitter.get_nodes_from_documents(documents)

    return nodes

def use_sentence_splitters(file_path):
    from llama_index.llms.openai import OpenAI
    from llama_index.core.node_parser import SentenceWindowNodeParser

    llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()

    node_parser2 = SentenceWindowNodeParser.from_defaults(
        window_size=3, window_metadata_key="window", original_text_metadata_key="original_text"
    )
    nodes2 = node_parser2.get_nodes_from_documents(documents)

    node_parser1 = SentenceSplitter(chunk_size=500, chunk_overlap=100)
    nodes1 = node_parser1.get_nodes_from_documents(documents)

    return nodes1, nodes2





###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


