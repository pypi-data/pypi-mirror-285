"""Qdrant utils

  pip install qdrant fastembed orjson ucall  ukv


"""
import os, sys, numpy as np, pandas as pd, fire
from fastembed.embedding import DefaultEmbedding
import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import uuid
import shutil


########################################~TEST CASES~#################################################################
def test1():
    qd = qDrant(db_path = "./new_path")

    test_list1 = ["MySQL","Docker","PyTorch","NGINX","FastAPI","SentenceTransformers","cron","Django","Qdrant","Python",]
    test_list2 = ["rose","tulip","daisy","dandelion","lily","orchid","sunflower","peony","daffodil","iris","poppy","carnation",]
    test_list3 = ["apple","banana","cherry","date","elderberry","fig","grape","honeydew","kiwi","lemon","mango","nectarine",]


    # Load collection
    qd.load_collection("test15")

    # Create embedding vectors
    embeddings_dict1 = qd.create_embedding(test_list1)
    embeddings_dict2 = qd.create_embedding(test_list2)
    embeddings_dict3 = qd.create_embedding(test_list3)

    # Set vectors
    for word in test_list1:
        qd.set(word,"software",embeddings_dict1[word])

    for word in test_list2:
        qd.set(word,"flowers",embeddings_dict2[word])

    for word in test_list3:
        qd.set(word,"fruits",embeddings_dict3[word])

    # Search
    search_result1 = qd.get("MySQL","software",5)
    print("Search result for MySQL in software category: ")
    print(search_result1)


    search_result2 = qd.get("rose","flowers",5)
    print("Search result for rose in flowers category: ")
    print(search_result2)

    search_result3 = qd.get("apple","fruits",5)
    print("Search result for apple in fruits category: ")
    print(search_result3)



    # Depreciate the db object
    qd = None

    # Reloading the index
    qd = qDrant(file_path="./new_path")
    qd.load_collection("test15")

    # Querying from the reload
    search_result1_after = qd.get("MySQL", "software", 5)
    search_result2_after = qd.get("rose", "flowers", 5)
    search_result3_after = qd.get("apple", "fruits", 5)

    #comparing results (Without assertion)
    def compare_results(before, after, category):
        if before != after:
            print(f"Differences found in {category} category:")
            print("Before Reloading:")
            print(before)
            print("After Reloading:")
            print(after)
            print("******************************************************************************************")
        else:
            print(f"No differences found in {category} category.")
            print("******************************************************************************************")

    # Compare and print differences
    compare_results(search_result1, search_result1_after, "MySQL in software")
    compare_results(search_result2, search_result2_after, "rose in flowers")
    compare_results(search_result3, search_result3_after, "apple in fruits")





#########################################~LOCAL-IM QD without docker~#################################################
class qDrant:
    def __init__(self,db_path, collection_name="test_collection"):
        self.collection_name = collection_name
        self.db_path = db_path
        self.client  = qdrant_client.QdrantClient(path = self.db_path, prefer_grpc=True)
        self.embedding_model = DefaultEmbedding()
        

    def load_collection(self, collection_name:str):
        collection_name_list = [name.name for name in self.client.get_collections().collections]
        if collection_name not in collection_name_list:
            self.client.create_collection(
                collection_name = collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
        self.collection_name = collection_name
        return True
    

    def print_collection(self,):
        collection_name_list = [name.name for name in self.client.get_collections().collections]
        print(collection_name_list)
    

    def create_embedding(self,wlist:list)-> dict[str, np.ndarray]:
        embeddings_dict = {}
        for word in wlist:
            embeddings_dict[word] = self.__create_embedding_vector(word)
        return embeddings_dict
    

    def __create_embedding_vector(self,word:str)-> np.ndarray:
        embedding = list(self.embedding_model.embed([word]))
        return embedding[0]
    

    def set(self, word:str, vector:np.ndarray, category:str='0',  idval:str=None):
        idval = str(uuid.uuid4()) if idval is None else idval
        word_point = PointStruct(
            id=idval,
            vector=vector,
            payload={"category": category, "word":word}
        )

        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=[word_point]
        )
        return operation_info
    

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
    


###############################################################################################
def qdrant_embed(wordlist:list[str], model_name="BAAI/bge-small-en-v1.5", size=128, model=None):
    """ pip install fastembed

    Docs:

         BAAI/bge-small-en-v1.5 384   0.13
         BAAI/bge-base-en       768   0.14
         sentence-transformers/all-MiniLM-L6-v2   0.09

        ll= list( qdrant_embed(['ik', 'ok']))


        ### https://qdrant.github.io/fastembed/examples/Supported_Models/
        from fastembed import TextEmbedding
        import pandas as pd
        pd.set_option("display.max_colwidth", None)
        pd.DataFrame(TextEmbedding.list_supported_models())


    """
    from fastembed.embedding import FlagEmbedding as Embedding

    if model is None:
       model = Embedding(model_name= model_name, max_length= size)

    vectorlist = model.embed(wordlist) 
    return vectorlist


def sim_cosinus(v1:list, v2:list)-> float :
   ### %timeit sim_cosinus(ll[0], ll[1])  0.3 microSec
   import simsimd 
   dist = simsimd.cosine(v1, v2)
   return dist


def sim_cosinus_list(v1:list[list], v2:list[list])-> list[float] :
   ### %timeit sim_cosinus(ll[0], ll[1])  0.3 microSec
   import simsimd
   vdist = [] 
   for x1,x2 in zip(v1, v2):
       dist = simsimd.cosine(x1, x2)
       vdist.append(vdist)
   return vdist


def pd_add_embed(df, col1:str, col2:str=None, size_embed=128, add_similarity=1, colsim=None):
   """
   
    df=  pd_add_embed(df, 'answer', 'answerfull', add_similarity=1)

    df.columns

    df['sim_answer_answerfull'].head(1)


   """ 


   v1 = qdrant_embed(df[col1].values)
   df[col1 + "_vec"] = list(v1)

   if col2 in df.columns:
      v1 = qdrant_embed(df[col2].values)
      df[col2 + "_vec"] = list(v1)

      if add_similarity>0:
         colsim2 = colsim if colsim is not None else f'sim_{col1}_{col2}'  
         vdist   = sim_cosinus_list(df[col1 + "_vec"].values, df[col2 + "_vec"].values, size=size_embed)
         df[ colsim2 ] = vdist
   return df


################################################################################################################################
    
if __name__ == "__main__":
    if os.environ.get('pyinstrument', "0") == "1":
        import pyinstrument
        profiler = pyinstrument.Profiler()
        profiler.start()

        fire.Fire()
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))
    else:
        fire.Fire()
