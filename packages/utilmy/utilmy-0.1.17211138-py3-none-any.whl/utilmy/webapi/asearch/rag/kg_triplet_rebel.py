""" Fine Tuner of Triplet generator using Rebel model
    Usage:

        alias pyrebel="python3 -u rag/rebel_train.py "

        # prepare fine-tuning dataset
            pyrebel data_norm_fakelabel --dirin 'ztmp/bench/norm/ag_news/train/df_1.parquet' --dirout 'ztmp/kg/train/ft_data.csv'
        

        # train
            pyrebel  run_train --dirtrain 'ztmp/kg/train/ft_data.parquet' --dirout "./ztmp/out/rebel_finetune"



    Dataset Label Sample:
        https://huggingface.co/Babelscape/rebel-large

        text: "European Union Extends Microsoft-Time Warner Review BRUSSELS, Belgium (AP) -- European antitrust regulators said Monday they have extended their review of a deal between Microsoft Corp. (MSFT) and Time Warner Inc...",
        label: <s><triplet> European Union Extends Microsoft-Time Warner Review <subj> antitrust regulators <obj> instance of <triplet> BRUSSELS <subj> Belgium <obj> country <triplet> Belgium <subj> BRUSSELS <obj> capital</s>
        <s> =>start,
        </s> => end,
        <triplet> => start of triplet,
        <subj> => denotes preceeding string to be subject,
        <obj> => denotes preceeding string to be object

        text: "Patriots Sign Top Pick Watson (Reuters) Reuters - New England Patriots\Monday announced signing of first-round draft pick Benjamin\Watson. As per team policy, terms of tight end's deal were\not released."
        label: <s><triplet> Benjamin\Watson <subj> New England Patriots <obj> member of sports team</s>


    Findings:
                "This is a multilingual version of REBEL(rebel-large). It can be used as a standalone multulingual Relation Extraction
                system, or as a pretrained system to be tuned on multilingual Relation Extraction datasets."
                - mrebel-base hf page

                If we are to stick to English for now, I think we should train, finetune rebel-large.
                model size:
                mrebel-base: 484M params
                rebel-large: 406M params
                So rebel-large is smaller than mrebel-base.

                https://huggingface.co/Babelscape/mrebel-base/discussions/2
                Babelscape/mrebel-base · mrebel-base output interpretation



    Infos:
        https://arxiv.org/pdf/2310.00696

        https://aclanthology.org/2021.findings-emnlp.204.pdf


   Otther models

    
      https://github.com/wtangdev/unirel

      https://paperswithcode.com/sota/relation-extraction-on-nyt?p=rebel-relation-extraction-by-end-to-end

      2023-06-01
         Add multi-token entity implementation.
         Provide UniRel class in predict.py for easy inference and a checkpoint trained on nyt (multi-token) for trying.



       Recent models for triplet entity relation extraction from text include:
        ZETT (Zero-shot Triplet Extraction via Template Infilling): This model uses a template infilling approach for zero-shot triplet extraction, leveraging pre-trained language models like T5 to fill in entity placeholders within a given template without requiring synthetic training data for unseen relations 3.

        Query-based Instance Discrimination Network: Focuses on relational triple extraction by distinguishing between different instances of relations in text, enhancing the extraction accuracy and handling multiple relations simultaneously 2.

        REKnow: A generative model that sequentially generates relational triplets and utilizes knowledge from Knowledge Graphs to resolve ambiguities in relation extraction tasks 2.

        EnriCo (Enriched Representation and Globally Constrained Inference for Entity and Relation Extraction): Combines enriched representations with globally constrained inference to improve the accuracy of joint entity and relation extraction 2.

        For more details on these models and their implementations, you can refer to the respective sources:

            ZETT on Megagon Labs
            Papers with Code - Joint Entity and Relation Extraction


       ##### Textual Graph Query /Answer

         https://arxiv.org/html/2402.07630v3

         



"""
if "Import":
    import json,re, os, pandas as pd, numpy as np,copy
    from dataclasses import dataclass
    from typing import Optional, Union
    from box import Box
    import fire

    from functools import partial
    import datasets 
    from datasets import Dataset, load_metric
    # If issue dataset: please restart session and run cell again
    from transformers import (
        TrainingArguments,
        Trainer,

        AutoTokenizer,
        AutoModelForTokenClassification,  #### NER Tasks
        AutoModelForSeq2SeqLM, 

        ### LLM
    )
    from transformers.tokenization_utils_base import PreTrainedTokenizerBase, PaddingStrategy

    import spacy, torch
    from utilmy import (date_now, date_now, pd_to_file, log, pd_read_file, json_save, 
                        config_load, pprint,)


    ### Local asearch PTYHONPATH="$(pwd)"
    from  utils.util_exp import (exp_create_exp_folder, exp_config_override, exp_get_filelist)
    from  utils.utils_base import torch_getdevice
    import evaluate
    from sklearn.metrics._scorer import metric








################################################################################################
#### Global for Jupyter/
def model_init(model_name="Babelscape/rebel-large"):
    global device, tokenizer, model
    device = torch_getdevice()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.to(device)

    metric = evaluate.load('accuracy')

    return model, tokenizer, metric


################################################################################################
def data_norm_fakelabel(dirin='ztmp/bench/norm/ag_news/train/df_1.parquet',
                        dirout="ztmp/kg/train/ft_data.parquet",
                        model_name="Babelscape/rebel-large",
                        batch_size=8, nrows=-1):
    """Generate a fine-tuning dataset for training a language model.

        python3 -u rag/rebel_train.py  run_train --dirin 'ztmp/kg/train/ft_data.parquet' --dirout "./ztmp/out/rebel_finetune"

        Args:
            dirin (str):  input  path containing  dataset in parquet format.
            dirout (str):  output  path to save  fine-tuning dataset in CSV format.
            batch_size (int):  number of rows to process in each batch.     : 8.
            nrows (int):  number of rows to process. If -1, processes all rows.

        Returns:
            None

        generates triplets based on  text using  rebel-base, and saves the
        dataset consists of
        two columns: 'text' and 'labels'.  
            'text' column contains  input text,
            'labels' column contains  output text generated by rebel-base.

        Example usage:
            data_norm_fakelabel(dirin='path/to/input/dataset.parquet', dirout='path/to/output/dataset.csv')
    """
    result_df = pd.DataFrame(columns=["text", "labels"])

    model, tokenizer, metric = model_init(model_name=model_name)

    df = pd_read_file(dirin)
    if nrows == -1:
        nrows = len(df)
    # result_df = df[:nrows]
    # generate triplets based on text using rebel-base
    ft_text = []
    ft_output = []
    for i in range(0, nrows, batch_size):
        df_subset = df[i:i + batch_size]
        text = df_subset['body'].tolist()
        ft_text.extend(text)
        output_text = rebel_generate_tripletlabel(model, tokenizer, text)
        ft_output.extend(output_text)

    result_df["text"] = ft_text
    result_df["labels"] = ft_output
    pd_to_file(result_df, dirout)


def run_train(dirtrain="ztmp/kg/train/ft_data.parquet",
              dirval=None,
              dirout='./ztmp/out/rebel_finetune/', nrows=-1):
    model, tokenizer, metric = model_init(model_name="Babelscape/rebel-large")

    ds_train = data_tokenize_split(dirtrain, tokenizer, nrows=nrows)

    if isinstance(dirval, str):
        ds_val = data_tokenize_split(dirval, nrows=nrows)
    else:
        # split dataset into train and test
        ds = ds_train.train_test_split(test_size=0.1)
        ds_train = ds["train"]
        ds_val = ds["test"]

    training_args = TrainingArguments(output_dir=dirout)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds_train,
        eval_dataset=ds_val
    )
    trainer.train()
    trainer.save_model(f"{dirout}/model")


####################################################################################################
def data_tokenize_split(dirin='ztmp/kg/train/ft_data.parquet', tokenizer=None, nrows=10):
    """ 
    dataset_hf = raw_dataset.map(lambda x:
                                 {'input_ids': tokenizer(x['text'], truncation=True, padding=True)[
                                     "input_ids"],
                                  "attention_mask":
                                      tokenizer(x["text"], truncation=True, padding=True)[
                                          "attention_mask"],
                                  'labels': tokenizer(x["labels"], truncation=True, padding=True)[
                                      "input_ids"]}
                                 )


    # map input_ids and attention mask via single call per text
    # train_data = ds.map(
    #     lambda x: {k: v for k, v in tokenizer(x['text'], truncation=True, padding=True, max_length=max_length).items()
    #                if k in ['input_ids', 'attention_mask']},
    #     batched=True, remove_columns=['text'])

    """
    if tokenizer is None:
        _, tokenizer, _ = model_init(model_name="Babelscape/rebel-large")

    df = pd_read_file(dirin)
    ###  text: 
    ###  labels:  "__en__ __sv__ BRUSSELS       __vi__ Belgium        __tn__ country</s>"
    df = df[["text", "labels"]]

    df = df[:nrows]
    ds = Dataset.from_pandas(df)
    # raw_dataset = raw_dataset.train_test_split(test_size=0.1)
    max_length = 128

    # def zzz_preprocess_func(row):
    #     #### Text tokenizer
    #     row_ddict = tokenizer(row["text"], truncation=True, padding=True, max_length=max_length,
    #                           return_offsets_mapping=False,
    #                           return_overflowing_tokens=False)
    #
    #     # out["labels"] = row["labels"]
    #     # log(out)
    #     # output["input_ids"] = output.pop("input_ids")  # Add input_ids to  output
    #     return row_ddict

    # ds = ds.map(preprocess_func, batched=True, remove_columns=['text', 'labels'])

    def prepro_text(x):
      return {k: v for k, v in tokenizer(x['text'], truncation=True, padding=True, max_length=max_length).items()
                   if k in ['input_ids', 'attention_mask']}

    train_data = ds.map(lambda x:  prepro_text(x), batched=True, remove_columns=['text'])



    # set labels to their input_ids
    def prepro_label(x):
      return {"labels": v for k, v in tokenizer(x['labels'], truncation=True, padding=True).items() if
                   k in ['input_ids']}

    train_data = train_data.map(lambda x: prepro_label(x),batched=True)
    return train_data


##########################################################################################
def rebel_generate_tripletlabel(model, tokenizer, text: list) -> list:
    """ 
        Label format : 

    """
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt").to(model.device)
    outputs = model.generate(inputs['input_ids'])
    result = tokenizer.batch_decode(outputs, skip_special_tokens=False)
    result = [res.replace("<pad>", "") for res in result]
    # print(result)
    return result


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


if __name__ == '__main__':
    fire.Fire()

"""### infos 

    ####Logs output:


        Special tokens have been added in vocabulary, make sure associated word embeddings are fine-tuned or trained.
        Map: 100%|██████████████████████████████████████████████| 7/7 [00:00<00:00, 1606.31 examples/s]
        Map: 100%|██████████████████████████████████████████████| 7/7 [00:00<00:00, 1967.31 examples/s]
        {'train_runtime': 2.3199, 'train_samples_per_second': 7.759, 'train_steps_per_second': 1.293, 'train_loss': 7.620423634847005, 'epoch': 3.0}
        100%|████████████████████████████████████████████████████████████| 3/3 [00:02<00:00,  1.29it/s]
        Some non-default generation parameters are set in model config. These should go into a GenerationConfig file (https://huggingface.co/docs/transformers/generation_strategies#save-a-custom-decoding-strategy-with-your-model) instead. This warning will be raised to an exception in v4.41.
        Non-default generation Args: {'max_length': 200, 'num_beams': 5}

    ##### Sample data

        ,text,labels
        0,"European Union Extends Microsoft-Time Warner Review BRUSSELS, Belgium (AP) -- European antitrust regulators said Monday they have extended their review of a deal between Microsoft Corp. (MSFT) and Time Warner Inc...",
             __en__ __sv__ BRUSSELS __vi__ Belgium __tn__ country</s>
        
        1,"Patriots Sign Top Pick Watson (Reuters) Reuters - New England Patriots\Monday announced signing of first-round draft pick Benjamin\Watson. As per team policy, terms of tight end's deal were\not released.",
            __en__ __sv__ Pick Watson __uk__ New England Patriots __vi__ member of sports team</s>
        
        2,"Olympics: Thorpe Beats Phelps as U.S. Fights Gold Gap  ATHENS (Reuters) - Australian swimmer Ian Thorpe beat  arch-rival Michael Phelps in men's 200-meter freestyle on  Monday as United States pursued China, Australia and Japan  in medals table on day three of Olympic Games.",
            __en__ __sv__ Ian Thorpe __uk__ swimmer __zu__ sport __sv__ Michael Phelps __uk__ swimmer __zu__ sport</s>

        3,"U.S. Awaits Judgment on Venezuela Voting (AP) AP - There was no evident pattern of fraud in Venezuela's balloting that left President Hugo Chavez in office but a final judgment depends on what observers report, State Department said Monday.",
            __en__ __sv__ Hugo Chavez __uk__ Venezuela __tn__ country of citizenship</s>


        4,"Bush, Kerry Press for Women's Votes (AP) AP - Elizabeth Burnosky is a registered Democrat who voted for President Bush in 2000, opposes his policy on Iraq and calls Sen. John Kerry ""a little wussy boy."" Call her conflicted.","__en__ __sv__ Bush, Kerry Press for Women's Votes __uk__ Democrat __zu__ member of political party</s>"
        5,"Insurers face massive storm bill Insurers are counting cost of Hurricane Charley in Florida, with early damage estimates reaching as high as \$14bn (7.6; 11bn euros).",__en__ __sv__ Hurricane Charley __tn__ Florida __tn__ located in administrative territorial entity</s>
        6,"Fischer Appeals to Powell to Help Him Renounce U.S. Citizenship Former chess champion Bobby Fischer announced plans Monday to marry a leading Japanese chess official and appealed to Secretary of State Colin Powell to help him renounce U.S. citizenship, latest in a series of moves as he seeks to block attempts to deport him to United States.",__en__ __sv__ Fischer Appeals to Powell to Help Him Renounce U.S. Citizenship Former chess __zu__ chess __zu__ sport __sv__ Bobby Fischer __uk__ chess __zu__ sport __sv__ Colin Powell __uk__ chess __zu__ sport</s>
        7,"Venezuela's Chavez Wins Recall Referendum  CARACAS, Venezuela (Reuters) - Venezuela's left-wing  President Hugo Chavez won a recall referendum on his divisive  rule in a vote backed on Monday by international observers who  found no ""element of fraud.\""",__en__ __sv__ Venezuela __tn__ Hugo Chavez __uk__ head of state __sv__ Hugo Chavez __uk__ Venezuela __tn__ country of citizenship</s>
        8,Halliburton Says Army Suspends Withhold Threat  WASHINGTON (Reuters) - Halliburton said on Monday U.S.  Army had decided to give company more time to resolve a  billing dispute before withholding payment of up to 15 percent  of company's bills in Iraq and Kuwait.,__en__ __sv__ Kuwait __tn__ Iraq __tn__ diplomatic relation</s>
        9,"Belo Takes Charge for Advertising Refunds  NEW YORK (Reuters) - Media company Belo Corp. &lt;A HREF=""http://www.investor.reuters.com/FullQuote.aspx?ticker=BLC.N target=/stocks/quickinfo/fullquote""&gt;BLC.N&lt;/A&gt; on  Monday said it would refund \$23 million to advertisers because  of a circulation scandal at its Dallas Morning News newspaper,  resulting in a charge against earnings in current quarter.",__en__ __sv__ NEW YORK (Reuters) __vi__ Dallas __tn__ headquarters location</s>
        10,"LifePoint to Buy Rival for \$1 Bln  NEW YORK (Reuters) - Rural hospital operator LifePoint  Hospitals Inc. &lt;A HREF=""http://www.investor.reuters.com/FullQuote.aspx?ticker=LPNT.O target=/stocks/quickinfo/fullquote""&gt;LPNT.O&lt;/A&gt; agreed to buy rival Province Healthcare  Co. &lt;A HREF=""http://www.investor.reuters.com/FullQuote.aspx?ticker=PRV.N target=/stocks/quickinfo/fullquote""&gt;PRV.N&lt;/A&gt; for \$1.03 billion in cash and stock to broaden its  geographic reach, companies said on Monday.",__en__ __sv__ LifePoint Hospitals Inc. __vi__ Rural hospital __zu__ industry</s>
        11,"Satellite TV Gains in Race Against Cable Thousands of Americans have defected to satellite TV as providers have reported hefty gains while cable industry has declined. Consumers likely will see aggressive marketing promotions in next six months as companies jockey for customers, analysts say.",__en__ __sv__ Satellite TV Gains in Race Against Cable __yo__ satellite TV __zu__ facet of</s>
        12,Columnists: Big Brother's Last Mile FCC's new ruling on broadband wiretaps will force customers to pay for privilege of making  Internet less secure.\,__en__ __sv__ broadband __zu__ wiretap __zu__ subclass of</s>
        13,"US to withdraw up to 70,000 troops from Europe and Asia: Bush (AFP) AFP - United States will withdraw up to 70,000 troops from Europe and Asia over next decade, President George W. Bush said, in a move aimed at increasing capability to fight ""war on terror"" and meet other new threats.",__en__ __sv__ George W. Bush __uk__ President __zu__ position held</s>
        14,"Thorpedo Sinks Phelps' Shot at Record ATHENS, Greece - kid couldn't catch Thorpedo - and he won't be catching Mark Spitz, either. Michael Phelps' quest for seven gold medals ended after just three events, doomed by another bronze Monday night in most anticipated race at Olympic pool - head-to-head showdown with Australia's Ian Thorpe in 200-meter freestyle...",__en__ __sv__ Ian Thorpe __uk__ Australia __tn__ country of citizenship</s>
        15,"AP: Group Finds Cave Linked to Baptist KIBBUTZ TZUBA, Israel - Archaeologists said Monday they have found a cave where they believe John Baptist anointed many of his disciples - a huge cistern with 28 steps leading to an underground pool of water.    During an exclusive tour of cave by Associated Press, archaeologists presented wall carvings they said tell story of fiery New Testament preacher, as well as a stone they believe was used for ceremonial foot washing...",__en__ __sv__ KIBBUTZ TZUBA __tn__ Israel __tn__ country</s>
        16,"Venezuela's Chavez Wins Recall Referendum (Reuters) Reuters - Venezuela's left-wing\President Hugo Chavez won a recall referendum on his divisive\rule in a vote backed on Monday by international observers who\found no ""element of fraud.\""",__en__ __sv__ Hugo Chavez __uk__ Venezuela __tn__ country of citizenship</s>
        17,"Private Firms to Buy Intelsat for \$3 Bln  PARIS (Reuters) - Four private equity firms plan to buy  Bermuda-based Intelsat for about \$3 billion, world's  second-largest satellite operator said on Monday.",__en__ __sv__ Intelsat __vi__ Bermuda __tn__ headquarters location</s>
        18,"Biometric ID System Said to Delay Venezuela Recall By CHRISTOPHER TOOTHAKER     CARACAS, Venezuela (AP) -- high-tech thumbprint devices were meant to keep people from voting more than once in recall ballot against President Hugo Chavez. Instead, they often wound up working fitfully - even when Chavez himself voted - contributing to huge delays in Sunday's historic referendum...",__en__ __sv__ CHRISTOPHER TOOTHAKER CARACAS __vi__ Venezuela __tn__ country __sv__ Venezuela __tn__ President __uk__ office held by head of government __sv__ President __uk__ Venezuela __tn__ country __sv__ Hugo Chavez __uk__ Venezuela __tn__ country of citizenship __uk__ President __uk__ position held</s>
        19,"Hurricane Emergency Aid Set Up in Florida (AP) AP - More than 76,000 meals and snacks have been served to hurricane-ravaged counties in Florida, with thousands more available from federal, local and private agencies, Federal Emergency Management Agency said Monday.",__en__ __sv__ Hurricane Emergency Aid Set Up in Florida __tn__ Florida __tn__ located in administrative territorial entity __sv__ hurricane-ravaged counties __tn__ Florida __tn__ located in administrative territorial entity</s>
        20,Taco Bell's Blue Dew Pepsi pushes a blue version of Mountain Dew only at Taco Bell. Is this a winning strategy?,__en__ __sv__ Blue Dew Pepsi __tr__ Taco Bell's __vi__ manufacturer</s>
        21,"Playlist magazine announced; first issue this month (MacCentral) MacCentral - Mac Publishing LLC, publishers of Macworld magazine on Monday announced Playlist, a new digital music magazine for Mac and Windows users. new magazine, which will be newsstand-only, will be available on August 24, 2004.",__en__ __sv__ Playlist __yo__ magazine __zu__ instance of __sv__ Playlist __yo__ magazine __zu__ instance of</s>
        22,"Traders Bet on Oracle's PeopleSoft Bid (Reuters) Reuters - Options traders have been\building bullish positions in PeopleSoft Inc.  (PSFT.O) as\investors bet a federal judge will approve Oracle Corp.'s\hostile takeover bid of business software maker, traders\said on Monday.",__en__ __sv__ Oracle Corp.'s __vi__ Oracle __tn__ headquarters location</s>
        23,"Olympics: Thorpe Beats Phelps as U.S. Suffers Gold Gap  ATHENS (Reuters) - Australian swimmer Ian Thorpe beat  arch-rival Michael Phelps in men's 200-meter freestyle on  Monday as United States trailed China, Australia and Japan  in medals table on day three of Olympic Games.",__en__ __sv__ Ian Thorpe __uk__ swimmer __zu__ sport __sv__ Michael Phelps __uk__ swimmer __zu__ sport</s>
        23,"Olympics: Thorpe Beats Phelps as U.S. Suffers Gold Gap  ATHENS (Reuters) - Australian swimmer Ian Thorpe beat  arch-rival Michael Phelps in men's 200-meter freestyle on  Monday as United States trailed China, Australia and Japan  in medals table on day three of Olympic Games.",__en__ __sv__ Ian Thorpe __uk__ swimmer __zu__ sport __sv__ Michael Phelps __uk__ swimmer __zu__ sport</s>
"""
