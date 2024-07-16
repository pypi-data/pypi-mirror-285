"""
    #### Install
        # NEbula installation
        Option 0 for machines with Docker: `curl -fsSL nebula-up.siwei.io/install.sh | bash`
        Option 1 for Desktop: NebulaGraph Docker Extension https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext


    #### USAGE:
        cd asearch
        export PYTHONPATH="$(pwd)"  ### relative import issue
        alias pykg="python3 -u rag/engine_kg.py  "

        ###############################################
        ###### Triplet extractions
            #### Create test data using Wikipedia/LlamaIndex
            pykg test_create_test_data --dirout ztmp/kg/testraw.parquet
                    
            ### Extract  triplets From raw text and save to csv 
            pykg  kg_triplets_extract_v2  --dirin myraw.parquet --model_id Babelscape/rebel-large -- dirout ztmp/kg/data/kg_relation.parquet
            

            ### Extract triplet from  agnews Data --> Store in csv file  ( Need Rebel-Large to prevent empty triplet....)
            pykg  kg_triplets_extract_v2  --model_id Babelscape/rebel-large  --dirin ztmp/bench/norm/ag_news/test/df_*.parquet  --dirout ztmp/kg/data/agnews_kg_relation_test.parquet --coltxt body --nrows 1000000 --batch_size 25


        ###############################################
        ##### neo4j DB as KG
            #### Init

                export NEO4J_URI="neo4j://localhost:7687"
                export NEO4J_USERNAME="username"
                export NEO4J_PASSWORD="password"

                pykg neo4j_create_db --db_name "neo4j"


                #### Storage of text in SQL database: (long document is splitted into small chunks)
                   doc_id, text_id, text 
                   ####    
                      doc_id, cat1, cat2, cat3


            #### Generate test questions from Inverting from triplets (using LlamaIndex and GPT3.5 )
               pykg kg_generate_questions_from_triplets --dirin ztmp/kg/data/agnews_kg_relation.parquet --dirout ztmp/kg/data/agnews_kg_questions.parquet --batch_size 20


            #### Insert Triplet
            pykg neo4j_db_insert_triplet_file --dirin ztmp/kg/data/kg_relation.parquet --db_name "neo4j"  --nrows -1


            #### Neo4j Query
            https://github.com/neo4j/NaLLM




        ###############################################
        ##### Using Nebula DB as KG
            ##### Create schema : in Nebula   DB
                pykg nebula_db_create_schema  --space_name kg_relation

            ##### insert triplets to Nebula Graph
                pykg  nebula_db_insert_triplet_file --dirin ztmp/kg/data/kg_relation.parquet   --space_name kg_relation


            ##### search kg:  using LlamaIndex and nebula Graph
                pykg nebula_db_query --space_name "agnews_kg_relation" --query "What is capital of mexico ?"

            ##### benchmark queries using Nebula Graph
                 pykg kg_benchmark_queries --dirin ztmp/kg/data/agnews_kg_questions.parquet --dirout ztmp/kg/data/agnews_kg_benchmark.parquet --queries=1000



          #######################################
          ##### Data Model
          
                      text_cat1 
                          modelid, task, ts, text_id, cat1, cat2, cat3, cat4, 

                      text_cat2 


    #### Data Format: 

     triplet storage : df[["doc_id", "head", "type", "tail"]] 
     question storage : df[["doc_id", "head", "type", "tail", "questions]



    #### Docs Info:
        KG has 2 query modes :
           A) Return list of triplets and ask LLM to generate answers from tiplets.

           B) Return List of documents doc_id and merge Fusion with other rankers
               neo4j_search_docids(db_name="neo4j", query: str = ""):


       B) Search on docid:
           pykg neo4j_search_docids --query "Who visited Chechnya?"
                #results=16, neo4j query took: 0.01 seconds


           query -->Keyword extraction --> Build a cypher query based on those keywords 
                --> Send cypher query to neo4j
                ---> Get triplets
                --> Extract doc_id for each triplet, Score(doc_id)= Frequency of found triplet.
                --> Rank doc by score
                --> Fetch actual text from doc_id using SQL, Sqlite.
                    --> return results SAME Format than Qdrant, tantiviy Engine
                            Engine 
                            TODO: Official return Format as DataClass.






   ### Docs
      Good Recipes for KG building
       https://faircookbook.elixir-europe.org/content/recipes/interoperability/nlp2kg/creating-knowledge-graph-from-text.html

   ### TODO :
      We want to fetch some documents ID, related to triplet of initial Question.

        Current with LllamaIndex :
             Natural Query --> NebulaGraph Cypher query --> Response in triplet --> Converted back in Natural questions (hallucination)


        ----> Use KG as Document Retriever (instead)
        What we to do (ie integrate with other engine)
             Natural Query --> NebulaGraph Cypher query --> Response in triplet 
                    --> Add document related to triplets. ????

               (triplet:  (Person, president, Country) ) ---> List of Doc_id per triplet. (list)

                Check in Nebula to find doc_id related to triplet

                    Or we do external storage (ie parquet or sqlmy, duckdb like sqlite).


         A) Goal attache doc_id to edge A --> B : when can we can retrieve doc_id for RAG part (as retriever)

         B) You are saying:   we need just to retrieve triplets directly from KG query.

             Open discussion, dont worry:  Be good or bad, --> to find something reasonable.

           --> difference is
                  A) we have dense text (ie full sentences)  to feed LLM.
                  B) we have only relation  A do B) : "sparse info"  for LLM.

                  LLnm is better at transforming Dense text.

            My end goal is 
              Use LLM with this prompt
                     you are a writer.

                     Reply to question
                          { my question }

                     Using ONLY context below
                          { context from RAG}     
                                Doc_id --> Dense text all concatenated.

                                Graph -->  Sparse ()

           Did not have time to google search/phind how other people are doing....

           How LlamaIndex does ???
               Query to feed LLM: ???

                  List of Triplets, (by keywords)  --> Graph Schema and records as below

                  In LLM prompt

                     { queestion}

                     {graph Schema} : All relations and node type defintion.

                     {List of triples}

                   --> enough for LLm to repply...


            I think from my experience:
               graph DB can be used in both ways:
                   1) Only triplets and provide grpah triple to LLM.

                   2) Dense Doc_id retriever and provide doc_id + text to LLM.
                         Search Engine can be useful.

                    Investigate quickly and propose  a  simple plan
                       1)
                       2)
                       3)

                    will create different milestone     


             Issues is database
                Nebulagraph looks incomplete, lack of funcitionnalities

                Neo4J : old DB but full of funcitonnalities + community support for bugs/workaround
                         (ie slower)

                 Need to check 
                 You can ask phind to convert stuff...


                 Just double check if Neo4J can accept docid to edge...

                 List of edges --> docid    simple merge ( --> re-rank by frequency --> take top-10 docis)

      

   ### Insert agnews, create some test queries

       "what is capital of mexico ?"

        Method 1:
            ---> Go by triple extractor,  ---> get some triplet --> query directly triple


        def kg_query_...


        Method 2:
            ---> Extract keyword :
                    capital, mexico






    #### Goal to small proptopye of KG retrieval

    A) Indexer :  Extract Triplet (A, relation, B) from raw text --> store in database/NebulaGraph
                Alot of connected keyword. : normalize keywords, extra triplets


    B) query  :
        query --> extract keyword from query --> search in KG datas using keyword and relation around keyword
                --> hybrid with emebdding  -->

    ####
    Groq Engine : Cloud service Host llama3, 
        very fast very cheap,  500 token/seconds,  Alternative to GPT 3.5  (cheaper/faster)

        

   ######## Re-ranking of KG results:


    Here are 10 re-ranking methodologies used for knowledge graph retrieval of documents and re-ranking of results:

    Query Graph Reranking - Refines the initial search results by reranking query graphs for improved knowledge base question answering 1.
    Embedding-based Models - Utilize embeddings to capture semantic and structural knowledge for re-ranking 412.
    Rule-induction and Subgraph-induction Methods - Employ rules and subgraphs to re-rank results 4.
    Language-based Models - Leverage language models to re-rank by calculating probabilities of candidates 412.
    Generative Relevance Feedback - Uses adaptive re-ranking with different first stages to find optimal graph traversal points 9.
    Normalized Relevance Score Display - Shows normalized [0..100] relevance scores next to each search result to indicate ranking distribution 10.
    Query Clarity Evaluation - Assesses clarity of document sets for re-ranking, regardless of how they are obtained 10.
    BERT-based Re-ranking - Applies BERT to score candidates by concatenating their textual forms with the query 12.
    Generative LLM-based Re-ranking - Utilizes generative language models to model the re-ranking process and generate candidate rankings 1213.
    Hybrid Search and Re-rank - Combines various search technologies and uses a rerank model to calculate relevance scores between query and documents for improved semantic sorting 14.
    The key is to refine initial search results using techniques like graph traversal, embeddings, rules, language models, relevance feedback, and hybrid approaches to deliver more accurate and relevant information 23514.


    ######################################################################################################
    #### Entity Extractor :

    https://github.com/zjunlp/DeepKE

    https://github.com/thunlp/OpenNRE

    https://github.com/zjunlp/KnowLM

    https://maartengr.github.io/BERTopic/getting_started/representation/representation.html#maximalmarginalrelevance

    
    
    1)
    Llamax -- use LLM + Prompt

    2) BERt like model to extract.(faster/cheaper) 
    https://medium.com/nlplanet/building-a-knowledge-base-from-texts-a-full-practical-example-8dbbffb912fa

    pre-trained model.  --> with huggingFae directlyt.
        https://huggingface.co/Babelscape/mrebel-large


    3) ... NER extraction...


    
    Llama Index --> Nebula Graph




    without LLM, one way:
    https://medium.com/nlplanet/building-a-knowledge-base-from-texts-a-full-practical-example-8dbbffb912fa


    ####Groq is cheap/Fast for Llama3 Enitry extraction
        https://towardsdatascience.com/relation-extraction-with-llama3-models-f8bc41858b9e



    #### Questions Pairs
        https://huggingface.co/datasets/databricks/databricks-dolly-15k



    REBEL model

    https://huggingface.co/Babelscape/mrebel-large



    Building  KG graph index is  trickier part....

    https://github.com/wenqiglantz/llamaindex_nebulagraph_phillies/tree/main

    https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c


    hacked  coedium engine to access by CLI (ie auto generate  docstring)


# Findings:
1. Number of triplets not dependent on text length but number of entities present in document.
2. Some times same information is being indexed in 2 triplets
Eg:
[[{'head': 'NASA', 'type': 'subsidiary', 'tail': 'Ames Research Center'}, {'head': 'Ames Research Center', 'type': 'parent organization', 'tail': 'NASA'}]]
This might lead to skewness in scoring.


##### REBEL findings:
        BAse model:  BART-large model
        Dataset: finetuning using REBEL-dataset.
        REBEL-dataset was prepared from wikipedia abstracts, Entities in the
        abstracts were linked to their corresponding  Wikidata entries. Candidate relations between those entities were picked
        from wikidata. Relations relevant to text were selected using Roberta model framing as text entailment problem.
        Eg:
        text <sep> relation_i  => entailment score
        if entailment score >0.75 then relation_i is relevant and becomes part of dataset else discarded and new candidate
        relation between those entities is considered.

        due to this method, we have *standard names* for relations:
        For eg:
        text: "Spain announce Davis Cup line-up Spain have named an unchanged team for the Davis Cup final against the United States in Seville on 3-5 December."
        relation: Davis Cup, Spain, participating team
        text: "Best Asian Tourism Destinations The new APMF survey of the best Asian tourism destinations has just kicked off,
        but it's crowded at the top, with Chiang Mai in Thailand just leading from perennial favourites Hong Kong,
        Bangkok and Phuket in Thailand, and Bali in  Indonesia."
        relation: Indonesia	Bali contains administrative territorial entity

        Due to use of standard relation, we get enough triplets per relation despite differnt text being used to represent that
        relation. Hence better fit as well as generalization in comparison to if we would have created relation just by using phrases
        in text.

        My opinion:
        Knowledge graphs are supposed to store facts about entities. For this to be done, the interpretation of entities need to
        be same across entire corpus. "Entity1"  should be grounded and represent same real world concept in all the triplets.
        This leads to triplet generation being heavily dependent on the named entities in the text. Named entities that are widely known
        and agreed upon. Common words like cat , city are often leftout in the triplet generation as their meaning is contextual
        and may differ across different tripets. Words like USA, Saudi, NASA etc are considered as named entities.
        Due to this constraint, KG retrieval is lossy in comparison to other search engines and their low performance is neither
        surprising nor does it mean that model isn"t performing enough. It means text doesnt have enough named entities due to
        which KG engine is blind to most of the information in text, which is very well captured in other search engines
        especially sparse.

##### Fine Tuning
    Input: 
       The Philippine one hundred-peso note ( Filipino: "Sandaang Piso" ) ( ₱100 ) is a denomination of Philippine currency .
       
    Output:
                     entityA                         entityB ,   Relation 
    <triplet> Philippine one hundred-peso note <subj> 100 <obj> face value</Tokytriplet>

    Create a dataset like this
    
    
    Many ways:
        Useful use case:        

        1) Pick the bad sample, and ask GPT-4 to generate the triplets.
              List of scores from neo4J
                 top-k text
                 raw text


        3) unknown relation:
           1) sentences --> NER ---> (entA, entB, entC, entD)           
                 (entA, entC) --> unknow_relation [ doc_id ]                 
               classify entX is relation or not.
               
              
                          
            1) Create report             
                looad darframe and topk > 5
                df_bad = df.topk> 5    
                re-ranking is bias :  
             
             2) minimal 5 samples dataset to fine rebel : 
                 code running for fine tuning.
             
             
                     
        
        2) Pre-defined database of data:  Reverse Engineer from the databse.
               How to generate the ground through, even imperfect.

            Domain field/knowledge:
               Databse
                    entitt ; Yes or NO
                    very rare word --> Databse --> indenfity as entiy                    
                    Biologu, Pharma: complicated word.
                      but you have the list of medical word --> entity
    
            Relation : 
                 Fake relation, pseudi-true relation from database.                 
                 --> sample to FORCE the model to recognize those words AS entity.                 
    
               Force the entity artificallly.
               Force the relation artifically.
    
            database of event:
                    A  happens at th
                        
            colA, colB, colC  (definition)  SQL to generate cola, colb, colc.                 
                 colA: entiy A
                 colab: entity B
                 colC: relation

            triplets --> sentences.
                Template sentence:
                    {Period}, {PersonA} visited {location}.
                    ....
                    
               Ask GPT to reformulate while keeping same mearning.
               --> many sentences --> fine tuning.
               --> Know the ground thrught --> evaluate easily.                      

                                     
                                              
        3)  NER: un-supservised NER.
           sentences --> NER -->   {PersonA},  {actionB}  {locationC} .
           
             Classify the NER tag : 500 NER tags.. : classifty using GPT-4             
                 NER-tag1 --> entity
                 NER-tag3 --> relation
                                     
            Parse the NER sentence :  remove the entiy {personA}
                 --> remaining NER : relation ot no.

        Example:         
              Cat sat on the mat. : Un-parsed. by NER and Rebel.


        Step 1:
        Generate Text from Triplet in Database, using Manuakl Human Template

        Step 2:
        Generate variation of this text using GPt-4 (ie but meaning is SAME).



        Step3
        Feed all in the fine tuning model,

        Key idea is Step 1:
        We reverse generate sentence : Database --> Manual sentence using template.

        {Period}, {Person} visited {location} .

        Period: last year, yesterday,
        person; Obama, Clinton,/..
        location: USA, india, London,...

        We need to have some manual template,
        which FORCE the triplets and entity we want...

        ---> Force Rebel to recognize our domain field.









"""

if "import":
    import os, time, traceback, warnings, logging, sys, sqlite3
    from collections import Counter

    warnings.filterwarnings("ignore")

    import json, warnings, spacy, pandas as pd, numpy as np
    from dataclasses import dataclass

    ### KG
    from nebula3.Config import Config
    from nebula3.gclient.net import ConnectionPool
    from nebula3.common import *
    from neo4j import GraphDatabase

    # NLP
    from transformers import (pipeline)
    import spacy

    spacy_model = None

    ############################################
    from rag.llm import llm_get_answer

    from utils.utils_base import torch_getdevice, pd_append

    ## Uncomment this section for llamaindex llm call logs
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    import llama_index.core

    llama_index.core.set_global_handler("simple")

    ############################################
    from utilmy import pd_read_file, os_makedirs, pd_to_file
    from utilmy import log


################################################################################
def test_create_test_data(dirout="./ztmp/testdata/myraw.parquet"):
    """
    usage: pythpn3 -u enging_kg test_create_test_data --dirout myraw.parquet
    """
    from llama_index.readers.wikipedia import WikipediaReader
    loader = WikipediaReader()
    documents = loader.load_data(
        pages=["Guardians of  Galaxy Vol. 3"], auto_suggest=False
    )
    text_list = documents[0].text.split("\n")
    # remove short lines
    text_list = [text for text in text_list if len(text) > 20]
    text_df = pd.DataFrame(text_list, columns=["text"], dtype=str)
    pd_to_file(text_df, dirout, show=1)


def test0():
    triplet_extractor = pipeline('translation_xx_to_yy', model='Babelscape/mrebel-base',
                                 tokenizer='Babelscape/mrebel-base')

    # We need to use  tokenizer manually since we need special tokens.
    msg = " Red Hot Chili Peppers were formed in Los Angeles by Kiedis, Flea"
    extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(msg,
                                                                                 src_lang="en", return_tensors=True,
                                                                                 return_text=False)[0][
                                                                   "translation_token_ids"]])  # change __en__ for  language of  source.
    log(extracted_text[0])



####################################################################################################
#### Triplet using LLM
def llm_triplet():
    """
      LLM Extraction:

      groq API KEY
      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


https://towardsdatascience.com/relation-extraction-with-llama3-models-f8bc41858b9e

    
    """

######################################################################################################
#######  NLP Tools: triplet, keywords ################################################################
class SpacyModel:
    def __init__(self, model_id="en_core_web_sm"):
        self.model_id = model_id
        self.nlp = spacy.load(model_id)
        self.nc_exceptions = ["-", "—", "What"]

        # exception added due to obseverved misbehaviour in  spacy model 3.7.1
        ruler = self.nlp.get_pipe("attribute_ruler")
        patterns = [[{"ORTH": "-"}]]
        attrs = {"TAG": "HYPH", "POS": "PUNCT"}
        ruler.add(patterns=patterns, attrs=attrs)

    def extract_keywords(self, text_list: list) -> list:
        """Extracts keywords from a list of text using spaCy library.
        Args:
            text_list (list): A list of text strings from which to extract keywords.

        Returns:
            list: A list of lists, where each inner list contains keywords extracted 
            
        """
        result = []
        docs = self.nlp.pipe(text_list)

        for doc in docs:
            keywords = [nc.text for nc in doc.noun_chunks if nc.text not in self.nc_exceptions]
            result.append(keywords)
        return result


class TripletExtractorModel:
    def __init__(self, model_id='Babelscape/rebel-large', model_type="mrebel"):
        """Initializes  TripletExtractorModel with  specified model_id and model_type.
         Args:
            model_id (str):  ID of  model to be used. Default is 'Babelscape/rebel-large'.
            model_type (str):  type of  model. Default is "mrebel".

        """
        self.model_id = model_id
        self.model_type = model_type

        if model_type == "mrebel":
            s_time = time.time()
            device = torch_getdevice()
            self.pipeline = pipeline('text2text-generation', model=model_id,
                                     tokenizer=model_id, device=device)
            log(f"Model loaded in {time.time() - s_time:.2f} seconds")
        else:
            raise ValueError(f"Invalid model type: {model_type}")

    def extract_triplets(self, text) -> list:
        """Extracts triplets from  given text.

        Args:
            text (str):  text from which to extract triplets.

        Returns:
            list: A list of dictionaries representing  extracted triplets. 
            Each dictionary contains  keys 'head', 'type', and 'tail', representing  subject, predicate, and object of  triplet.

        """
        triplets = []
        relation, subject, relation, object_ = '', '', '', ''
        text = text.strip()
        current = 'x'
        for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
            if token == "<triplet>":
                current = 't'
                if relation != '':
                    triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
                    relation = ''
                subject = ''
            elif token == "<subj>":
                current = 's'
                if relation != '':
                    triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
                object_ = ''
            elif token == "<obj>":
                current = 'o'
                relation = ''
            else:
                if current == 't':
                    subject += ' ' + token
                elif current == 's':
                    object_ += ' ' + token
                elif current == 'o':
                    relation += ' ' + token
        if subject != '' and relation != '' and object_ != '':
            triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
        return triplets

    def extract(self, text_list: list) -> list:
        """Extracts information from a list of texts and returns a list of extracted triplets.
        
         Args:
            text_list (list): A list of texts for which information needs to be extracted.
        
        Returns:
            list: A list of extracted triplets containing  head, type, and tail of each triplet.
        """

        # result = []
        from datasets import Dataset

        data = {'id': np.arange(0, len(text_list)),
                'text': text_list
                }
        dataset = Dataset.from_dict(data)
        # log(dataset)

        text_list2 = self.pipeline(dataset["text"], return_tensors=True, return_text=False)
        text_list2 = self.pipeline.tokenizer.batch_decode([x["generated_token_ids"] for x in text_list2])

        # log(f"extracted_text: {extracted_text}")
        # result = [[] for _ in range(len(text_list2))]
        list_list_triplets = []
        for i, text in enumerate(text_list2):
            triplet_list = self.extract_triplets(text)
            list_list_triplets.append(triplet_list)
        return list_list_triplets


    def extract_pandas(self, df) -> pd.DataFrame:
        """Extracts information from a list of texts and returns a list of extracted triplets.
        
         Args:
            text_list (list): A list of texts for which information needs to be extracted.
        
        Returns:
            list: A list of extracted triplets containing  head, type, and tail of each triplet.
        """

        # result = []
        from datasets import Dataset

        data = {'id': np.arange(0, len(text_list)),
                'text': text_list
                }
        dataset = Dataset.from_dict(data)
        # log(dataset)

        text_list2 = self.pipeline(dataset["text"], return_tensors=True, return_text=False)
        text_list2 = self.pipeline.tokenizer.batch_decode([x["generated_token_ids"] for x in text_list2])

        # log(f"extracted_text: {extracted_text}")
        # result = [[] for _ in range(len(text_list2))]
        list_list_triplets = []
        for i, text in enumerate(text_list2):
            triplet_list = self.extract_triplets(text)
            list_list_triplets.append(triplet_list)
        return list_list_triplets






class SpacyTripletExtractorModel:

    def __init__(self, model_id='Babelscape/rebel-large'):
        self.model_id = model_id
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.add_pipe("rebel", after="senter", config={
            'device': -1,  # Number of GPU, -1 if want to use CPU
            'model_name': model_id}  # Model used, will default to 'Babelscape/rebel-large' if not given
                          )

    def post_process(self, extracted_triplets):
        post_processed = []
        for triplet in extracted_triplets:
            p_triplet = {}
            p_triplet['head'] = triplet['head_span'].lemma_  # span => lemmatized str
            p_triplet['tail'] = triplet['tail_span'].lemma_  # span => lemmatized str
            p_triplet['type'] = triplet['relation']  # already str
            post_processed.append(p_triplet)
        return post_processed

    def extract(self, text_list: list) -> list:
        result = []
        docs = self.nlp.pipe(text_list)
        for doc in docs:
            for value, rel_dict in doc._.rel.items():
                result.append(rel_dict)

        result = self.post_process(result)
        return result


##################################################################################################
###### Triplets  tasks   #########################################################################
# @dataclass
# class TripletSchema:
#    doc_id:int 
#    head:str 
#    tail:str
#    type:str
#    info_json:str





def kg_triplets_extract_v2(cfg=None, dirin="./ztmp/bench/ag_news/aparquet/*.parquet",
                           dirout="ztmp/bench/ag_news/kg_triplets/kg_relation.parquet",
                           model_id="Babelscape/rebel-large",
                           istart=20000,
                           nrows=1000000,
                           colid="text_id", coltxt="text",
                           batch_size=1000):
    """Extract triplets from raw text, using Rebel and save to csv
       
       export pykg="python -u rag/engine_kg.py  "
       pykg kg_triplets_extract_v2  --dirin myraw.parquet --model_id Babelscape/rebel-large -- dirout .ztmp/data/kg/kg_relation.parquet
            Processed docs/Time taken:
            10/5.56 seconds
            20/9.66 seconds
            30/14.06 seconds

    """
    df = pd_read_file(dirin)
    assert coltxt in df.columns

    log(df)
    # pick nrows rows from df
    df = df.iloc[istart:istart + nrows, :]
    log(df)

    extractor = TripletExtractorModel(model_id=model_id)
    # extractor = SpacyTripletExtractorModel(model_id=model_id)

    kmax = 1 + int(len(df) // batch_size)
    for k in range(0, kmax):
        log(k)


        dfk = df.iloc[k * batch_size:(k + 1) * batch_size, :]

        idx0 = dfk.index[0]
        text_ids: list = dfk[colid].values.tolist()
        txt_list: list = dfk[coltxt].values.tolist()
        diroutk = dirout.replace(".parquet", f"_{idx0}_{k}_{len(dfk)}.parquet")
        del dfk

        log("####### Start model triplet exraction ##############")
        extracted_triplets: list = extractor.extract(txt_list)

        log("####### Save triplet exraction #####################")
        # log(f"len(extracted_triplets): {len(extracted_triplets)}")
        result = zip(text_ids, extracted_triplets)
        kg_triplets_save(result, dirout=diroutk)


def kg_triplets_save(textid_triplets_tuple: list, dirout=",/ztmp/bench/ag_news/kg_triplets/kg_triplet.parquet"):
    """ Save triplets extracted from documents to file

    Args:
        doc_id_triplets (list): A list of tuples containing document IDs and their corresponding triplets.
            Each tuple consists of a document ID (str) and a list of triplets (dict).
            Each triplet is a dictionary with keys "head" (str), "type" (str), and "tail" (str).
        dirout (str ): path to output CSV file.     : ",/ztmp/out/kg/kg_relation.parquet".

    """
    df = pd.DataFrame(columns=['text_id', 'head', 'type', 'tail', "info_json"])
    if os.path.exists(dirout):
        df = pd_read_file(dirout)
        df = df[['text_id', 'head', 'type', 'tail', "info_json"]]

    row_list = []
    for text_id, triplets in textid_triplets_tuple:
        for triplet_dict in triplets:
            row_list.append([str(text_id), triplet_dict["head"],
                             triplet_dict["type"],
                             triplet_dict["tail"],
                             triplet_dict.get("info_json", "")])  # dummy field added to avoid parquet error

    df = pd_append(df, row_list)
    df = df.drop_duplicates(subset=['text_id', 'head', 'type', 'tail'], keep='first')
    log(df[['head', 'type', 'tail']])
    pd_to_file(df, dirout, show=0)




######################################################################################################
##############  NEO4J DB   ###########################################################################

#### Insert triplet Mode   ################################################
def neo4j_create_db(db_name="neo4j"):
    """Creates a Neo4j database with specified name.
    Args:
        db_name (str ):  name of Neo4j database.     : "neo4j".

        python rag/engine_kg.py neo4j_create_db --db_name "neo4j"


        Installation steps (https://neo4j.com/docs/operations-manual/current/installation/linux/tarball/):
            1. Download tar file from https://neo4j.com/deployment-center
            2. tar zxf neo4j-enterprise-5.19.0-unix.tar.gz
            3. mv neo4j-community-5.19.0 /opt/
            ln -s /opt/neo4j-community-5.19.0 /opt/neo4j
            4.  groupadd neo4j
                useradd -g neo4j neo4j -s /bin/bash
            5. chown -R neo4j:adm /opt/neo4j-community-5.19.0

            Run in background:
            1. /opt/neo4j/bin/neo4j start
            2. Web UI: http://localhost:7474

        Docker run:    





    """
    # URI = "neo4j://localhost:7687"
    # AUTH = ("neo4j", "hell0neo")

    driver = neo4j_get_client()

    # with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    # create db
    # Note: community edition supports only single database
    # query = f"CREATE DATABASE {db_name} IF NOT EXISTS;"
    # add constraint to avoid duplicates
    # driver.execute_query(query_=query)
    query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.name IS UNIQUE"
    driver.execute_query(query_=query, database_=db_name)

    driver.close()


def neo4j_db_insert_triplet_file(dirin="ztmp/kg/data/kg_relation.parquet", db_name="neo4j",
                                 nrows: int = -1, ntry_max=3):
    """Inserts triplets from a CSV file into a Neo4j database.
  
       #triples: 1627, total time taken : 8.34 seconds  

       Args:
            dirin (str ):    path to CSV file containing triplets.     : "ztmp/data/kg_relation.parquet".
            db_name (str ):  name of Neo4j database.     : "neo4j".
            nrows (int ):    number of rows to process from CSV file.     : -1 (process all rows).

        Returns:
            None: If an exception occurs during execution of query.
    """
    df = pd_read_file(dirin)
    nrows = len(df) if nrows < 0 else nrows

    df = df.iloc[:nrows, :]

    # URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    # expects NEO4J_USERNAME and NEO4J_PASSWORD in env
    # AUTH = (os.environ.get("NEO4J_USERNAME", "username"), os.environ.get("NEO4J_PASSWORD", "password"))

    driver = neo4j_get_client()
    # with GraphDatabase.driver(URI, auth=AUTH) as driver:
    s_time = time.time()
    for row in df.itertuples():
        # pro: single query for all insertions
        # con: docids may contain duplicates
        query = f"""
                MERGE (head:Entity {{name: $head}})
                ON CREATE SET head.name = $head
                MERGE (tail:Entity {{name: $tail}})
                ON CREATE SET tail.name = $tail
                MERGE (head)-[relation:Relationship {{name: $type__}}]->(tail)
                ON CREATE 
                    SET 
                        relation.textids = [$text_id]
                ON MATCH 
                    SET 
                        relation.textids = relation.textids + [$text_id]
                """
        params = {"head": row.head, "tail": row.tail, "type__": row.type, "text_id": row.text_id}
        # pro: keeps docids unique in db
        # con: run 2 queries for 1 insertion
        # check if relation already exists
        # query = f"MATCH (n:Entity {{id: '{head}'}})-[r:RELATIONSHIP {{name: '{relation}'}}]->(m:Entity {{id: '{tail}'}}) RETURN r"
        # result, _, _ = driver.execute_query(query_=query, database_="neo4j")
        # if len(result) > 0:
        #     # log(result[0]["r"]["docids"])
        #     if docid not in result[0]["r"]["docids"]:
        #         # update relationship with new docid
        #         query = f"MATCH (n:Entity {{id: '{head}'}})-[r:RELATIONSHIP {{name: '{relation}'}}]->(m:Entity {{id: '{tail}'}}) SET r.docids = r.docids + [{docid}] RETURN r"
        #         driver.execute_query(query_=query, database_="neo4j")
        #     return
        #
        # query = f"""CREATE (e1:Entity {{id: '{head}'}}),
        # (e2:Entity {{id: '{tail}'}}),
        # (e1)-[:RELATIONSHIP {{name: '{relation}', docids: {[docid]}}}]->(e2);"""

        # log(query)
        ntry = 0
        ii = 0
        ntry = 0
        while ntry < ntry_max:
            try:
                driver.execute_query(query_=query, **params, database_=db_name)
                ii += 1
                break
            except Exception as e:
                log(traceback.format_exc())
                log(query)
                ntry += 1
                time.sleep(5 * ntry)

    log(f" #triplet inserted: {ii} / {nrows},  time : {(time.time() - s_time):.2f} seconds")
    driver.close()


#### Search Mode   ###################################################
def neo4j_search_triplets_bykeyword(cfg=None, db_name="neo4j", keywords: list = None):
    from neo4j import GraphDatabase
    # query = f"""
    #         WITH {keywords} AS keywords
    #         MATCH (entity1)-[rel]-(entity2)
    #         WHERE any(keyword IN keywords WHERE entity1.name CONTAINS keyword
    #                   OR entity2.name CONTAINS keyword
    #                   OR type(rel) CONTAINS keyword)
    #         RETURN entity1, rel, entity2
    # """
    # leads to 41.1% accuracy
    query = f"""
                WITH {keywords} AS keywords
                MATCH (entity1)-[rel]-(entity2)
                WHERE any(keyword IN keywords WHERE toLower(entity1.name) CONTAINS toLower(keyword)
                          OR toLower(entity2.name) CONTAINS toLower(keyword)
                          OR toLower(rel.name) CONTAINS toLower(keyword))
                RETURN entity1, rel, entity2
        """
    # leads to 42.2% accuracy

    # query = f"""
    #             WITH {keywords} AS keywords
    #             MATCH (entity1)-[rel]-(entity2)
    #             WHERE any(keyword IN keywords WHERE toLower(entity1.name) = toLower(keyword)
    #                       OR toLower(entity2.name) = toLower(keyword)
    #                       OR toLower(rel.name) = toLower(keyword))
    #             RETURN entity1, rel, entity2
    #      """
    # leads to 38.8% accuracy

    driver = neo4j_get_client()
    # log(query)
    # URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    # expects NEO4J_USERNAME and NEO4J_PASSWORD in env
    # AUTH = (os.environ.get("NEO4J_USERNAME", "username"), os.environ.get("NEO4J_PASSWORD", "password"))
    # with GraphDatabase.driver(URI, auth=AUTH) as driver:
    s_time = time.time()
    records, summary, keys = driver.execute_query(query_=query, database_=db_name)
    # log(f"#results={len(records)}, neo4j query took: {time.time() - s_time:.2f} seconds")
    driver.close()
    return records


def neo4j_convert_result_triplets_to_df(triplets: list):
    triplet_rows = []
    for ent1, rel, ent2 in triplets:
        triplet = [item._properties['name'] for item in [ent1, rel, ent2]]
        r_textids = list(set(rel._properties["textids"]))
        triplet_rows.append([r_textids, *triplet])

    triplet_df = pd.DataFrame(triplet_rows, columns=["text_id", "head", "relation", "tail"])

    triplet_df = triplet_df.explode("text_id")
    return triplet_df




def neo4j_triplet_scorer(dfi, question):
    """
        Assign score to triplet based on overlapping components with question
        """
    score = 0
    for i, row in dfi.iterrows():
        triplet = (row["head"], row["relation"], row["tail"])
        intersection_score_map = {
            (1, 1, 1): 10,
            (1, 1, 0): 5,
            (0, 1, 1): 5,
            (1, 0, 1): 2,
            (1, 0, 0): 1,
            (0, 1, 0): 1,
            (0, 0, 1): 1,
        }
        question = question.lower()
        triplet_intersection = tuple([1 if item.lower() in question else 0 for item in triplet])
        score += intersection_score_map.get(triplet_intersection, 0)
    return score


def neo4j_triplet_rerankscorer(triplet_df, question, topk=-1):
    """
        Assign score to triplet based on overlapping components with question
    """        
    if len(triplet_df) == 0:
        return pd.DataFrame()
    df_score         = triplet_df.groupby("text_id").apply(lambda dfi: neo4j_triplet_scorer(dfi, question=question)).reset_index()
    df_score         = df_score.rename(columns={0: "score_rerank"})
    df_score         = df_score.sort_values(by="score_rerank", ascending=False)
    topk = topk if topk > 0 else len(df_score)
    df_score         = df_score.iloc[:topk,:]
    return df_score




def neo4j_search_docids(cfg=None, db_name="neo4j", query: str = "", model_keyword="en_core_web_sm", topk: int = 5):
    """Performs a search of (docid, doc_text) in a Neo4j database based on given query.
    Docs:
        Args:
            db_name (str ):  name of Neo4j database.     : "neo4j".
            query (str ):  search query.     : "".

        Returns:
            list: A list of dictionaries representing search results. Each dictionary contains following keys:
                - "id" (str):  ID of document.
                - "text" (str):  text content of document.
                - "score" (float):  score indicating relevance of document to search query.

        Notes:
            query -->Keyword extraction --> Build a cypher query based on those keywords 
                    --> Send cypher query to neo4j
                    ---> Get triplets
                    --> Extract doc_id for each triplet, Score(doc_id)= Frequency of found triplet.
                    --> Rank doc by score
                    --> Fetch actual text from doc_id using SQL, Sqlite.
                        --> return results SAME Format than Qdrant, tantiviy Engine
                                Engine 
                                TODO: Official return Format as DataClass



            -  search is performed by extracting keywords from query using `nlp_extract_keywords_from_text` function.
            -  search is performed in specified Neo4j database using `neo4j_search_triplets_bykeyword` function.
            -  search results are processed to retrieve document IDs and their corresponding scores using `neo4j_get_docs_from_triplets` function.
            -  text content of documents is fetched from a local database using `dbsql_fetch_text_by_doc_ids` function.
            -  relevance scores are assigned to records.
            -  records are sorted based on relevance scores in descending order.

        Example:
            >>> neo4j_search_docids(db_name="my_database", query="search query")
            [
                {
                    "id": "document1_id",
                    "text": "document1_text",
                    "score": 8
                },
                {
                    "id": "document2_id",
                    "text": "document2_text",
                    "score": 6
                },
                ...
            ]
    """
    global spacy_model
    if spacy_model is None:
        spacy_model = SpacyModel("en_core_web_sm")
    keyword_list = spacy_model.extract_keywords([query])
    keywords = keyword_list[0]

    triplet_list = neo4j_search_triplets_bykeyword(db_name=db_name, keywords=keywords)
    if len(triplet_list) == 0:
        return []

    triplet_df   = neo4j_convert_result_triplets_to_df(triplet_list) ### textid, head, rel, tail
    assert triplet_df[[ "text_id", "head", "relation", "tail"]].shape

    ##### re-ranking  ###########################
    df_textid_score = neo4j_triplet_rerankscorer(triplet_df, question=query, topk=topk)
    # df_doc_id_score = triplet_df.groupby("textid").apply(lambda dfi: neo4j_triplet_scorer(dfi, question=query))
    # docid_score_map = {doc_id: score for doc_id, score in df_textid_score.items()}

    textid_score_map = df_textid_score.set_index('text_id').to_dict(orient='index')
    textid_score_map = {str(k): v['score_rerank'] for k, v in textid_score_map.items()}
    text_ids         = list(df_textid_score["text_id"].values)
    # log(f"text_ids: {text_ids}")
    
    #### Doc list
    doc_list = dbsql_fetch_text_by_doc_ids(text_ids=text_ids)
    for x in doc_list:
        x["score"] = textid_score_map[ x["text_id"]]
        
    doc_list = sorted(doc_list, key=lambda x: x["score"], reverse=True)
    # doc_list = doc_list[:topk]
    # log(doc_list)
    return doc_list


# def z_neo4j_get_fuzzy_intersection_score(triplet: list, question: str):
#     """
#     Assign score to triplet based on overlapping components with question
#     """
#     assert len(triplet) == 3
#     intersection_score_map = {
#         (1, 1, 1): 10,
#         (1, 1, 0): 5,
#         (0, 1, 1): 5,
#         (1, 0, 0): 1,
#         (0, 1, 0): 1,
#         (0, 0, 1): 1,
#     }
#     question = question.lower()
#     triplet_intersection = tuple([1 if item.lower() in question else 0 for item in triplet])
#     final_score = intersection_score_map.get(triplet_intersection, 0)
#     return final_score


# def z_neo4j_rerank_docs_from_triplets(triplet_list: list, question: str, topk: int = -1) -> list:
#     """Get document IDs from neo4j results.
#     Args:
#         results (list): A list of tuples containing results.
#         topk (int ):  maximum number of document IDs to return.     : -1, which returns all document IDs.
#
#     Returns:
#         list: A list of document IDs.
#     """
#     text_ids = []
#     # log(f"len(results): {len(results)}")
#     for ent1, rel, ent2 in triplet_list:
#         triplet = [item._properties['name'] for item in [ent1, rel, ent2]]
#         fuzzy_intersection = neo4j_get_fuzzy_intersection_score(triplet, question)
#         r_textids = list(set(rel._properties["textids"]))
#
#         # increase corresponding docid count by their score. equivalent to weighting the docid when applying Counter
#         text_ids.extend(r_textids * fuzzy_intersection)
#
#     ###### Re-Rank by total weight accumulated  #################################
#     textid_counter = Counter(text_ids)
#     topk = len(textid_counter) if topk == -1 else topk
#
#     ### Scoring of doc_id by frequency.
#     text_ids = [(k, v) for k, v in textid_counter.most_common(topk)]
#     return text_ids

def neo4j_get_docs_from_triplets_v2(triplet_list: list, question: str, topk: int = -1) -> list:
    """Get document IDs from neo4j results.
    Args:
        results (list): A list of tuples containing results.
        topk (int ):  maximum number of document IDs to return.     : -1, which returns all document IDs.
        
        
        dataframe :
        
      ### normalize triplets into dataframe     
      df[[ "textid", "ent1", "rel", "ent2"]] 
        
        
      ### Re-ranking score
      df[[ "textid", "ent1", "rel", "ent2", "score_rerank]] 
      
      
      ### Topk  
      df =  df.sort_values(by="score_rerank", ascending=False)[["textid", "ent1", "rel", "ent2", "score_rerank"]][:topk]

      ### list of doc ids
      text_ids =  [(textid, score ) for  df[["textid", 'score_rerank']].values


    Returns:
        list: A list of document IDs.
    """
    text_ids = []
    # log(f"len(results): {len(results)}")
    for ent1, rel, ent2 in triplet_list:
        triplet = [item._properties['name'] for item in [ent1, rel, ent2]]
        fuzzy_intersection = neo4j_get_fuzzy_intersection_score(triplet, question)
        r_textids = list(set(rel._properties["textids"]))    

        # increase corresponding docid count by their score. equivalent to weighting the docid when applying Counter
        text_ids.extend(r_textids * fuzzy_intersection)

    ###### Re-Rank by frequency  #################################
    textid_counter = Counter(text_ids)
    topk = len(textid_counter) if topk == -1 else topk

    ### Scoring of doc_id by frequency.    
    text_ids = [(k, v) for k, v in textid_counter.most_common(topk)]
    return text_ids


def dbsql_fetch_text_by_doc_ids(db_path="./ztmp/db/db_sqlite/datasets.db",
                                table_name: str = "agnews",
                                text_ids: list = None) -> list:
    """Fetches text from a local SQLite database based on given document IDs.

    Args:
        db_name (str):  name of SQLite database file.     : "datasets.db".
        table_name (str):  name of table in database.     : "agnews".
        text_ids (list):  list of text IDs to fetch text for.     : None.

    Returns:
        list: A list of text strings corresponding to fetched document IDs.

    """
    conn = sqlite3.connect(f"{db_path}")
    c = conn.cursor()

    text_ids = tuple([str(text_id) for text_id in text_ids])
    if len(text_ids) == 1:
        query = f"SELECT text_id, text FROM {table_name} WHERE text_id = '{text_ids[0]}'"
    else:
        query = f"SELECT text_id, text FROM {table_name} WHERE text_id IN {text_ids}"
    # log(query)
    c.execute(query)

    # log(doc_ids)
    # query = f"SELECT id, text FROM {table_name} WHERE id IN {doc_ids}"
    headers = c.description
    results = c.fetchall()
    # zip headers with results
    results = [{headers[i][0]: row[i] for i in range(len(headers))} for row in results]
    # convert results to dict
    conn.close()
    # sort by original order of text_ids
    results = sorted(results, key=lambda x: text_ids.index(x["text_id"]))
    return results


def dbsql_fetch_text_by_doc_ids_sqlachemy(db_name="sqlite:///ztmp/db/db_sqlite/datasets.db",
                                          table_name="agnews", doc_ids=None, ):
    """Fetches text from a local SQL database based on given document IDs.

    Args:
        db_name (str):  name of SQLite database file.     : "datasets.db".
        table_name (str):  name of table in database.     : "agnews".
        doc_ids (list):  list of document IDs to fetch text for.     : None.

    Returns:
        list: A list of text strings corresponding to fetched document IDs.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.sql import select, column, table
    engine = create_engine(db_name)
    Session = sessionmaker(bind=engine)
    session = Session()

    # doc_ids     = tuple(doc_ids)  # Ensure doc_ids is a tuple
    # query_table = table(table_name, column('id'), column('text'))
    # query       = select([query_table]).where(column('id').in_(doc_ids))

    doc_ids = tuple([str(docid) for docid in doc_ids])  # Ensure doc_ids is a tuple
    raw_sql = text(f"SELECT id, text FROM {table_name} WHERE id IN :doc_ids")

    result = session.execute(raw_sql, {'doc_ids': doc_ids})
    results = [{column: value for column, value in zip(result.keys(), row)} for row in result.fetchall()]

    session.close()
    return results



############ Client    ####################################
def neo4j_get_client(cfg=None, user=None, passw=None):
    from neo4j import GraphDatabase
    URI = os.environ.get("NEO4J_URI", "neo4j://localhost:7687")
    # expects NEO4J_USERNAME and NEO4J_PASSWORD in env
    AUTH = (os.environ.get("NEO4J_USERNAME", "username"), os.environ.get("NEO4J_PASSWORD", "password"))
    return GraphDatabase.driver(URI, auth=AUTH)





#######  doc_id Storage  ###########################################################
def dbsql_table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    existing_tables = [row[0] for row in cursor.fetchall()]
    return table_name in existing_tables


def dbsql_create_table(conn, table_name):
    # conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            text_id VARCHAR(255) PRIMARY KEY,
            text TEXT
        )
    """)

    conn.commit()
    # conn.close()


def dbsql_save_records_to_db(dirin="ztmp/bench/norm/ag_news/*/*.parquet",
                             db_path="./ztmp/db/db_sqlite/datasets.db",
                             table_name="agnews", coltext="text",
                             colid="text_id", nrows: int = -1):
    """Saves records from a path of Parquet files to a local SQLite database.

    Args:
        dirin (str )     : path containing Parquet files.     : "ztmp/bench/norm/ag_news/*/*.parquet".
        db_path (str )   : path to SQLite database.     : "./ztmp/db/db_sqlite/datasets.db".
        table_name (str ): name of table in database.     : "agnews".
        coltext (str )   : name of column containing text. 
        colid (str )     : name of column containing text ID. 

    """
    df = pd_read_file(dirin)
    df = df[[colid, coltext]]
    # log(len(df))
    if nrows > 0:
        df = df[:nrows]
    # create mysqlite instance
    os_makedirs(db_path)

    conn = sqlite3.connect(f"{db_path}")
    if dbsql_table_exists(conn, table_name) is False:
        dbsql_create_table(conn, table_name)

    # record_df.to_sql(table_name, conn, if_exists="append", index=False)
    # df = df.rename(columns={colid: "id", coltext: "text"})
    df["text_id"] = df["text_id"].astype("string")
    df.drop_duplicates(subset=["text_id"], keep="first", inplace=True)
    df.to_sql(table_name, conn, if_exists="append", index=False, chunksize=1000)


def dbsql_create_conn(db_uri="sqlite:///ztmp/db/db_sqlite/datasets.db"):
    if "sqlite:///" in db_uri:
        from sqlalchemy import create_engine
        engine = create_engine(db_uri)
        return engine

    elif ".db" in db_uri:
        conn = sqlite3.connect(db_uri)
        return conn




######################################################################################################
#######  Query generator from KG db triplet ##########################################################
def kg_generate_questions_from_triplets(dirin="ztmp/bench/ag_news/kg_triplets/agnews_kg_relation_test.parquet",
                                        dirout="ztmp/bench/ag_news/kg_questions/agnews_kg_question.parquet",
                                        nrows: int = 1000, batch_size: int = 5):
    """ Generate questions based on triplets extracted from a file --> Send to LLM  --> Get the questions
        dirin: Input file path containing triplets
        dirout: Output file path to save generated questions

           text_id          ,    Triplets                , question generated
        12276780668924807370,Turner,parent organization,Federal Mogul,  --->  Who is the parent organization of Federal Mogul?
        12276780668924807370,Federal Mogul,subsidiary,Turner,   -->  What is the subsidiary of Turner?
        12083816893608411777,TORONTO,country,Canada,            -->  What is the capital of Canada?

    """
    df = pd_read_file(dirin)
    df = df[["text_id", "head", "type", "tail"]]  ### Triplet Format
    df = df.drop_duplicates()
    df = df[:nrows]


    dfall = pd.DataFrame(columns=["text_id", "head", "type", "tail", "question"])
    for i in range(0, len(df), batch_size):
        df_subset = df[i:i + batch_size]

        #### Example for LLM Prompt :  |head|type|tail   |head|type|tail   
        triplet_str = "\n".join([f"{'|'.join([row.head, row.type, row.tail])}" for row in df_subset.itertuples()])

        #### Send Prompt + Triplets reference --> Generate questions from those triplets.
        prompt = f"For each triplet, generate a question based on triplet(head|type|tail):\n{triplet_str}"


        #### log(f"prompt: {prompt}")
        time.sleep(.6)  # sleep added to prevent ratelimiting
        response = llm_get_answer(prompt, model="gpt-3.5-turbo", max_tokens=1000)
        questions = response.split("\n")
        # log(f"questions: {questions}")


        #### clean up : remove preceeding numerical number
        questions = [q.split(".")[1].strip() if "." in q else q for q in questions]
        if len(questions) == len(df_subset):
            df_subset["question"] = questions
            dfall = pd.concat([dfall, df_subset])

    pd_to_file(dfall, dirout)
    # pd_to_file(dfall, dirout, index=False)  #### only for csv



######################################################################################################
#######  Metrics /benchmark ##########################################################
def metrics_kg_is_triplet_covered(triplet_tuple, question, answer):
    return all([k in question or k in answer for k in triplet_tuple])


def kg_benchmark_queries(dirin="ztmp/kg/data/agnews_kg_question.parquet",
                         dirout="ztmp/kg/data/agnews_kg_benchmark.parquet",
                         queries=1000):
    """
    Average time taken per query: 1.82 seconds
        Accuracy: 80% 

    """
    question_df = pd_read_file(dirin)
    result = []
    for row in question_df[:queries].itertuples():
        s_time = time.time()
        response = nebula_db_query(query=row.question)
        dt = time.time() - s_time

        is_correct = metrics_kg_is_triplet_covered([row.head, row.tail], row.question, response)
        result.append([row.question, response, dt, is_correct])

    df = pd.DataFrame(result, columns=["question", "response", "dt", "is_correct"])
    pd_to_file(df, dirout, index=False, show=1)
    log(f" Average time taken: {df.dt.mean():.2f} seconds")
    log(f" Percentage accuracy: {df.is_correct.mean() * 100:.2f} %")


######################################################################################################
#######  DB Nebula Graph #############################################################################
def test_nebula_db_insert_triplet_file():
    """ A function to test if data is inserted into KKG DB

    """
    # check if data is inserted
    space_name = "test_kg_relation"
    client = nebula_db_get_client()
    nebula_db_create_schema(client=client, space_name=space_name)
    time.sleep(10)

    resp = client.execute(f"USE {space_name};")
    nebula_db_insert_triplet_file(dirin="data/kg_relation.parquet", space_name=space_name, nrows=10)
    time.sleep(10)

    resp_json = client.execute_json(f"MATCH (s)-[e]->(o) RETURN count(e) as count;")
    json_obj = json.loads(resp_json)
    # {'errors': [{'code': 0}], 'results': [{'spaceName': 'test_kg_relation', 'data': [{'meta': [None], 'row': [10]}], 'columns': ['count'], 'errors': {'code': 0}, 'latencyInUs': 4081}]}
    assert json_obj["results"][0]["data"][0]["row"][0] == 10
    # drop space
    resp = client.execute(f"DROP SPACE {space_name};")


def nebula_db_get_client(engine_name="nebula"):
    config = Config()
    connection_pool = ConnectionPool()
    assert connection_pool.init([('127.0.0.1', 9669)], config)
    # get session from  pool
    client = connection_pool.get_session('root', 'nebula')
    assert client is not None
    return client


def nebula_db_create_schema(client=None, space_name="kg_relation"):
    if client is None:
        client = nebula_db_get_client()
    resp = client.execute(
        f"CREATE SPACE {space_name}(vid_type=FIXED_STRING(256), partition_num=1, replica_factor=1);"
        f"USE {space_name};"
        "CREATE TAG entity(name string);"
        "CREATE EDGE relationship(relationship string);"
        "CREATE TAG INDEX entity_index ON entity(name(256));"
    )
    assert resp.is_succeeded(), resp.error_msg()


def nebula_db_insert_triplet(client=None, space_name="kg_relation", row=None):
    """
    Findings:
    https://docs.nebula-graph.io/2.6.1/3.ngql-guide/3.data-types/6.list/#opencypher_compatibility
    A composite data type (i.e., set, map, and list) CAN NOT be stored as properties for vertices or edges.
    It is recommended to modify graph modeling method.  composite data type should be modeled as an adjacent edge of a vertex, rather than its property. Each adjacent edge can be dynamically added or deleted.  rank values of adjacent edges can be used for sequencing.


    """
    resp = client.execute(f"USE {space_name};")
    assert resp.is_succeeded(), resp.error_msg()

    vertex_query = f"""INSERT VERTEX entity(name) VALUES "{row.head}":("{row.head}"), "{row.tail}":("{row.tail}")"""
    # log(vertex_query)
    resp = client.execute(vertex_query)
    assert resp.is_succeeded(), resp.error_msg()

    # edge query
    edge_query = f"""INSERT EDGE relationship(relationship) VALUES "{row.head}"->"{row.tail}":("{row.type}")"""

    # log(edge_query)
    resp = client.execute(edge_query)
    assert resp.is_succeeded(), resp.error_msg()


def nebula_db_insert_triplet_file(dirin="data/kg_relation.parquet", space_name="kg_relation", nrows: int = -1):
    """

    """
    df = pd_read_file(dirin)
    nrows = len(df) if nrows < 0 else nrows

    # create nebula client
    client = nebula_db_get_client()
    assert client is not None

    log("#### create schema ")
    client.execute(f"""USE {space_name};""")

    log("#### insert ")
    for row in df[:nrows].itertuples():
        nebula_db_insert_triplet(client=client, space_name=space_name, row=row)


##############  Query DB   
def nebula_db_query(space_name="agnews_kg_relation", query="", db_type="nebula"):
    """A function to query knowledge graph database with specified space name and query string.

    LlamaIndex uses LLM GPt3.5
          Naturaal Query ---> KG Nebula queries.
          Required OPENAI TOKEN in env variable.
          
        Digged deeper into llama-index query calls.
        For each query it is calling llm 2 times:
        1. Extract keywords from llm query
        2. Fetch answer from db output triplets


    Issues: LLM is called every time to convert Natural Queries --> KG Nebula queries

            Find a way to generate Nebula query from llama Index.



    Args:
    - space_name (str):  name of space in knowledge graph database to query.
    - query (str):  query string to search in knowledge graph.

    """
    from llama_index.core import KnowledgeGraphIndex, StorageContext
    from llama_index.graph_stores.nebula import NebulaGraphStore

    if not query:
        return

    edge_types, rel_prop_names = ["relationship"], ["relationship"]
    tags = ["entity"]

    ### Init Databse
    # expects NEBULA_USER, NEBULA_PASSWORD, NEBULA_ADDRESS in environment variables
    graph_store = NebulaGraphStore(
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,

    )
    # create storage context
    storage_context = StorageContext.from_defaults(graph_store=graph_store, )

    # fetch KG database index
    index = KnowledgeGraphIndex.from_documents(
        [],
        storage_context=storage_context,
        max_triplets_per_chunk=2,
        space_name=space_name,
        edge_types=edge_types,
        rel_prop_names=rel_prop_names,
        tags=tags,
    )
    query_engine = index.as_query_engine()

    # llm call here. adds network overhead to each query
    ### LLM is called to generate Natural query --> KG Query
    response = query_engine.query(query)
    return response.response


###################################################################################################
if __name__ == "__main__":
    import fire

    fire.Fire()
    # results = neo4j_search_triplets_bykeyword(db_name="neo4j", keywords=["Casio Computer", 'magazine', 'United States'])
    # log(results)
    # df = pd_read_file("ztmp/bench/norm/ag_news/test/df_1.parquet")
    # log(df["id"])

