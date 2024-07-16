""" 



17.12.1.2. Avoiding ambiguity of entities with coreference resolution¶
The prepared text should go through coreference resolution model. In a nutshell, this process should replace all ambiguous words in a sentence so that text doesn’t need any extra context to be understood. For example, personal pronouns are being replaced with a referred person’s name. Although a number of approaches exist to perform task, one of most recently developed is crosslingual coreference from spaCy universe. spaCy is a python library that provides an easy way to create pipelines for natural language processing.

!pip install crosslingual-coreference==0.2.3 spacy-transformers==1.1.5 wikipedia neo4j
!pip install --upgrade google-cloud-storage
!pip install transformers==4.18.0
!python -m spacy download en_core_web_sm
import spacy
import crosslingual_coreference

# Configure `Device` parameter:
DEVICE = -1 # Number of GPU, -1 if want to use CPU

# Add coreference resolution model:
coref = spacy.load('en_core_web_sm', disable=['ner', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
coref.add_pipe("xx_coref", config={"chunk_size": 2500, "chunk_overlap": 2, "device": DEVICE})


https://towardsdatascience.com/extract-knowledge-from-text-end-to-end-information-extraction-pipeline-with-spacy-and-neo4j-502b2b1e0754


"""


def ner_normalize_coreferebce(text):
    """ Normalizes given text by resolving coreference.
    Args:
        text (str): input text to be normalized.

    https://towardsdatascience.com/extract-knowledge-from-text-end-to-end-information-extraction-pipeline-with-spacy-and-neo4j-502b2b1e0754


    17.12.1.2. Avoiding ambiguity of entities with coreference resolution¶
    prepared text should go through coreference resolution model. In a nutshell, this process should replace all ambiguous words in a sentence so that text doesn’t need any extra context to be understood. For example, personal pronouns are being replaced with a referred person’s name. Although a number of approaches exist to perform task, one of most recently developed is crosslingual coreference from spaCy universe. spaCy is a python library that provides an easy way to create pipelines for natural language processing.

    !pip install crosslingual-coreference==0.2.3 spacy-transformers==1.1.5 wikipedia neo4j
    !pip install --upgrade google-cloud-storage
    !pip install transformers==4.18.0
    !python -m spacy download en_core_web_sm


    """

    import spacy
    import crosslingual_coreference


    # Configure `Device` parameter:
    DEVICE = -1 # Number of GPU, -1 if want to use CPU

    # Add coreference resolution model:
    coref = spacy.load('en_core_web_sm', disable=['ner', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer'])
    coref.add_pipe("xx_coref", config={"chunk_size": 2500, "chunk_overlap": 2, "device": DEVICE})

    doc = coref(text)
    return doc


