from utilmy import pd_read_file
from utilmy.nlp import util_transformers
from utilmy.deeplearning import util_embedding
import pandas as pd
import transformers
import numpy as np

# def get_files_directory():
#     return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'ztmp', 'data'))

def test_embedding():
    # Create texts for testing
    text = ["This is a cat", "THIS IS A DOG", "Not the same text", "Small text", "Another text",
           "This is it", "Test", "This is a test", "It is a new text"]

    # Get the embedded vectors using Bert
    embedded_vector = util_transformers.embedding_bert(text)
    print(f"This is the embedeed vector [dim: {embedded_vector.shape}]: \n {embedded_vector}")

    # Compute cosine similarity
    cosine_similarity_score = util_embedding.embedding_cosinus_scores_pairwise(embedded_vector)

    print(f"Similarity between \"{text[0]}\" and \"{text[1]}\": ", cosine_similarity_score['sim_score'][0])
    print(f"Similarity between \"{text[0]}\" and \"{text[2]}\": ", cosine_similarity_score['sim_score'][1])

    # Create dataframe for parquet file
    data = pd.DataFrame([(txt, ",".join(map(str, row))) for txt, row in zip(text, embedded_vector)], columns=['id', 'emb'])
    
    # Set the directories to load and save the files
    dirtmp ="./ztmp/"
    dirfile = dirtmp + 'embedded_vectors.parquet'

    print(f"This is the data: \n{data}")
    data.to_parquet(dirfile, engine='pyarrow')

    # Dimension reduction
    util_embedding.embedding_create_vizhtml(dirin=dirfile, dirout=dirtmp + "/out/")

def test_model():
    # Create texts for testing
    text = ["This is a cat", "THIS IS A DOG", "Not the same text", "Small text", "Another text",
           "This is it", "Test", "THIS IS A TEST", "It is a new text"] 
    
    # Set Bert model
    tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-cased')
    model = transformers.TFBertModel.from_pretrained('bert-base-cased')

    # Create embedded vectors
    embedded_vector = util_transformers.embedding_bert(text, tokenizer=tokenizer, nlp=model)

    # Compute cosine similarity
    cosine_similarity_score = util_embedding.embedding_cosinus_scores_pairwise(embedded_vector)

    print(f"Similarity between \"{text[0]}\" and \"{text[1]}\": ", cosine_similarity_score['sim_score'][0])
    print(f"Similarity between \"{text[0]}\" and \"{text[2]}\": ", cosine_similarity_score['sim_score'][1])

     # Create dataframe for parquet file
    data = pd.DataFrame([(txt, ",".join(map(str, row))) for txt, row in zip(text, embedded_vector)], columns=['id', 'emb'])
    
    # Set the directories to load and save the files
    dirtmp ="./ztmp/"
    dirfile = dirtmp + 'embedded_vectors.parquet'

    print(f"This is the data: \n{data}")
    data.to_parquet(dirfile, engine='pyarrow')

    # Dimension reduction
    util_embedding.embedding_create_vizhtml(dirin=dirfile, dirout=dirtmp + "/out/")

test_embedding()
test_model()