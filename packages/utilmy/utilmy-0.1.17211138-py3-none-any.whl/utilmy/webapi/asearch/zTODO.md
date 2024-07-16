

```python


#### DONE
   benchmark and calcualte accuracy for all retrieval engine. --> CSV reports.



#### Knowledge Graph Queries: 

   https://github.com/wenqiglantz/llamaindex_nebulagraph_phillies/tree/main

   https://towardsdatascience.com/12-rag-pain-points-and-proposed-solutions-43709939a28c





#### Fine Tune Embedding
https://docs.llamaindex.ai/en/stable/examples/finetuning/embeddings/finetune_embedding/







### TODO 2

   1)  text --> Classifier into mutiple labels.
              NER extractions
              Graph relation extractions




   2) Aggregate data from many sources: 

       (example   ) --->   Generate Text Description.

    

  Fine tuning GPT-4








### Current TODO
    qdrant in binary : Works in linux, Done

    Eval : 
       Better queries for better testing.

       1) synthetic query from raw text
           use Plain LLM GPT-3

           Give to GPT-3.5 LLlama the text,  PRompt:generate 10 different questions about this
                Qwen


           Output is dataframe and save on disk as parquet
             id_global,    body,    query_list_gpt3
               text_id          Text       "@@".join(    ) 

           100 text ---> 10 queries 

          prompt constraints: 
              Online tool to generate/save prompt.
              (very specific to the News article,..)

              Question has to be specific.

         Ask   www.phind.com 


          Hack to use GPT-4 for free as API (low volume, kind of slow...)
          Skype ---> I hack to use GPT-4 Co-pilot in skype
              query/
              Edge co-pilot the browser  -->

        Make quick and dirty (at least working)
        query.py


             DSPY.py https://dspy-docs.vercel.app/docs/intro


-----------------------------------------------------------------------------------------
      2) Do the retrieval using engin.py and save the top-k in parquet files.

      3)  
       Different type of Eval:

         A) Simple eval metrics: accuracy in top-K with synthetic queries.
               But, what will happebd: query is generic, other document may be valid ...  






#### New models :
    github.com//abstractive_text_summarization/blob/main/notebooks/Text_summarization_pre_processing_and_training.ipynb






-----------------------------------------------------------------------------------------
         B) Evaluate the quality of retrieval using LLM
             Create a prompt:

            """" you are an expert ...
             You have the query and the answer and analyze the 
                 reply by yes or no..

                query:  { XXXXXXX }

                Answer: { YYYYYYY  }
            """ 

            Ask the LLM if the answer replies correctly with the with query and explain why in step by step.
                    Yes or NO
                    explain why

            GPT-4 Level.







#### At the Search querytime   : what happening, processing pipeline
               Sparse,       

        Queries ambiguity/ User intention ambiguity:

         query --> Process the query. 
         A) Query Enhancement process : add more data to initial queries more acccurate.
             query = Find article about Obama predisent when he visited Europe.
 
             1) Classifer (BERT, sentence transformer,...)
                User Intent -->  Bert Classifier --> category : news_type: business, sport,...
                                      information,
                                      politics, Sports, ...  (pre-defined category)

                            -->  NER extraction (most imporant) : news
                                     Person, Date, event, ....

                             
                Ex: Find article about Obama predisent when he visited Europe.
                     NER --->  (Obama, person
                               (Europe, geo-area)

                     Classifier:  find news article.

                Spacy:
                   Keyword extraction :  Obama, president, Europe, visit, article.  


             2) Rephrase the query: (Small LLM or T5-Flan Google)
                  QueryNew ---> Obama preident when  visited Europe.     (Dense, Sparse)
                                                     
                ...


         B) Re-format the query + New meta-data into search API (tantivy, Dense)
               Qdrant has category filtering...  ---> more accurate. ... OR   OR ...
      

         C)
           1 query --->  Multiple queries to enlarge the retrieval (most)
                     by LLM or by rule based using meta-data.
           
                   --->  Launch Multiple search at same time  ( in parallel, 
                   --->  Many results ---> Merge them (re-ranking) --> Top-K









### Raw TODO (to be discussed):
   Use qdrant server binary file instead of Docker : 
     --> Binary file (for linux, Macos):
     --> Run by command line (in github action --> test it)
        https://github.com/qdrant/qdrant/releases

        Assets 10
        qdrant-aarch64-apple-darwin.tar.gz

        Run the qdrant server using only the binary file (not the docker....)
          make the config.

        ### bash 
           ./qdrant_server  "localhost:6339"

          Our engine code.py and Qdrant Server on the SAME docker:  
                Inside same docker: localhost is inside the docker.... faster, no network latency.

          Big Machine: 64GB
                Many engine.py  processor, 1 single qdrant in same Docker.    



  4) More real world queries : ( not just a substring ).
        Query Generator (ie LLM model to rephrase substring, like GPT 3, ).
               String  --> correct query. (reverse from answer)

        Inverse : Answers --> Many queries: 

        Generating Better Eval dataset.


  5) Chunk the initial dataset in chunk.py
      50% done,


  6) Am re-Normalizing the dataset : For many task: Fine Tuning after)
         data.py
         Google Drive:   in parquet file.

        ### Actual data
        /hf_data/data/{url_name_unique}/train/
        /hf_data/data/{url_name_unique}/test/

        #### Meta
        /hf_data/meta/{url_name_unique}/meta.json


    ### All column are SAME NAME :
        ("id_global",  "int64", "global unique ID"),
        ("id_dataset", "int64", "global unique ID of the dataset"),

        ("id_local", "int64", "local ID"),
        ("dt", "float64", "Unix timestamps"),

        ("title", "str", " Title "),
        ("summary", "str", " Summary "),
        ("body", "str", " Summary "),
        ("info_json", "str", " Extra info in JSON string format "),

        ("cat1", "str", " Category 1 or label "),
        ("cat2", "str", " Category 2 or label "),
        ("cat3", "str", " Category 3 or label "),
        ("cat4", "str", " Category 4 or label "),
        ("cat5", "str", " Category 5 or label "),




   Chunking of raw News Text into smaller size: >100 sentences --> split by 5-10 sentences (paagrap)


 ### After we get better Eval queries/datasets:
  3) Analysis WHY Dense are failing.

  5) Retrieval from questions:
       1 Single Question --> Rephrase the question --> many similar questions Q1, Q2, Q3,...
           --> RAG for each of the question.
           --> Merge all retrieval (ie duplicate, are higher score)

       Rephrase the question from QUESTION INTO  Affirmative sentence.
           Retrieval : Same type of sentence, to have consistent.    



  6) Use Knowdlege Graph retrieval LLamaIndex
        Additional engine.
        https://docs.llamaindex.ai/en/stable/examples/query_engine/knowledge_graph_query_engine/ 



  7) Test the Fusion retrieval : Better Eval queries/dataset.







#############################################









```






