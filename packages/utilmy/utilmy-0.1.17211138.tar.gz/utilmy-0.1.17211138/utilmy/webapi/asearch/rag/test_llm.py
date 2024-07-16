from rag.llm import LLM


if __name__ == '__main__':
    llm1 = LLM('openai', 'gpt-3.5-turbo')
    prompts = ["What is capital of Germany?",
               "What is capital of France?",
               "What is capital of Spain?"]
    # llm1.get_save_bulk(prompts, dirout="ztmp/gpt_out/")
    llm1.get_save(prompts[0], dirout="ztmp/gpt_out/")