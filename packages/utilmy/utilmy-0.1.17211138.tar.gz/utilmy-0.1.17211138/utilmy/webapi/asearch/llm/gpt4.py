""" 


Fact Checking generation,

2) Have this interestsing idea: 
 2 steps generation

Step 1 ;  Prompt + {RAG_context}. --> generate text1  using only from RAG context

Steps 2:  Prompt + {generate_Text1}    + {Rag_context} and Ask LLM to Map:
            sentence from text1. --> fact in Rag context...

           --> As Fact checker.

           

##########################################################



###Prompt optimization

   https://www.microsoft.com/en-us/research/blog/sammo-a-general-purpose-framework-for-prompt-optimization/


   https://microsoft.github.io/autogen/docs/topics/handling_long_contexts/compressing_text_w_llmligua


###### Graph RAG
    https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/

    https://pypi.org/project/graphrag/0.0.0/#files

    https://github.com/Joshua-Yu/graph-rag/tree/main


    Details 
    Reaodning,



#### Graph Retrieval:
    https://pypi.org/project/GraphRetrieval/#description




#### Hallucination
   ##### Self Check GPT:
     https://github.com/arita37/selfcheckgpt


     https://github.com/arita37/crosscheckgpt-dev

   https://github.com/McGill-NLP/FaithDial


   ### Amazon Ref checker using KG graph
   https://www.amazon.science/code-and-datasets/refchecker
     


###########
    Why LLm hallucinates ? 
        Probabilitics model.
        Associative generation.

     How people human people reduce hallucination ?
       fact checking
         -> logical Reasoning over graph
         --> Connected graph : Ground knowledge + basic graph connection.









Long text generation

Sliding


https://github.com/junruxiong/IncarnaMind




To generate long text sequences using GPT-3 with a sliding window and Retrieval-Augmented Generation (RAG), follow these steps:

Chunk and Index: Break down your knowledge base into manageable chunks (e.g., paragraphs or sections) and index these using a vector database to facilitate efficient retrieval. This step is crucial for RAG's retrieval phase to function effectively.
Sliding Window for Retrieval: Implement a sliding window mechanism on your input text to handle long inputs that exceed GPT-3's token limit. For each window, retrieve relevant context from your indexed knowledge base. This can be done by matching semantic content of text window with indexed chunks using vector similarity.
Merge and Generate: Use retrieved chunks to augment input to GPT-3, ensuring that context for generation is both relevant and concise. This might involve some preprocessing to integrate input window with retrieved content smoothly.
Iterate: Move window across input text, repeating retrieval and generation steps. Each new window should slightly overlap with previous one to maintain context continuity.
Post-process: After generating text for each window, merge outputs. Handle overlaps intelligently to ensure text is coherent and there are no abrupt transitions or repetitions.
This approach leverages strengths of GPT-3 in generating coherent text while using RAG to ensure content is contextually enriched and accurate, addressing limitations of GPT-3's fixed input size. For more details on implementing RAG with GPT-3, refer to Hugging Face Transformers library, which supports integration with external knowledge sources and custom retrieval mechanisms.





{"prompt": "Input text 1", "completion": " Expected output 1"}
{"prompt": "Input text 2", "completion": " Expected output 2"}




import openai

openai.api_key = 'your-api-key'

# Upload dataset
response = openai.File.create(
  file=open("path_to_your_file.jsonl"),
  purpose='fine-tune'
)
file_id = response['id']

# Create a fine-tuning job
fine_tune = openai.FineTune.create(
  training_file=file_id,
  model="gpt-3.5-turbo",
  n_epochs=4
)

print(f"Fine-tuning job started with ID: {fine_tune['id']}")







"""

import openai

def generate_long_text(prompt, max_length):
    openai.api_key = 'your-api-key'
    response = openai.Completion.create(
        engine="text-davinci-002",  # Replace with gpt-4 when available in your API
        prompt=prompt,
        max_tokens=4096
    )
    generated_text = response.choices[0].text.strip()
    total_generated = [generated_text]

    while len(' '.join(total_generated)) < max_length:
        new_prompt = ' '.join(total_generated)[-2048:]  # Use last 2048 tokens as new prompt
        response = openai.Completion.create(
            engine="text-davinci-002",  # Replace with gpt-4 when available in your API
            prompt=new_prompt,
            max_tokens=4096
        )
        generated_text = response.choices[0].text.strip()
        total_generated.append(generated_text)

    return ' '.join(total_generated)

# Example usage
long_text = generate_long_text("Once upon a time, in a land far, far away,", 10000)
print(long_text)





from llama_index import GPT4, RAG, RollingSequentialPrompt

# Initialize GPT-4 model
gpt4 = GPT4(api_key='your_openai_api_key')

# Initialize RAG (Retrieval-Augmented Generation)
rag = RAG(model=gpt4)

# Define a rolling sequential prompt
rolling_prompt = RollingSequentialPrompt(
    model=gpt4,
    prompt_template="Continue story: {text}",
    max_tokens=1000  # Adjust as needed
)

# Function to generate long text
def generate_long_text(initial_text, num_iterations=5):
    text = initial_text
    for _ in range(num_iterations):
        response = rolling_prompt.generate(text)
        text += response['choices'][0]['text']
    return text

# Example usage
initial_text = "Once upon a time in a land far, far away,"
long_text = generate_long_text(initial_text)
print(long_text)









from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(api_key="<you openAI API Key>")

# Function to perform Named Entity Recognition (NER)
def perform_ner(text):
    # Define prompt for NER task
    prompt = """
    
    You are an expert on recognising Named entities. I will provide you short sentences and you will respond all entities you find. Return entities clasified in four types:
    PER for persons such as Bill Clinton, Gauss, Jennifer Lopez
    LOC for locations such as California, Europe, 9th Avenue
    ORG for organizations such as Apple, Google, UNO
    MISC any other type of entity you consider that do not fits in beforementioned cases. 

    Respond in JSON format. 

    For example:

    "google and apple are looking at buying u.k. startup for $1 billion"

    response:

    {"entities": [
    {"name": "google", "type": "ORG"},
    {"name": "apple", "type": "ORG"},
    {"name": "u.k.", "type": "MISC"}
    ]}
    
    """

    # Generate completion using OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": text}
        ],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0
    )

    # Extract and return entities from response
    
    entities = response.choices[0].message.content.strip()
    return json.loads(entities)

# Function to receive new text and return NER JSON
def get_ner_json(new_text):
    # Perform NER on new text
    entities = perform_ner(new_text)
    return entities

# Example new text
new_text = "I went to Paris last summer and visited Eiffel Tower."

# Get NER JSON for new text
ner_json = get_ner_json(new_text)
print(json.dumps(ner_json, indent=2)