# -*- coding: utf-8 -*-
"""
    #### Install
        pip install -r py39.txt
        pip install fastembed==0.2.6 loguru --no-deps


    #### ENV variables
        export HF=
        export
        export torch_device='cpu'
        #### Test

            python rag/engine_tv.py test_tantivy




    #### Benchmarks:
            sudo docker run -d -p 6333:6333     -v ~/.watchtower/qdrant_storage:/qdrant/storage:z     qdrant/qdrant
            alias py2="python rag/engine_tv.py "

            py2 bench_v1_create_indexes --dirdata_root ztmp/bench/
            py2 bench_v1_run  --dirout ztmp/bench/   --topk 5


            ### Bench
            tantivy : v1  6ms
            Sparse :      23ms
            Dense:        30 ms
            
            ag_news index timings:
            records: 127600
            dense stransformers vectors: 9m28s
            dense fastembed vectors:
            sparse vectors: 9819/12760


    #### Dataset
        https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail


        https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail

        https://zenn.dev/kun432/scraps/1356729a3608d6


        https://huggingface.co/datasets/big_patent


        https://huggingface.co/datasets/ag_news


    #### Flow
        HFace Or Kaggle --> dataset in RAM--> parquet (ie same columns)  -->  parquet new columns (final)


        Custom per text data
        title  :   text
        text   :    text
        cat1   :    string   fiction / sport /  politics
        cat2   :    string     important / no-important
        cat3   :    string
        cat4   :    string
        cat5   :    string
        dt_ymd :    int     20240311


"""
import functools
import warnings

from engine_qd import EmbeddingModel

warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback, pandas as pd, numpy as np, torch
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from box import Box  ## use dot notation as pseudo class

import tantivy

from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForMaskedLM
from ranx import Qrels, Run, fuse

from utilmy import pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob
from utilmy import log, log2, log3, log_error, log_warning

########## Local import
from rag.dataprep import (pd_fake_data, dataset_hf_to_parquet)



######################################################################################
def test_all():
    ### python engine2.py test_all
    test_tantivy()
    test_fusion_search()


def test_tantivy(nrows=50):
    """test function for tantivy indexing"""
    dirtmp = "ztmp/df_test.parquet"
    dirindex = "ztmp/tantivy_index"
    if not os.path.exists(dirtmp):
        test_df = pd_fake_data(nrows=nrows, dirout=dirtmp, overwrite=False)
        pd_to_file(test_df, dirtmp)
    else:
        test_df = pd_read_file(dirtmp)

    tantivy_index_documents(
        dirin=dirtmp, datapath=dirindex, kbatch=10, colsused=["title", "text"]
    )
    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]

    query = query.replace("\n", " ")
    results = tantivy_search(query=query, datapath=dirindex)
    log(f"len(results):{len(results)}")
    assert len(results) > 0


def test_fusion_search():
    """test function for fusion search"""

    from rag.engine_qd import QdrantClient, qdrant_sparse_search, qdrant_sparse_create_index
    # get results from qdrant sparse search
    dirtmp = "ztmp/df_test.parquet"
    test_df = pd_read_file(dirtmp)
    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]
    query = query.replace("\n", " ")

    server_url = ":memory:"
    # index in memory data for later retrieval
    client = QdrantClient(server_url)
    qdrant_sparse_create_index(dirin=dirtmp, client=client)
    v1_results = qdrant_sparse_search(query, client=client)
    v1 = fusion_postprocess_qdrant(v1_results)
    # collect ids from  results
    v1_ids = list(v1.keys())


    # get results from tantivy search
    v2_results = tantivy_search(query=query)
    v2 = fusion_postprocess_tantivy(v2_results)
    # collect ids from  results
    v2_ids = list(v2.keys())

    fusion_results = fusion_search(query=query, method="rrf", client=client)


    search_ids = set(v1_ids).union(v2_ids)
    fusion_ids = set(fusion_results["q1"].keys())
    # check if  ids from  two search results are  same as ids from fusion search
    # log(f"{search_ids.difference(fusion_ids)}")
    assert search_ids.difference(fusion_ids) == set()




###################################################################################
##  Tantivy Engine ################################################################
def tantivy_index_get(datapath: str = "./ztmp/tantivy_index", schema_name: str = None):
    if schema_name is None:
        schema = tantivy_schema_get_default()
    else:
        ### Load  function to create  schema only by name string.
        from utilmy import load_function_uri

        schema_builder_fun = load_function_uri(schema_name)
        schema = schema_builder_fun()

    # create datastore
    os_makedirs(datapath)

    index_disk = tantivy.Index(schema, path=str(datapath))
    return index_disk


def tantivy_schema_get_default():
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_text_field("title", stored=True, index_option="basic")
    schema_builder.add_text_field("text", stored=True, index_option="basic")
    schema_builder.add_unsigned_field("text_id", stored=True)
    schema_builder.add_text_field("categories", stored=True, index_option="basic")
    schema_builder.add_text_field("cat1", stored=True, index_option="basic")
    schema_builder.add_text_field("cat2", stored=True, index_option="basic")
    schema_builder.add_text_field("cat3", stored=True, index_option="basic")
    schema_builder.add_text_field("cat4", stored=True, index_option="basic")
    schema_builder.add_text_field("cat5", stored=True, index_option="basic")
    schema_builder.add_text_field("fulltext", index_option="position")

    schema = schema_builder.build()
    return schema


def tantivy_index_documents(
        dirin: str,
        datapath: str = None,
        kbatch: int = 10,
        colsused=None,
        db_sep: str = " @ ",
        db_heap_size: int = 50_0000_000,
        db_max_threads: int = 1,
) -> None:
    """Indexes documents into a Tantivy index.
    Args                : 
    dirin (str)         : path containing  documents to be indexed.
    datapath (str)      : path to  Tantivy index.                         : None.
    kbatch (int)        : batch size for committing documents to  index.  : 10.
    colsused (List)     : list of columns to use for indexing.            : None.
    db_sep (str)        : separator to use for concatenating text columns.: " @ ".
    db_heap_size (int)  : heap size for  Tantivy index.                   : 50_0000_000.
    db_max_threads (int): maximum number of threads for  Tantivy index.   : 1.

    Returns:
        None
    """
    df = pd_read_file(path_glob=dirin)

    # create index schema if not already existing
    index_disk = tantivy_index_get(datapath)
    writer = index_disk.writer(heap_size=db_heap_size, num_threads=db_max_threads)

    textcols = (
        [col for col in df.columns if col not in ("text_id",)]
        if colsused is None
        else colsused
    )

    #### Insert inside  index
    for k, row in df.iterrows():
        # log(type(doc.categories))
        title = row.get("title", row["text"][:30])
        fulltext = db_sep.join(
            [str(row[col]) for col in textcols]
        )  # .title, row.text, " ".join(row.categories)])
        writer.add_document(
            tantivy.Document(
                title=title,
                text=row["text"],
                text_id=str(row["text_id"]),
                # categories=row.categories if "categories" in row else "",
                fulltext=fulltext,
            )
        )

        if k % kbatch == 0:
            log("Commit:", k)
            writer.commit()

    writer.commit()
    writer.wait_merging_threads()


def str_to_alphanum_only(txt):
    return "".join([c if c.isalnum() else " " for c in txt])


def tantivy_search(datapath: str = "./ztmp/tantivy_index", query: str = "", topk: int = 10):
    """Search a tantivy index
    datapath: str: path to  tantivy index
    query: str: query to search
    size: int: number of results to return
    :return: list of tuples (score, document) where document is a dictionary of  document fields
    """
    index = tantivy_index_get(datapath)
    # query_parser = reader.query_parser(["title", "text"], default_conjunction="AND")
    searcher = index.searcher()
    # print(f"Searching for: {query}")
    try:
        query = str_to_alphanum_only(query)
        query = index.parse_query(query, ["fulltext"])
        results = searcher.search(query, topk).hits
        # log(results)
        score_docs = [
            (score, searcher.doc(doc_address)) for score, doc_address in results
        ]
        return score_docs
    except Exception as err:
        print(traceback.format_exc())
        log(query, err)
        return []





###############################################################################
######## Fusion Rank ##########################################################
def fusion_search(query="the", engine: str = "", method="rrf", client=None,
                  sparse_collection_name="", dense_collection_name="", tantivy_datapath="", neo4j_db="",
                  sparse_model: EmbeddingModel = None, dense_model: EmbeddingModel = None) -> Dict:
    """Perform a fusion search using  given query and method.
    Args:
        query (str):  query to search for.     : "the".
        engine (str): underscore separated engines to use.
        method (str):  method to use for merging  results.     : "rrf".

    Returns:
        Dict:  merged ranking results.

     Loose Coupling and Clear/Indentify coupling  between  code components.
     "id"  columns must in  dataframe

    """
    engines = [en for en in engine.split("_") if en in ("dense", "sparse", "tantivy", "neo4j")]
    if not engines:
        engines = ("sparse", "tantivy")

    from rag.engine_qd import qdrant_sparse_search, qdrant_dense_search
    from engine_kg import neo4j_search_docids
    results = []
    for en in engines:
        if en == "sparse":
            v1_results = qdrant_sparse_search(query, client=client, collection_name=sparse_collection_name,
                                              model=sparse_model)
            result = fusion_postprocess_qdrant(v1_results, colid="text_id")
            results.append(result)
        elif en == "tantivy":
            v2_results = tantivy_search(query=query, datapath=tantivy_datapath)
            result = fusion_postprocess_tantivy(v2_results)
            results.append(result)
        elif en == "dense":
            v3_results = qdrant_dense_search(query=query, collection_name=dense_collection_name, model=dense_model)
            result = fusion_postprocess_qdrant(v3_results, colid="text_id")
            results.append(result)
        elif en == "neo4j":
            v4_results = neo4j_search_docids(query=query, db_name=neo4j_db)  # , db_name=neo4j_db)
            result = fusion_postprocess_neo4j(v4_results)
            results.append(result)

    # log(f"results:{results}")
    results = [res for res in results if len(res) > 0]
    if len(results) == 0:
        vmerge = {}
    elif len(results) == 1:
        vmerge = results[0]
    else:
        vmerge: Dict = ranx_merge_ranking(results, method=method)
    # log(f"vmerge: {vmerge}")
    return vmerge


def fusion_postprocess_qdrant(results: List, colid="id") -> Dict:
    """Postprocess  search results from a sparse qdrant search.
    Args:
        results (List):  search results.

    Returns: { doc_id: score }
    """
    v1 = {
        str(scored_point.payload[colid]): scored_point.score for scored_point in results
    }
    # log(f"v1:{v1}")
    return v1


def fusion_postprocess_tantivy(results: List, colid="id") -> Dict:
    """Postprocess  search results from a tantivy search.
    Args: results (List):  search results.

    Returns: { doc_id: score }
    """
    v2 = {str(doc.get_all(colid)[0]): score for score, doc in results}
    # log(f"v2:{v2}")
    return v2


def fusion_postprocess_neo4j(results: List, colid="text_id") -> Dict:
    """Postprocess  search results from a neo4j search.
    Args: results (List):  search results.

    Returns: { doc_id: score }
    """
    v4 = {str(doc[colid]): doc["score"] for doc in results}
    # log(f"v4:{v4}")
    return v4


def ranx_merge_ranking(vs: List, method="rrf") -> Dict:
    """Merge two rankings using  specified fusion method.

    Args:
        method (str):  fusion method to use.     : "rrf".
        v1 (Dict):  first ranking to merge.     : None.
        v2 (Dict):  second ranking to merge.     : None.

    Returns:Dict:  {'q1': {'d1': 0.5, 'd2': 0.8, 'd3': 0.3}}


    Example:
        >>> v1 = {"d1": 0.5, "d2": 0.8, "d3": 0.3}
        >>> v2 = {"d1": 0.9, "d2": 0.2, "d3": 0.7}
        >>> ranx_merge_ranking(vs=[v1,v2], method="rrf")
        {'q1': {'d1': 0.5, 'd2': 0.8, 'd3': 0.3}}
    """
    runs = [Run.from_dict({"q1": v}) for v in vs]
    # Fuse rankings using Reciprocal Rank Fusion (RRF)
    fused_run = fuse(runs, method=method)
    # log3(f"run1:{run1}")
    # log3(f"run2:{run2}")
    # log3(fused_run)
    fused_run: dict = dict(fused_run)

    #   {'q1': {'d1': 0.5, 'd2': 0.8, 'd3': 0.3}}
    return fused_run["q1"]






###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


