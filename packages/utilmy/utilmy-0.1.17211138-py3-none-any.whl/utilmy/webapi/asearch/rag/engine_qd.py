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

            python  rag/engine_kg.py test_qdrant_dense
            python  rag/engine_kg.py test_qdrant_sparse


    #### Benchmarks:
            sudo docker run -d -p 6333:6333     -v ~/.watchtower/qdrant_storage:/qdrant/storage:z     qdrant/qdrant
            alias py2="python rag/engine_kg.py "

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
import warnings
warnings.filterwarnings("ignore")
import os, pathlib, uuid, time, traceback, pandas as pd, numpy as np, torch
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
from box import Box  ## use dot notation as pseudo class


from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct

from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

from utilmy import (pd_read_file, os_makedirs, pd_to_file, date_now, glob_glob)
from utilmy import log, log2

########## Local import
from rag.dataprep import (pd_fake_data, )



######################################################################################
def test_all():
    ### python engine2.py test_all
    test_qdrant_dense()
    test_qdrant_sparse()


def test_qdrant_dense(nrows=20):
    """
    python rag/engine_kg.py test_qdrant_dense_create_index    
    """
    dirtmp = "ztmp/df_test.parquet"
    test_df = pd_fake_data(nrows=nrows, dirout=dirtmp, overwrite=False)

    model_type = "stransformers"
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    server_url = ":memory:"  ### "http://localhost:6333"
    collection_name = "my-documents"

    client = QdrantClient(server_url)

    qdrant_dense_create_index(
        dirin=dirtmp,
        server_url=server_url,
        collection_name=collection_name,
        coltext="text",
        model_id=model_id,
        model_type=model_type,
        client=client
    )
    model = EmbeddingModel(model_id, model_type)

    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]
    results = qdrant_dense_search(
        query,
        server_url=server_url,
        collection_name=collection_name,
        model=model,
        client=client
        # category_filter={"categories": "Fiction"},
    )
    results = [
        ((scored_point.payload), scored_point.score)
        for scored_point in results
        if scored_point.score > 0
    ]
    log(f"len(results):{len(results)}")
    assert len(results) > 0


def test_qdrant_sparse(nrows=30):
    """test function for sparse qdrant indexing"""
    dirtmp = "ztmp/df_test.parquet"
    test_df = pd_fake_data(nrows=nrows, dirout=dirtmp, overwrite=False)

    model_id = "naver/efficient-splade-VI-BT-large-doc"
    model_type = "stransformers"
    server_url = ":memory:"  ### "http://localhost:6333"
    collection_name = "my-documents"

    client = QdrantClient(server_url)

    qdrant_sparse_create_index(
        dirin=dirtmp,
        collection_name="my-sparse-documents",
        model_id=model_id,
        client=client
    )
    # pick random query from test dataframe
    query = test_df.sample(1)["text"].values[0]

    model = EmbeddingModelSparse(model_id)
    results = qdrant_sparse_search(
        query,
        # category_filter={"categories": "Fiction"},
        collection_name="my-sparse-documents",
        model=model,
        client=client
    )

    results = [
        ((scored_point.payload), scored_point.score)
        for scored_point in results
        if scored_point.score > 0
    ]
    # print(results)
    log(f"len(results):{len(results)}")
    assert len(results) > 0




#####################################################################################
########## Dense Vector creation
class EmbeddingModel:
    def __init__(self, model_id, model_type, device: str = "", embed_size: int = 128):
        self.model_id = model_id
        self.model_type = model_type

        from utils.utils_base import torch_getdevice
        self.device = torch_getdevice(device)

        if model_type == "stransformers":
            self.model = SentenceTransformer(model_id, device=self.device)
            self.model_size = self.model.get_sentence_embedding_dimension()

        elif model_type == "fastembed":
            self.model = TextEmbedding(model_name=model_id, max_length=embed_size)
            self.model_size = self.model.get_embedding_size()

        else:
            raise ValueError(f"Invalid model type: {model_type}")

    def embed(self, texts: List):
        if self.model_type == "stransformers":
            vectors = list(self.model.encode(texts))
        elif self.model_type == "fastembed":
            vectors = list(self.model.embed(texts))
        return vectors


class EmbeddingModelSparse:
    def __init__(self, model_id: str = "", max_length: int = 512):
        """ """
        # Initialize tokenizer and model
        from utils.utils_base import torch_getdevice
        self.device = torch_getdevice()
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForMaskedLM.from_pretrained(
            model_id, device_map=self.device
        )

    def embed(self, texts):
        # Tokenize all texts
        if isinstance(texts, np.ndarray):
            # convert to list
            texts = texts.tolist()
        tokens_batch = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length,
        )
        # Forward pass through  model
        tokens_batch.to(device=self.device)
        with torch.no_grad():
            output = self.model(**tokens_batch)

        # Extract logits and attention mask
        logits = output.logits
        attention_mask = tokens_batch["attention_mask"]

        # ReLU and weighting
        relu_log = torch.log(1 + torch.relu(logits))
        weighted_log = relu_log * attention_mask.unsqueeze(-1)

        # Compute max values
        max_vals, _ = torch.max(weighted_log, dim=1)
        # log(f"max_vals.shape: {max_vals.shape}")

        # for each tensor in  batch, get  indices of  non-zero elements
        indices_list = [torch.nonzero(tensor, as_tuple=False) for tensor in max_vals]
        indices_list = [
            indices.cpu().numpy().flatten().tolist() for indices in indices_list
        ]
        # for each tensor in  batch, get  values of  non-zero elements
        values = [
            max_vals[i][indices].cpu().numpy().tolist()
            for i, indices in enumerate(indices_list)
        ]

        return list(zip(indices_list, values))

    def decode_embedding(self, cols: list, weights) -> dict:
        """Decodes embedding from indices and values."""
        # Map indices to tokens and create a dictionary
        idx2token = {idx: token for token, idx in self.tokenizer.get_vocab().items()}
        token_weight_dict = {
            idx2token[idx]: round(weight, 2) for idx, weight in zip(cols, weights)
        }

        # Sort  dictionary by weights in descending order
        sorted_token_weight_dict = {
            k: v
            for k, v in sorted(
                token_weight_dict.items(), key=lambda item: item[1], reverse=True
            )
        }

        return sorted_token_weight_dict



#####################################################################################
########## Qdrant Dense Vector Indexing
def qdrant_collection_exists(qclient, collection_name):
    collections = qclient.get_collections()
    collections = {coll.name for coll in collections.collections}
    return collection_name in collections


def qdrant_dense_create_collection(
        qclient, collection_name="documents", size: int = None
):
    """
    Create a collection in qdrant
    :param qclient: qdrant client
    :param collection_name: name of  collection
    :param size: size of  vector
    :return: collection_name
    """
    if not qdrant_collection_exists(qclient, collection_name):
        qclient.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=size, distance=models.Distance.COSINE
            ),
        )
        log(f"created collection:{collection_name}")
    return collection_name


def qdrant_dense_index_documents(
        qclient,
        collection_name: str,
        df: pd.DataFrame,
        colscat: List = None,  ## list of categories field
) -> None:
    """Indexes documents from a pandas DataFrame into a qdrant collection.
    Args:
        qclient:  qdrant client.
        collection_name:  name of  collection.
        df:  DataFrame containing  documents.
        colscat: list of fields to be indexed

    """
    colscat = (
        [ci for ci in df.columns if ci not in ["vector"]]
        if colscat is None
        else colscat
    )

    assert df[["text_id", "vector"]].shape
    # log(df)

    # Convert documents to points for insertion into qdrant.
    points = [
        PointStruct(
            id=row["text_id"],  # Use existing id if available, else generate new one.
            vector=row["vector"].tolist(),  # Numpy ---> List, Vector of  document.
            payload={ci: row[ci] for ci in colscat},  ### Category filtering values
        )
        for i, row in df.iterrows()
    ]

    vector_size = len(points[0].vector)  # Get  size of  vectors.

    # Create collection if not existing.
    qdrant_dense_create_collection(
        qclient, collection_name=collection_name, size=vector_size)

    # Index documents.
    qclient.upsert(collection_name=collection_name, points=points)
    log("qdrant upsert done: ", collection_name, qclient.count(collection_name), )


def qdrant_dense_create_index(
        dirin: str,
        server_url: str = ":memory:",
        collection_name: str = "my-documents",
        colscat: List = None,  ## list of categories field
        coltext: str = "text",
        model_id=None,
        model_type=None,
        batch_size=100,
        client=None
) -> None:
    """Create a qdrant index from a parquet file.

    dirin: str: path to  parquet file
    server_url: str: url path to  qdrant server
    coltext: str: column name of  text column
    model_id: str: name of  embedding model to use
    model_type: str: type of  embedding model
    batch_size: int: batch size for embedding vectors
    (ID_k, text_k)

    """
    # df = pd_read_file(path_glob=dirin, verbose=True)
    flist = glob_glob(dirin)
    log("Nfiles: ", len(flist))

    ##### Load model
    model = EmbeddingModel(model_id, model_type)
    client = QdrantClient(server_url) if client is None else client
    qdrant_dense_create_collection(client, collection_name, size=model.model_size)
    for i, fi in enumerate(flist):
        dfi = pd_read_file(fi)

        ### Create embedding vectors batchwise
        kmax = int(len(dfi) // batch_size) + 1
        for k in range(0, kmax):
            dfk = dfi.iloc[k * batch_size: (k + 1) * batch_size, :]
            if len(dfk) <= 0:
                break
            # get document vectors
            dfk["vector"] = model.embed(dfk[coltext].values)

            # insert documents into qdrant
            assert dfk[["text_id", "vector"]].shape
            qdrant_dense_index_documents(
                client, collection_name, colscat=colscat, df=dfk
            )


def qdrant_dense_search(query,
                        topk: int = 20,
                        category_filter: dict = None,
                        server_url: str = "",
                        collection_name: str = "my-documents",
                        model: EmbeddingModel = None,
                        client=None,
                        model_type_default="stransformers",
                        model_id_default="sentence-transformers/all-MiniLM-L6-v2"  ### 384,  50 Mb
                        ) -> List:
    """
    Search a qdrant index
    query: str: query to search
    server_url: str: url path to  qdrant server
    collection_name: str: name of  collection to search
    model_id: str: name of  embedding model to use

    Main issue with Category iS :

       How do we know the category in advance ?
          1)  User provide them.
          2)  We can guess easily by simple rules.
          3)  Train a BERT model to category the query.
          4)  New Qdrant way : Self Learning : using LLM to get the categories
          
              Category : Hard Filtering.            
              Embedding: soft fitlering ()

            
              3 query similarity query : retrieval, you dont missg
                  Cat News A, one with Cat News B, one with Cat news C   

               Final results: 30% of A, 30% of B, 30% of C
               
          Async launch of comppute; 
          
          wait      

# query filter
hits = client.search(
    collection_name="wine_reviews",
    query_vector=encoder.encode("Night Sky").tolist(),
    query_filter=models.Filter(
        must=[
            models.FieldCondition(key="metadata.country", match=models.MatchValue(value="US")),
            models.FieldCondition(key="metadata.price", range=models.Range(gte=15.0, lte=30.0)), 
            models.FieldCondition(key="metadata.points", range=models.Range(gte=90, lte=100))
        ]
    ),
    limit=3,
)

for hit in hits:
    print(hit.payload['metadata']['title'], "\nprice:", hit.payload['metadata']['price'], "\npoints:", hit.payload['metadata']['points'], "\n\n")               
               
               
    Schema
         title, text ,  cat1, cat2, cat2
          ("cat2name" : "myval"  )

    """
    if server_url == "":
        server_url = os.environ.get("QDRANT_URL", ":memory:")

    client = QdrantClient(server_url) if client is None else client

    model = EmbeddingModel(model_id_default, model_type_default) if model is None else model
    query_vector: list = model.embed([query])
    query_filter = qdrant_query_createfilter(category_filter)

    # log(client.count(collection_name))
    result: list = client.search(
        collection_name=collection_name,
        query_vector=query_vector[0],
        query_filter=query_filter,
        limit=topk
    )
    # log([scored_point.payload["categories"] for scored_point in search_result])
    # log(f"#search_results:{len(search_result)}")
    return result


def qdrant_query_createfilter(
        category_filter: Dict = None,
) -> Union[None, models.Filter]:
    """Create a query filter for Qdrant based on  given category filter.
    Args:
        category_filter (Dict[str, Any]): A dictionary representing  category filter.     : None.

    Returns:
        Union[None, models.Filter]:  query filter created based on  category filter, or None if  category filter is None.
    """
    query_filter = None
    if category_filter:
        catfilter = []
        for catname, catval in category_filter.items():
            xi = models.FieldCondition(
                key=catname, match=models.MatchValue(value=catval)
            )
            catfilter.append(xi)
        query_filter = models.Filter(should=catfilter)
    return query_filter



####################################################################################
######### Qdrant Sparse Vector Engine :
def qdrant_sparse_create_collection(
        qclient, collection_name="documents", size: int = None
):
    """Create a collection in qdrant
    :param qclient: qdrant client
    :param collection_name: name of  collection
    :param size: size of  vector
    :return: collection_name
    """
    if not qdrant_collection_exists(qclient, collection_name):
        vectors_cfg = {}  # left blank in case of sparse indexing
        sparse_vectors_cfg = {
            "text": models.SparseVectorParams(
                index=models.SparseIndexParams(
                    on_disk=True,
                )
            )
        }
        qclient.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_cfg,
            sparse_vectors_config=sparse_vectors_cfg,
        )
        log(f"created sparse collection:{collection_name}")
    return collection_name


def qdrant_sparse_index_documents(
        qclient, collection_name, df: pd.DataFrame, colscat: list = None
):
    # covert documents to points for insertion into qdrant

    colscat = (
        [ci for ci in df.columns if ci not in ["vector"]]
        if colscat is None
        else colscat
    )
    points = [
        models.PointStruct(
            id=doc["text_id"],
            payload={key: doc[key] for key in colscat},
            # Add any additional payload if necessary
            vector={
                "text": models.SparseVector(indices=doc.vector[0], values=doc.vector[1])
            },
        )
        for i, doc in df.iterrows()
    ]

    # Create collection if not existing
    # qdrant_sparse_create_collection(qclient, collection_name=collection_name)
    # Index documents
    try:
        qclient.upsert(collection_name=collection_name, points=points)
    except Exception as err:
        print(traceback.format_exc())


def qdrant_sparse_create_index(
        dirin: str,
        server_url: str = ":memory:",
        collection_name: str = "my-sparse-documents",
        colscat: list = None,
        coltext: str = "text",
        model_id: str = "naver/efficient-splade-VI-BT-large-doc",
        batch_size: int = 5,
        client=None,
) -> None:
    """
    Create a qdrant sparse index from a parquet file
    dirin: str: path to  parquet file
    server_url: str: url path to  qdrant server
    coltext: str: column name of  text column
    model_id: str: name of  sparse embedding model to use
    """
    flist = glob_glob(dirin)
    log("Nfiles: ", len(flist))

    ##### Load model
    model = EmbeddingModelSparse(model_id)
    client = QdrantClient(server_url) if client is None else client
    qdrant_sparse_create_collection(client, collection_name)
    for i, fi in enumerate(flist):
        dfi = pd_read_file(fi)
        ### Create embedding vectors batchwise
        kmax = int(len(dfi) // batch_size) + 1
        for k in range(0, kmax):
            dfk = dfi.iloc[k * batch_size: (k + 1) * batch_size, :]
            if len(dfk) <= 0:
                break
            # get document vectors
            dfk["vector"] = model.embed(dfk[coltext].values)

            # insert documents into qdrant
            assert dfk[["text_id", "vector"]].shape
            qdrant_sparse_index_documents(
                client, collection_name, colscat=colscat, df=dfk
            )


def qdrant_sparse_search(query: str,
                         category_filter: dict = None,
                         server_url: str = "",
                         collection_name: str = "my-sparse-documents",
                         model: EmbeddingModelSparse = None,
                         model_id_default: str = "naver/efficient-splade-VI-BT-large-doc",
                         topk: int = 10,
                         client=None
                         ) -> List:
    """Search a qdrant index
    query: str: query to search
    server_url: str: url path to  qdrant server
    collection_name: str: name of  collection to search
    model_id: str: name of  embedding model to use
    """
    if server_url == "":
        server_url = os.environ.get("QDRANT_URL", ":memory:")

    client = QdrantClient(server_url) if client is None else client
    model = EmbeddingModelSparse(model_id_default) if model is None else model
    result = model.embed([query])
    query_indices, query_values = result[0]

    query_dict = model.decode_embedding(query_indices, query_values)
    # log(f"query_dict:{query_dict}")

    query_filter = qdrant_query_createfilter(category_filter)

    query_vector = models.NamedSparseVector(name="text",
                                            vector=models.SparseVector(indices=query_indices, values=query_values, ),
                                            )

    # Searching for similar documents
    search_results: List = client.search(collection_name=collection_name,
                                         query_vector=query_vector,
                                         # query_filter=query_filter,
                                         with_vectors=True,
                                         limit=topk,
                                         )
    return search_results







###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()


