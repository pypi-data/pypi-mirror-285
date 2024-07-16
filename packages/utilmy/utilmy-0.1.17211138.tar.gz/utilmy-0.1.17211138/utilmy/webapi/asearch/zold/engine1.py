# -*- coding: utf-8 -*-
import os
import pathlib
import typing
import uuid
import pandas as pd
import tantivy
import torch

from qdrant_client import QdrantClient
from qdrant_client import models
from qdrant_client.http.models import PointStruct

from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForMaskedLM

from utilmy import pd_read_file


# Qdrant Dense Vector Indexing
def _create_quadrant_collection_dense(q_client, collection_name="documents", size: int = None):
    """
    Create a collection in qdrant
    :param q_client: qdrant client
    :param collection_name: name of collection
    :param size: size of vector
    :return: collection_name
    """
    collections = q_client.get_collections()
    collections = [coll.name for coll in collections.collections]
    if collection_name not in collections:

        q_client.create_collection(collection_name=collection_name,
                                   vectors_config=models.VectorParams(size=size, distance=models.Distance.COSINE),
                                   )
        print(f"created collection:{collection_name}")
    else:
        print(f"found existing collection:{collection_name}")
    return collection_name


def _index_qdrant_documents(q_client, collection_name, documents: pd.DataFrame):
    # covert documents to points for insertion into qdrant
    points = [
        PointStruct(
            id=doc.id if "id" in doc else str(uuid.uuid4()),
            vector=doc.vector,
            payload={key: doc[key] for key in doc.keys() if key not in ["vector"]},
        )
        for i, doc in documents.iterrows()
    ]

    vector_size = len(points[0].vector)
    # print(f"dimension={vector_size}")

    # Create collection if not existing
    _create_quadrant_collection_dense(q_client, collection_name=collection_name, size=vector_size)
    # index documents
    q_client.upsert(collection_name=collection_name, points=points)


def create_qdrant_index_dense(dirin: str, client_url_path: str = None,
                              collection_name: str = "my-documents",
                              coltext: str = "body",
                              model_id=None
                              ) -> None:
    """
    Create a qdrant index from a parquet file
    dirin: str: path to parquet file
    client_url_path: str: url path to qdrant server
    coltext: str: column name of text column
    model_id: str: name of embedding model to use
    """
    docs = pd_read_file(path_glob=dirin)
    if not client_url_path:
        client = QdrantClient("http://localhost:6333")
    else:
        client = QdrantClient(client_url_path)
    texts = [doc[coltext] for i, doc in docs.iterrows()]

    # intialize model and get document vectors
    if not model_id:
        embedding_model = TextEmbedding()
        vectors = list(embedding_model.embed(texts))
    else:
        embedding_model = SentenceTransformer(model_id)
        vectors = list(embedding_model.encode(texts))
    docs["vector"] = vectors

    # insert documents into qdrant
    _index_qdrant_documents(client, collection_name, docs)


def search_quadrant_index(query, category_filter: list = None, client_url_path: str = None,
                          collection_name: str = "my-documents",
                          model_id: str = None,
                          ):
    """
    Search a qdrant index
    query: str: query to search
    client_url_path: str: url path to qdrant server
    collection_name: str: name of collection to search
    model_id: str: name of embedding model to use
    """
    if not client_url_path:
        client = QdrantClient("http://localhost:6333")
    else:
        client = QdrantClient(client_url_path)
    if not model_id:
        embedding_model = TextEmbedding()
        query_vector = list(embedding_model.embed([query]))[0]
    else:
        embedding_model = SentenceTransformer(model_id)
        query_vector = embedding_model.encode(query)
    if category_filter:
        filter_ = models.Filter(
            should=[
                models.FieldCondition(
                    key="categories",
                    match=models.MatchAny(any=category_filter)
                )])
    else:
        filter_ = None
    search_result = client.search(collection_name=collection_name, query_vector=query_vector, query_filter=filter_)
    # print([scored_point.payload["categories"] for scored_point in search_result])
    # print(f"#search_results:{len(search_result)}")
    return search_result


# Qdrant Sparse Vector Indexing

def _create_quadrant_collection_sparse(q_client, collection_name="documents", size: int = None):
    """
    Create a collection in qdrant
    :param q_client: qdrant client
    :param collection_name: name of collection
    :param size: size of vector
    :return: collection_name
    """
    collections = q_client.get_collections()
    collections = [coll.name for coll in collections.collections]
    if collection_name not in collections:
        q_client.create_collection(collection_name=collection_name,
                                   vectors_config={},
                                   sparse_vectors_config={
                                       "text": models.SparseVectorParams(
                                           index=models.SparseIndexParams(
                                               on_disk=False,
                                           )
                                       )
                                   }
                                   )
        print(f"created sparse collection:{collection_name}")
    else:
        print(f"found existing collection:{collection_name}")
    return collection_name


def _index_qdrant_documents_sparse(q_client, collection_name, documents: pd.DataFrame):
    # covert documents to points for insertion into qdrant
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),
            payload={key: doc[key] for key in doc.keys() if key not in ["vector"]},
            # Add any additional payload if necessary
            vector={
                "text": models.SparseVector(
                    indices=doc.vector[0], values=doc.vector[1]
                )
            },
        ) for i, doc in documents.iterrows()]

    # Create collection if not existing
    _create_quadrant_collection_sparse(q_client, collection_name=collection_name)
    # Index documents
    q_client.upsert(collection_name=collection_name, points=points)


def _compute_sparse_vectors(texts: list, model_id: str = None):
    """
    Compute sparse vectors from a list of texts
    texts: list: list of texts to compute sparse vectors
    model_id: str: name of model to use
    :return: list of tuples (indices, values) for each text
    """

    # Initialize tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForMaskedLM.from_pretrained(model_id)

    # Tokenize all texts
    tokens_batch = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    # Forward pass through model
    with torch.no_grad():
        output = model(**tokens_batch)

    # Extract logits and attention mask
    logits = output.logits
    attention_mask = tokens_batch['attention_mask']

    # ReLU and weighting
    relu_log = torch.log(1 + torch.relu(logits))
    weighted_log = relu_log * attention_mask.unsqueeze(-1)

    # Compute max values
    max_vals, _ = torch.max(weighted_log, dim=1)
    # print(f"max_vals.shape: {max_vals.shape}")

    # for each tensor in batch, get indices of non-zero elements
    indices_list = [torch.nonzero(tensor, as_tuple=False) for tensor in max_vals]
    indices_list = [indices.numpy().flatten().tolist() for indices in indices_list]
    # for each tensor in batch, get values of non-zero elements
    values = [max_vals[i][indices].numpy().tolist() for i, indices in enumerate(indices_list)]

    return list(zip(indices_list, values))


def create_qdrant_index_sparse(dirin: str, client_url_path: str = None,
                               collection_name: str = "my-sparse-documents",
                               coltext: str = "body",
                               model_id: str = None
                               ) -> None:
    """
    Create a qdrant sparse index from a parquet file
    dirin: str: path to parquet file
    client_url_path: str: url path to qdrant server
    coltext: str: column name of text column
    model_id: str: name of sparse embedding model to use
    """
    docs = pd_read_file(path_glob=dirin)
    if not client_url_path:
        client = QdrantClient("http://localhost:6333")
    else:
        client = QdrantClient(client_url_path)
    texts = [doc[coltext] for i, doc in docs.iterrows()]

    # intialize model and get document vectors
    # choose default splade model if not specified
    if not model_id:
        model_id = 'naver/splade-cocondenser-ensembledistil'

    vectors = _compute_sparse_vectors(texts, model_id)  # [_compute_sparse_vector(text, model_id) for text in texts]
    docs["vector"] = vectors

    # insert documents into qdrant
    _index_qdrant_documents_sparse(client, collection_name, docs)


def _extract_and_map_sparse_vector(cols: typing.List, weights: typing.List, tokenizer):
    """
    Extracts non-zero elements from a given vector and maps these elements to their human-readable tokens using a tokenizer. function creates and returns a sorted dictionary where keys are tokens corresponding to non-zero elements in vector, and values are weights of these elements, sorted in descending order of weights.

    This function is useful in NLP tasks where you need to understand significance of different tokens based on a model's output vector. It first identifies non-zero values in vector, maps them to tokens, and sorts them by weight for better interpretability.

    Args:
    vector (torch.Tensor): A PyTorch tensor from which to extract non-zero elements.
    tokenizer: tokenizer used for tokenization in model, providing mapping from tokens to indices.

    Returns:
    dict: A sorted dictionary mapping human-readable tokens to their corresponding non-zero weights.
    """

    # Map indices to tokens and create a dictionary
    idx2token = {idx: token for token, idx in tokenizer.get_vocab().items()}
    token_weight_dict = {idx2token[idx]: round(weight, 2) for idx, weight in zip(cols, weights)}

    # Sort dictionary by weights in descending order
    sorted_token_weight_dict = {k: v for k, v in
                                sorted(token_weight_dict.items(), key=lambda item: item[1], reverse=True)}

    return sorted_token_weight_dict


def search_quadrant_index_sparse(query, category_filter: list = None, client_url_path: str = None,
                                 collection_name: str = "my-documents",
                                 model_id: str = None):
    """
    Search a qdrant index
    query: str: query to search
    client_url_path: str: url path to qdrant server
    collection_name: str: name of collection to search
    model_id: str: name of embedding model to use
    """
    if not client_url_path:
        client = QdrantClient("http://localhost:6333")
    else:
        client = QdrantClient(client_url_path)
    if not model_id:
        model_id = "naver/splade-cocondenser-ensembledistil"

    result = _compute_sparse_vectors([query], model_id)
    query_indices, query_values = result[0]
    query_dict = _extract_and_map_sparse_vector(query_indices, query_values,
                                                AutoTokenizer.from_pretrained(model_id))
    print(f"query_dict:{query_dict}")

    if category_filter:
        filter_ = models.Filter(
            should=[
                models.FieldCondition(
                    key="categories",
                    match=models.MatchAny(any=category_filter)
                )])
    else:
        filter_ = None

    # Searching for similar documents
    search_results = client.search(
        collection_name=collection_name,
        query_vector=models.NamedSparseVector(
            name="text",
            vector=models.SparseVector(
                indices=query_indices,
                values=query_values,
            )
        ),
        query_filter=filter_,
        with_vectors=True,
    )

    return search_results


##  Tantivy Indexing
def _get_tantivy_index(datapath: str = ""):
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_text_field("title", stored=True, index_option="basic")
    schema_builder.add_text_field("body", stored=True, index_option="basic")
    schema_builder.add_text_field("id", stored=True, index_option="basic")
    schema_builder.add_text_field("categories", stored=True, index_option="basic")
    schema_builder.add_text_field("fulltext", index_option="position")

    schema = schema_builder.build()
    # create datastore
    index_path = pathlib.Path(".") / ".tantivy_index"
    if not os.path.exists(index_path):
        index_path.mkdir()
    persistent_index = tantivy.Index(schema, path=str(index_path))
    return persistent_index


def _index_tantivy_documents(writer, documents: pd.DataFrame):
    for i, doc in documents.iterrows():
        # print(type(doc.categories))
        fulltext = " ".join([doc.title, doc.body, " ".join(doc.categories)])
        writer.add_document(
            tantivy.Document(
                title=doc.title,
                body=doc.body,
                id=str(uuid.uuid4()),
                categories=doc.categories,
                fulltext=fulltext
            )
        )
    writer.commit()
    writer.wait_merging_threads()


def create_tantivy_index(dirin: str, datapath: str = "") -> None:
    if not datapath:
        datapath = pathlib.Path(".") / ".tantivy_index"

    # create index schema if not already existing
    persistent_index = _get_tantivy_index(datapath)

    documents = pd_read_file(path_glob=dirin)
    writer = persistent_index.writer(50_000_000)
    _index_tantivy_documents(writer, documents)


def search_tantivy_index(datapath: str = "", query: str = "", size: int = 10):
    """
    Search a tantivy index
    datapath: str: path to tantivy index
    query: str: query to search
    size: int: number of results to return
    :return: list of tuples (score, document) where document is a dictionary of document fields
    """
    if not datapath:
        datapath = pathlib.Path(".") / ".tantivy_index"
    index = _get_tantivy_index(datapath)
    # query_parser = reader.query_parser(["title", "body"], default_conjunction="AND")
    searcher = index.searcher()
    query = index.parse_query(query, ["fulltext"])
    results = searcher.search(query, size).hits
    # print(results)
    score_docs = [(score, searcher.doc(doc_address)) for score, doc_address in results]
    return score_docs


""" 

def create_qdrant_index_dense(dirin:str, dirout:str, 
                         coltext:str="body", ### Vector
                         colscat:list=None,
                         embed_engine_name="embed"
                          )--> None
   ### dirin: list of parquet files :  Ankush
     pip install fastembed
     

def create_qdrant_index_sparse(dirin:str, dirout:str, 
                         coltext:str="body", ### Vector
                         colscat:list=None,
                         embed_engine="embed"
                          )--> None
   ### dirin: list of parquet files :  Ankush
   ### pip install fastembed
   https://qdrant.tech/articles/sparse-vectors/



def merge_fun(x, cols, sep=" @ "):
    ##     textall = title + body. + cat1 " @ "
    ss = ""
    for ci in cols : 
         ss = x[ci] + sep 
    return ss[:-1] 


def create_tantivy_index(dirin:str, dirout:str, 
                         cols:list=None)--> None
   ### dirin: list of parquet files : Ankush
   df["textall"] = df.apply(lambda x : merge_fun(x, cols), axis=1)


#### packages to use 
  pip in




#### Document Schema : specificedby User.
   title  :   text
   body   :    text
   cat1   :    string   fiction / sport /  politics
   cat2   :    string     important / no-important 
   cat3   :    string
   cat4   :    string   
   cat5   :    string    
   dt_ymd :    int     20240311


   ---> Encode into Indexes by engine.



"""


def test_create_qdrant_index_dense():
    """
    test function for dense qdrant indexing
    """
    create_qdrant_index_dense(dirin="documents.parquet",
                              client_url_path=None,
                              collection_name="my-documents",
                              coltext="body",
                              model_id="sentence-transformers/nli-bert-base"
                              )
    results = search_quadrant_index(
        "Generative Knowledge Graph Construction (KGC) refers to those methods that leverage sequence-to-sequence framework for building knowledge graphs, which is flexible and can be adapted to widespread tasks.",
        client_url_path=None, collection_name="my-documents",
        model_id="sentence-transformers/nli-bert-base",
        category_filter=["Fiction"]
    )
    results = [((scored_point.payload["categories"]), scored_point.score) for scored_point in results if
               scored_point.score > 0]
    assert len(results) > 0


def test_create_qdrant_index_sparse():
    """
    test function for sparse qdrant indexing
    """
    create_qdrant_index_sparse(
        dirin="documents.parquet",
        collection_name="my-sparse-documents",
        model_id="naver/splade-cocondenser-ensembledistil"
    )
    results = search_quadrant_index_sparse(
        "Generative Knowledge Graph Construction (KGC) refers to those methods that leverage sequence-to-sequence framework for building knowledge graphs, which is flexible and can be adapted to widespread tasks.",
        # "Knowledge Graph",
        category_filter=["Fiction"],
        collection_name="my-sparse-documents",
        model_id="naver/splade-cocondenser-ensembledistil")

    results = [((scored_point.payload["categories"]), scored_point.score) for scored_point in results if
               scored_point.score > 0]
    print(results)
    print(f"len(results):{len(results)}")
    assert len(results) > 0


def test_create_tantivy_index():
    """
    test function for tantivy indexing
    """
    create_tantivy_index(dirin="documents.parquet")
    results = search_tantivy_index(
        query="Generative Knowledge Graph Construction (KGC) refers to those methods that leverage sequence-to-sequence framework for building knowledge graphs, which is flexible and can be adapted to widespread tasks.")
    print(results)
    assert len(results) > 0


def test_all():
    pass


###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()
    # Way to test qdrant dense function
    # python3 -u engine.py test_create_qdrant_index_dense
    # Way to test qdrant sparse function
    # python3 -u engine.py test_create_qdrant_index_sparse
    # Way to test tantivy function
    # python3 -u engine.py test_create_tantivy_index
"""
    def get(self, word:str, category:str='0', topk:int=10, collection_name=None):

        if isinstance(word, str):
             vector0 = self.__create_embedding_vector(word)
        else:
             vector0 = word     

        collection_name = self.collection_name if collection_name is None else self.collection_name

        search_result = self.client.search(
            collection_name=collection_name,
            query_vector=vector0,
            query_filter=Filter(
                must=[FieldCondition(key="category", match=MatchValue(value=category))]
            ),
            with_payload=True,
            limit=topk,
        )
        return search_result

from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")

# Define filter for category "city" with value "London"
filter_ = models.Filter(
    must=[
        models.FieldCondition(
            key="city",
            match=models.MatchValue(
                value="London",
            ),
        )
    ]
)

# Define search query with filter
search_query = models.SearchRequest(
    vector=[0.2, 0.1, 0.9, 0.7],  # Example vector
    filter=filter_,
    limit=3  # Limit results to 3
)

# Perform search on a specific collection
results = client.search(
    collection_name="your_collection_name",
    query=search_query
)

print(results)
"""
