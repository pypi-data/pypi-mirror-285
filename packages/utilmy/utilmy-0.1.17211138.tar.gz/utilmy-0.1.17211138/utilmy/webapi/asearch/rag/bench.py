# -*- coding: utf-8 -*-
""" Benchmark runs

    ### Folder structure
        ### Refefence data: 
            ztmp/data/cats/ag_news/  raw/   from internet
                                    train/  .parquet  normalized
                                    test/   .parquet  normalized   


        ### Bench data: 
                ztmp/bench/ag_news/ : dirbench
                        aparquet/  : dir of input data, parquet files copied from  /data/cats/ag_news/train and test/
                        ... 

                        dense/ 
                        sparse/
                        metrics/
                        ...
                        questions/


                        kg_triplets/  
                        kg_questions/
                            



    #### Install

       export torch_device='cpu'

    ### How to run
        sudo docker run -d -p 6333:6333     -v ~/.watchtower/qdrant_storage:/qdrant/storage:z     qdrant/qdrant


    ### How to run qdrant from binary file

        # download latest tar.gz package file from here, Linux: 
            wget -c https://github.com/qdrant/qdrant/releases/download/v1.9.0/qdrant-x86_64-unknown-linux-gnu.tar.gz

        # extract tar.gz package
            tar -xvf qdrant-x86_64-unknown-linux-gnu.tar.gz

        # run qdrant on separate shell.
            cd download_folder
            ./qdrant --config-path /absolute/path/to/config.yaml &

            # Config Where to store all  data
            storage_path: ./ztmp/qdrant/storage

            ---> In same docker : easy


    ### Benchmarks:
        alias py2="python bench.py "

        py2 bench_v1_create_indexes --dirdata_root ztmp/bench/
        py2 bench_v1_run  --dirout ztmp/bench/   --topk 5


        ### Bench
        tantivy : v1  6ms
        Sparse :      23ms
        Dense:        30 ms


    Index:  Document => triplet => question
    Twhile search, we try to: question =>triplets=>document



    ### Benchmark accuracy:
    Sames 1000 query for all 3.
        --> Accuracy.
        --> Compare  errors.

        join  dataframe on id


        ### csv metrics
        df1 = df1.merge(df2, on='id', how='left', suffixes=('', '_2'))

        df[ df.is_topk == 0 ] --> Find errors.


    ### Binary mode for qdrant
    https://github.com/qdrant/qdrant/releases


"""
import os, time, glob, pandas as pd, numpy as np
from box import Box  ## use dot notation as pseudo class
from qdrant_client import QdrantClient

from utilmy import pd_read_file, pd_to_file, date_now, glob_glob, json_save, json_load, os_makedirs
from utilmy import log

##### Local imports ######################################
from rag.engine_kg import kg_triplets_extract_v2, dbsql_save_records_to_db, neo4j_db_insert_triplet_file, \
    neo4j_create_db, \
    kg_generate_questions_from_triplets, neo4j_search_docids, dbsql_fetch_text_by_doc_ids
# from fastembed import TextEmbedding

from rag.engine_qd import (EmbeddingModel,
                           qdrant_dense_create_index, qdrant_dense_search,
                           qdrant_dense_create_collection,

                           EmbeddingModelSparse,
                           qdrant_sparse_create_index, qdrant_sparse_search,
                           qdrant_sparse_create_collection,

                           qdrant_collection_exists,
                           )

from rag.engine_tv import (tantivy_index_documents, tantivy_search,
                           fusion_search)

from rag.dataprep import (dataset_hf_to_parquet, dataset_agnews_schema_v1, )

from utils.utils_base import pd_append


def report_get_rank_by_docids(row, engine):
    col_docids = f"topk_docids_{engine}"
    result_string = row[col_docids]
    result_ids = result_string.split(";") if isinstance(result_string, str) else []
    try:
        rank = result_ids.index(str(row.text_id))
    except ValueError as err:
        rank = -1
    # log(f"engine:{engine}, rank:{rank}")
    return rank


##########################################################################################
def report_create_textsample(dirin="ztmp/bench", dataset="ag_news", dirquery=None, engines: str = "",
                             error_filter: str = ""):
    """Merging  query dataframe with  results from each benchmark --> create text report

        python bench.py report_create_textsample  --dirin "ztmp/bench/"
        
        args:
        dirin (str):  input path to load or create  query dataset.
        dataset (str):  dataset name
        dirquery (str):  input path to load or create  query dataset.
        engines (str):  comma separated engines to use. defaults to all
        error_filter (int):  engine to filter query errors with. when set shows only those records for which engine fails. defaults to no filter.
        Output sample:
                                       
            Question#1: What distinguishes short-sellers from ultra-cynics within the realm of investing?
            =================
            Dense --top5
            1)
            doc_id:11077278260051828775
            Long-Short Funds Have Uneven Record (Investor's Business Daily) Investor's Business Daily - At a time when rapid growth in hedge funds might suggest that their mutual fund counterparts -- long-short funds -- would also prove popular, few investors seem to have much appetite for mutual funds they can sell short.
            --------
            2)
            doc_id:11271908030688414242
            Investor Profile: Asensio Ponders Long Bet As a dedicated short-seller for nearly eight years, Manuel Asensio became known as one of the most ruthless investors in the business.


            =================
            Sparse --top5  - true,
            1)
            doc_id:3492334796636090735
            Wall St. Bears Claw Back Into the Black  NEW YORK (Reuters) - Short-sellers, Wall Street's dwindling  band of ultra-cynics, are seeing green again.
            --------
            2)
            doc_id:14504362844448484081
            Wall St. Bears Claw Back Into the Black (Reuters) Reuters - Short-sellers, Wall Street's dwindling\band of ultra-cynics, are seeing green again.


            =================
            Neo4j --top5
            1)
            doc_id:14362295801255034810
            Australian Newbery wins women #39;s platform Olympic gold Chantelle Newbery won Australia #39;s first gold medal in diving since 1924 Sunday night, easily holding off China #39;s Lao Lishi and Aussie teammate Loudy Tourky in women #39;s 10-meter platform.

    
    
    
    """
    tunix = date_now(fmt="%Y%m%d/%H%M%S", returnval="str")
    dirout = f"{dirin}/{dataset}/error_reports/{tunix}"

    query_df = pd_read_file(dirquery)
    query_df = query_df[["text_id", "question", 'head', 'tail', 'type']]

    all_engines = ("dense", "sparse", "neo4j", "sparse_neo4j", "dense_neo4j")
    if isinstance(engines, str):
        engines = engines.split(",")
    engines = [engine for engine in engines if engine in all_engines]

    if not engines:
        engines = all_engines

    log(f"generating report for engines: {engines}")
    # get latest bench config
    configs = [report_get_latest_config(dirin, dataset, engine=engine) for engine in
               engines]
    configs = [config for config in configs if config is not None]
    os_makedirs(dirout)
    df_all = report_get_combined_metrics_df(configs)

    assert len(query_df) == len(df_all)

    query_df = pd.concat([query_df, df_all], axis=1)
    # log(query_df.shape)
    for engine in engines:
        query_df[f"{engine}_rank"] = query_df.apply(lambda x: report_get_rank_by_docids(x, engine), axis=1)

    error_filter_col = f"{error_filter}_rank" if error_filter in engines else ""
    if error_filter_col != "":
        query_df = query_df[query_df[error_filter_col] < 0]

    report_path = f"{dirout}/report.txt"
    with open(report_path, "a") as fp:
        for i, row in enumerate(query_df.itertuples()):
            # log(row)
            question = row.question
            fp.write(f"\nQuestion#{i + 1}: {question}")
            triplet = f"{row.head}, {row.type},{row.tail}"
            fp.write(f"\nsource_triplet: {triplet}")
            source_str = report_get_result_string_by_docids([row.text_id])
            fp.write(f"\nsource_text:{source_str}")
            engine_status_list = []
            engine_string = ""
            for engine in engines:
                if f"topk_docids_{engine}" in query_df.columns:
                    col_docids = f"topk_docids_{engine}"
                    col_rank = f"{engine}_rank"
                    result_string = query_df.iloc[i][col_docids]
                    result_ids = result_string.split(";") if isinstance(result_string, str) else []
                    engine_status_list.append(f"{engine}:{query_df.iloc[i][col_rank]}")
                    engine_string += f"\n=================\n{engine} --topk | {query_df.iloc[i][col_rank]}\n=================\n"
                    result_string = report_get_result_string_by_docids(result_ids)
                    engine_string += result_string
            fp.write("\nengine_rank: " + "|".join(engine_status_list) + "\n")
            fp.write(engine_string)
            fp.write(f"\n\n\n")
    log(f"report saved in:{report_path}")


def report_create_textsample_rerun_bench(dirin="ztmp/bench", dataset="ag_news", dirquery=None):
    """Merging  query dataframe with  results from each benchmark.

       python bench.py report_create_textsample_rerun_bench --dirin "ztmp/bench/"
    
 
    """
    tunix = date_now(fmt="%Y%m%d/%H%M%S", returnval="str")
    dirout = f"{dirin}/{dataset}/error_reports/{tunix}/"
    dirout2 = f"{dirout}/report.txt"

    query_df = pd_read_file(dirquery)
    # get latest bench config

    dense_config, sparse_config, neo4j_config = [report_get_latest_config(dirin, dataset, engine=engine) for engine in
                                                 ("dense", "sparse", "neo4j")]

    dense_model = EmbeddingModel(dense_config.model_id, dense_config.model_type)
    sparse_model = EmbeddingModelSparse(sparse_config.model_id)
    os_makedirs(dirout)
    with open(f"{dirout2}", "a") as fp:
        for i, row in enumerate(query_df.itertuples(), start=1):
            question = row.question
            fp.write(f"Question#{i}: {question}\n")

            fp.write(f"=================\nDense --top5\n=================\n")
            dense_response = qdrant_dense_search(query=question, topk=dense_config.topk,
                                                 server_url=dense_config.server_url,
                                                 collection_name=dense_config.collection_name, model=dense_model)
            dense_result_ids = [dense_item.payload["text_id"] for dense_item in dense_response]
            result_string = report_get_result_string_by_docids(dense_result_ids)
            fp.write(result_string)

            fp.write(f"\n=================\nSparse --top5\n=================\n")
            sparse_results = qdrant_sparse_search(query=question, topk=sparse_config.topk,
                                                  server_url=sparse_config.server_url,
                                                  collection_name=sparse_config.collection_name, model=sparse_model)
            sparse_result_ids = [sparse_result.payload["text_id"] for sparse_result in sparse_results]
            result_string = report_get_result_string_by_docids(sparse_result_ids)
            fp.write(result_string)

            fp.write(f"\n=================\nNeo4j --top5\n=================\n")
            neo4j_results = neo4j_search_docids(query=question, topk=neo4j_config.topk)
            neo4j_result_ids = [neo4j_result["text_id"] for neo4j_result in neo4j_results]
            result_string = report_get_result_string_by_docids(neo4j_result_ids)
            fp.write(result_string)
            # log(neo4j_result_ids)
            fp.write(f"\n\n\n")

    log(dirout2)


def report_merge_metrics(dirin="ztmp/bench", dataset="ag_news", dirquery=None):
    """Merging  query dataframe with  results from each benchmark.

    python bench.py report_merge_metrics --dirin "ztmp/bench/"

    Args:
        dirin (str):  path path where  benchmark results are stored.     : "ztmp/bench".

    """
    dirmetric = f"{dirin}/{dataset}/metrics"

    log("###### pick latest file from each benchmark directory")
    search_types = ("sparse", "dense", "tantivy")
    bench_dirs = [f"{dirin}/{dataset}/{dirk}" for dirk in search_types]
    flist = [glob_glob_last_modified(f"{bench_dir}/*/*.csv") for bench_dir in bench_dirs]
    flist = [filepath for filepath in flist if filepath is not None]

    log("###### Merge query df with results from each benchmark")
    dirquery = f"{dirin}/{dataset}/query/df_search_test.parquet" if dirquery is None else dirquery
    dfall = pd_read_file(dirquery)
    dfall = dfall[["id", "query"]]

    for i, filepath in enumerate(flist):
        df2 = pd_read_file(filepath)
        dfall = dfall.merge(df2, on="id", how="left", suffixes=("", f"_{search_types[i]}"))
    dfall.rename(columns={"istop_k": "istop_k_sparse"}, inplace=True)

    pd_to_file(dfall, f"{dirmetric}/df_err_all.csv", show=1)

    log("##### Select mismatch rows between engine")
    dfdiff = dfall[(dfall.istop_k_sparse != 1) | (dfall.istop_k_dense != 1) | (dfall.istop_k_tantivy != 1)]
    dfdiff = dfdiff[["id", "query", "istop_k_sparse", "istop_k_dense", "istop_k_tantivy"]]
    pd_to_file(dfdiff, f"{dirmetric}/df_err_mismatch.csv", show=1)

    log("##### Calc metrics")
    n = len(dfall)
    dmetrics = {"acc_dense": dfall["istop_k_dense"].sum() / n,  ## 91%
                "acc_sparse": dfall["istop_k_sparse"].sum() / n,  ## 99.9%
                "acc_tantivy": dfall["istop_k_tantivy"].sum() / n,
                }
    log(dmetrics)
    json_save(dmetrics, f"{dirmetric}/metrics.json")


def report_get_result_string_by_docids(docids, sep="\n--------\n"):
    # 'ztmp/bench/ag_news/results/neo4j/20240608/230111/'
    results = dbsql_fetch_text_by_doc_ids(text_ids=docids)
    dense_text = [f"{idx})\ndoc_id:{result['text_id']}\n{result['text']}" for idx, result in
                  enumerate(results, start=1)]
    return sep.join(dense_text)


def report_get_latest_config(dirin, dataset, engine="dense"):
    dirconfig = f"{dirin}/{dataset}/{engine}/*/*/config.json"
    latest_config_file = glob_glob_last_modified(dirconfig)

    latest_config = json_load(latest_config_file)
    latest_config = Box(latest_config)
    return latest_config


def report_get_combined_metrics_df(configs):
    config_dfs = [pd_read_file(f"{config.dirout2}/dfmetrics.csv", sep="\t") for config in configs]
    config_engines = [config.engine for config in configs]

    combined_dfs = []
    for config_df, engine in zip(config_dfs, config_engines):
        config_df = config_df[["topk_docids"]]
        config_df.rename(columns={"topk_docids": f"topk_docids_{engine}"}, inplace=True)
        combined_dfs.append(config_df)

    df_len = [combined_df.shape[0] for combined_df in combined_dfs]
    assert min(df_len) == max(df_len)

    result_df = pd.concat(combined_dfs, axis=1)
    return result_df


##########################################################################################
####### data converter ###################################################################
def bench_v1_data_convert(dirin=None, dirdata_root=None, dataset=None, dirout=None):
    dirdata_norm = f"{dirdata_root}/norm/{dataset}"

    norm_files = glob_glob(f"{dirdata_norm}/*/*.parquet")
    if len(norm_files) > 0:
        return None

    if dirin is None:
        dataset_hf_to_parquet(dataset, dirout=dirdata_root, splits=["train", "test"])

    if dataset == "agnews":
        # normalize
        dataset_agnews_schema_v1(dirin=f"{dirdata_root}/{dataset}/*.parquet", dirout=dirdata_norm)


def query_load_or_create(dirin=None, dirdata=None, nfile=1, nquery=1000):
    """Load or create a query dataset based on  input directories and parameters.
    args :
        dirin (str):  input path to load or create  query dataset.
        dirdata (str):  data path used to create  query dataset.
        nfile (int): Number of files to read when creating  dataset. Default is 1.
        nquery (int): Number of queries to sample from  dataset. Default is 1000.

    Returns:
        DataFrame:  loaded or created query dataset.
    """

    if not os.path.exists(dirin):
        df = pd_read_file(f"{dirdata}/*/df*.parquet", nfile=nfile)  ##  Real Dataset

        # pick thousand random rows
        df_query = df.sample(nquery)
        df_query["query"] = df_query["text"].apply(lambda x: np_random_subset(x, 20))
        pd_to_file(df_query, f"{dirin}")

    else:
        df_query = pd_read_file(dirin)

    return df_query


#############################################################################################
####### Qdrant Dense Vector  ################################################################
def bench_v1_dense_run(cfg=None, dirout="ztmp/bench/", topk=5, dataset="ag_news", dirdata="ztmp/bench/norm/",
                       dirquery: str = None, colid: str = "text_id", colquestion="question"):
    """Measure performance in Real and bigger dataset.

    python rag/bench.py bench_v1_run  --dirout ztmp/bench/   --topk 5


    """
    cc = Box({})
    cc.engine = "dense"
    cc.name = "bench_v1_dense_run"

    cc.server_url = "http://localhost:6333"
    cc.collection_name = f"hf-{dataset}-dense"
    cc.model_type = "stransformers"
    cc.model_id = "sentence-transformers/all-MiniLM-L6-v2"  ### 384,  50 Mb
    cc.topk = topk

    cc.dataset = dataset
    cc.dirquery = f"{dirout}/{dataset}/query/df_search_test.parquet" if dirquery is None else dirquery
    cc.dirdata2 = f"{dirdata}/{dataset}/"

    df_query = query_load_or_create(dirin=cc.dirquery, dirdata=cc.dirdata2)
    model = EmbeddingModel(cc.model_id, cc.model_type)
    client = QdrantClient(cc.server_url)

    dfmetrics = pd.DataFrame(columns=["id", "istop_k", "dt", "topk_docids", "topk_scores"])
    for i, row in df_query.iterrows():
        id1 = row[colid]
        query = row[colquestion]
        t0 = time.time()
        results = qdrant_dense_search(query, collection_name=cc.collection_name,
                                      model=model, topk=topk, client=client)
        dt = time.time() - t0
        topk_ids = [str(scored_point.id) for scored_point in results[:topk]]
        topk_id_str = ";".join(topk_ids)
        topk_scores = [str(scored_point.score) for scored_point in results[:topk]]
        topk_scores_str = ";".join(topk_scores)
        ####  Add metrics
        istop_k = 1 if id1 in topk_ids else 0
        dfmetrics = pd_append(dfmetrics, [[id1, istop_k, dt, topk_id_str, topk_scores_str]])

    metrics_export(dfmetrics, dataset, dirout, cc, engine="dense")


def bench_v1_create_dense_indexes(dirbench="./ztmp/bench/ag_news", dataset="ag_news"):
    """Create indexes for benchmarking
    python rag/bench.py bench_v1_create_indexes --dirout ztmp/bench/
    """
    # download dataset from Hugging Face in dirout
    # save normalized dataset in dirout/norm
    model_type = "stransformers"
    model_id = "sentence-transformers/all-MiniLM-L6-v2"  ### 384,  50 Mb
    server_url = "http://localhost:6333"

    diref = "./ztmp/data/cats/ag_news"  ### Reference data
    # dirbench = "./ztmp/bench/ag_news/"

    #### Move the file to ag_news/bench/aparquet/
    if len(glob_glob(dirbench + f"/aparquet/*.parquet")) < 1:
        from utilmy import os_copy
        for ii, fi in enumerate(glob_glob(diref + "/train/*.parquet")):
            os_copy(fi, dirbench + f"/aparquet/df_{ii}.parquet")

    # print(filelist)
    collection_name = f"hf-{dataset}-dense"
    qclient = QdrantClient(server_url)
    if qdrant_collection_exists(qclient, collection_name):
        log(f"collection {collection_name} already exists")
        return

    model = EmbeddingModel(model_id, model_type)
    qdrant_dense_create_collection(qclient, collection_name=collection_name,
                                   size=model.model_size)
    qdrant_dense_create_index(
        dirin=f"{dirbench}/aparquet/*.parquet",
        collection_name=collection_name,
        coltext="text",
        colscat=["text_id", "text"],
        model_id="sentence-transformers/all-MiniLM-L6-v2",
        model_type="stransformers",
        batch_size=10,
        client=qclient
    )


##########################################################################################
####### Qdrant Sparse Index  #############################################################
def bench_v1_create_sparse_indexes(dirbench="./ztmp/bench/ag_news", dataset="ag_news"):
    model_id = "naver/efficient-splade-VI-BT-large-doc"  # 268 MB
    server_url = "http://localhost:6333"

    diref = "./ztmp/data/cats/ag_news"  ### Reference data
    # dirbench = "./ztmp/bench/ag_news/"

    #### Move the file to ag_news/bench/aparquet/
    if len(glob_glob(dirbench + f"/aparquet/*.parquet")) < 1:
        from utilmy import os_copy
        for ii, fi in enumerate(glob_glob(diref + "/train/*.parquet")):
            os_copy(fi, dirbench + f"/aparquet/df_{ii}.parquet")

    # print(filelist)
    collection_name = f"hf-{dataset}-sparse"
    qclient = QdrantClient(server_url)
    if qdrant_collection_exists(qclient, collection_name):
        log(f"collection {collection_name} already exists")
        return

    qdrant_sparse_create_collection(qclient=qclient, collection_name=collection_name)
    qdrant_sparse_create_index(
        dirin=f"{dirbench}/aparquet/*.parquet",
        collection_name=collection_name,
        coltext="text",
        colscat=["text_id", "text"],
        model_id=model_id,
        batch_size=10,
        client=qclient
    )


def bench_v1_sparse_run(cfg=None, dirout="ztmp/bench", topk=5, dataset="ag_news",
                        dirdata="ztmp/bench/norm/", dirquery: str = None, colid: str = "text_id",
                        colquestion: str = "question"):
    """Measure performance in Real and bigger dataset.

    python rag/bench.py bench_v1_sparse_run  --dirout ztmp/bench/   --topk 5


    """
    cc = Box({})
    cc.engine = "sparse"
    cc.name = "bench_v1_sparse_run"

    cc.server_url = "http://localhost:6333"
    cc.collection_name = f"hf-{dataset}-sparse"
    cc.model_type = "stransformers"
    cc.model_id = "naver/efficient-splade-VI-BT-large-query"  ### 17 Mb
    cc.topk = topk

    cc.dataset = dataset
    cc.dirquery = f"{dirout}/{dataset}/query/df_search_test.parquet" if dirquery is None else dirquery
    cc.dirdata2 = f"{dirdata}/{dataset}/"

    df_query = query_load_or_create(dirin=cc.dirquery, dirdata=cc.dirdata2)
    model = EmbeddingModelSparse(cc.model_id)
    client = QdrantClient(cc.server_url)
    dfmetrics = pd.DataFrame(columns=["id", "istop_k", "dt", "topk_docids", "topk_scores"])

    for i, row in df_query.iterrows():
        # print(row)
        id1 = row[colid]
        query = row[colquestion]

        t0 = time.time()
        results = qdrant_sparse_search(
            query, collection_name=cc.collection_name, model=model, topk=topk, client=client
        )
        dt = time.time() - t0
        topk_ids = [str(scored_point.id) for scored_point in results[:topk]]
        topk_id_str = ";".join(topk_ids)
        topk_scores = [str(scored_point.score) for scored_point in results[:topk]]
        topk_scores_str = ";".join(topk_scores)
        #### Accuracy.abs
        istop_k = 1 if id1 in topk_ids else 0
        dfmetrics = pd_append(dfmetrics, [[id1, istop_k, dt, topk_id_str, topk_scores_str]])

    metrics_export(dfmetrics, dataset, dirout, cc, engine="sparse")


##########################################################################################
####### Tantivy Index  ###################################################################
def bench_v1_create_tantivy_indexes(dirdata_root="ztmp/bench", dataset="ag_news"):
    """Create indexes for benchmarking
    python rag/bench.py bench_v1_create_tantivy_indexes --dirout ztmp/bench/
    """
    # download dataset from Hugging Face in dirout
    # save normalized dataset in dirout/norm

    dirdata_norm = f"{dirdata_root}/norm/{dataset}"
    # print(filelist)
    index_path = f"{dirdata_root}/tantivy_index/hf-{dataset}"
    if os.path.exists(index_path):
        return

    # if dirdata_norm not empty skip
    bench_v1_data_convert(dirdata_root=dirdata_root, dataset=dataset)

    colsused = ["title", "text", "cat1"]
    tantivy_index_documents(
        dirin=f"{dirdata_norm}/*/*.parquet", datapath=index_path, colsused=colsused
    )


def bench_v1_tantivy_run(cfg=None, dirout="ztmp/bench", topk=5, dataset="ag_news", dirdata="ztmp/bench/norm/",
                         dirquery=None, colid: str = "text_id", colquestion: str = "question"):
    """Measure performance in Real and bigger dataset.

    python rag/bench.py bench_v1_tantivy_run  --dirout ztmp/bench/   --topk 5

    """
    cc = Box({})
    cc.name = "bench_v1_tantivy_run"
    cc.dirquery = f"{dirout}/{dataset}/query/df_search_test.parquet" if dirquery is None else dirquery

    cc.dirdata2 = f"{dirdata}/{dataset}/"
    cc.datapath = f"{dirout}/tantivy_index/hf-{dataset}"
    df_query = query_load_or_create(dirin=cc.dirquery, dirdata=cc.dirdata2)

    dfmetrics = pd.DataFrame(columns=["id", "istop_k", "dt", "topk_docids", "topk_scores"])
    # log(df_query.title)
    for i, row in df_query.iterrows():
        # print(row)
        id1 = row[colid]
        query = row[colquestion]

        # clean query to avoid query language errors
        # replace non alphanumeric characters with space
        query = str_to_alphanum_only(query)
        t0 = time.time()
        results = tantivy_search(datapath=cc.datapath, query=query, topk=topk)
        dt = time.time() - t0

        topk_ids = [doc[colid][0] for score, doc in results]
        #### Accuracy.abs
        istop_k = 1 if id1 in topk_ids else 0
        topk_id_str = ";".join(topk_ids)
        topk_scores = [str(score) for score, _ in results[:topk]]
        topk_scores_str = ";".join(topk_scores)

        dfmetrics = pd_append(dfmetrics, [[id1, istop_k, dt, topk_id_str, topk_scores_str]])

    metrics_export(dfmetrics, dataset, dirout, cc, engine="tantivy")


##########################################################################################
####### KG neo4J Index  ###################################################################
def bench_v1_create_neo4j_indexes(dirbench="./ztmp/bench/ag_news", nrows: int = -1, nqueries: int = 20):
    """Create indexes for benchmarking
       python rag/bench.py bench_v1_create_neo4j_indexes --dirout ztmp/bench/

       ### using neo4j search docids ---> 
          timing and
          When you filter the questions, 
                  make sure the text (doc_id) are actually inserted in neo4j.


       #### neo4j benchmarking indexing
            ```
            # pybench bench_v1_create_neo4j_indexes --nrows 20 --nqueries 20
            Model loaded in 6.82 seconds
            ./ztmp/bench/ag_news/kg_triplets/agnews_kg_relation_btest.csv
                            doc_id  ... info_json
            0   10031470251246589555  ...        {}
            44  13086739540453328833  ...        {}

            [45 rows x 5 columns]
            Extracted triplets from #20,  dt exec: 20.385884046554565

            ####### Generate questions from triplets ############################
            HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
            ztmp/kg/data/agnews_kg_bquestion.csv
            (20, 5)
            Generated questions from triplets,  dt exec: 10.212386846542358

            ####### Save records to DBSQL ######################################
            Saved #20 records to sqlite,  dt exec: 0.4380199909210205

            ####### Insert Triplet into neo4j ##################################
            #triplet inserted: 1 / 45,  time : 0.09 seconds
            Inserted triplets into neo4j,  dt exec: 0.31346702575683594

    """
    diref = "./ztmp/data/cats/ag_news"  ### Reference data
    # dirbench = "./ztmp/bench/ag_news/"

    #### Move the file to ag_news/bench/aparquet/
    if len(glob_glob(dirbench + f"/aparquet/*.parquet")) < 1:
        from utilmy import os_copy
        for ii, fi in enumerate(glob_glob(diref + "/train/*.parquet")):
            os_copy(fi, dirbench + f"/aparquet/df_{ii}.parquet")

    #### extract triplets
    t0 = time.time()
    kg_triplets_extract_v2(model_id="Babelscape/rebel-large",
                           dirin=f"{dirbench}/aparquet/*.parquet",
                           dirout=f"{dirbench}/kg_triplets/agnews_kg_relation_btest.parquet",
                           nrows=nrows,
                           coltxt="text", colid="text_id")
    log_time(f"Extracted triplets from #{nrows}", t0)

    log("\n####### Generate questions from triplets ############################")
    t0 = time.time()
    # generate questions from #nqueries triplets
    kg_generate_questions_from_triplets(dirin=f"{dirbench}/kg_triplets/agnews_kg_relation_btest.parquet",
                                        dirout=f"{dirbench}/kg_questions/agnews_kg_bquestion.parquet",
                                        batch_size=5, nrows=nqueries)
    log_time(f"Generated questions from triplets", t0)

    log("\n####### Save records to DBSQL ######################################")
    t0 = time.time()
    dbsql_save_records_to_db(dirin=f"{dirbench}/aparquet/",
                             db_path="./ztmp/db/db_sqlite/datasets.db",
                             table_name="b_agnews", coltext="text",
                             colid="text_id", nrows=nrows)
    log_time(f"Saved #{nrows} records to sqlite", t0)

    log("\n####### Insert Triplet into neo4j ##################################")
    neo4j_create_db(db_name="neo4j")
    t0 = time.time()
    neo4j_db_insert_triplet_file(dirin=f"{dirbench}/kg_triplets/agnews_kg_relation_btest.parquet",
                                 db_name="neo4j")
    log_time(f"Inserted triplets into neo4j", t0)


def bench_v1_neo4j_run(cfg=None, dirout="ztmp/bench", topk: int = 5, dataset="ag_news",
                       db_name="neo4j",
                       dirquery="./ztmp/bench/ag_news/kg_questions/agnews_kg_bquestion.parquet",
                       colid: str = "text_id", colquestion: str = "question"
                       ):
    """Measure performance in Real and bigger dataset.
    docs::

        python rag/bench.py bench_v1_neo4j_run  --dirout ztmp/bench/   --topk 5
        pybench bench_v1_neo4j_run --dirout "ztmp/bench" --topk 5 --dataset "ag_news" --dirquery "ztmp/kg/data/agnews_kg_bquestion.parquet"

        ##### neo4j benchmarking run

            {'name': 'bench_v1_neo4j_run', 'dirquery': 'ztmp/kg/data/agnews_kg_bquestion.csv', 'dirout2': 'ztmp/bench/ag_news/neo4j/20240531/200902/'}
            ztmp/bench/ag_news/neo4j/20240531/200902//dfmetrics.csv
                                id istop_k        dt
            0   10031470251246589555       1  0.339181
            1   10031470251246589555       1  0.015657
            19  12910890402456928629       1  0.016215
            Avg time per request 0.03225210905075073
            Percentage accuracy 80.0

    """
    from rag.engine_kg import (neo4j_search_docids)
    cc = Box({})
    cc.engine = "neo4j"
    cc.name = "bench_v1_neo4j_run"
    cc.db_name = db_name
    cc.dirquery = dirquery  # f"{dirout}/{dataset}/query/df_search_test.parquet" if dirquery is None else dirquery
    cc.topk = topk
    cc.dataset = dataset

    df_query = pd_read_file(cc.dirquery)
    dfmetrics = pd.DataFrame(columns=["id", "istop_k", "dt", "topk_docids", "topk_scores"])
    # log(df_query.title)
    for i, row in df_query.iterrows():
        text_id = row[colid]
        query = row[colquestion]

        # commented as it was interfering with keyword extraction
        # query = str_to_alphanum_only(query)  # replace non alphanumeric characters with space

        t0 = time.time()
        results = neo4j_search_docids(query=query, topk=topk, db_name=db_name)
        # log(results)
        dt = time.time() - t0

        #### Accuracy results
        topk_ids = [str(doc["text_id"]) for doc in results]
        topk_id_str = ";".join(topk_ids)
        topk_scores = [str(doc["score"]) for doc in results]
        topk_scores_str = ";".join(topk_scores)
        # log(f"text_id: {text_id}")
        # log(f"topk_ids: {topk_ids}")
        # doc_id stored as str in db, hence casting
        istop_k = 1 if str(text_id) in topk_ids else 0
        dfmetrics = pd_append(dfmetrics, [[text_id, istop_k, dt, topk_id_str, topk_scores_str]])

    metrics_export(dfmetrics, dataset, dirout, cc, engine="neo4j")


def bench_v1_fusion_run(cfg=None, dirout="ztmp/bench/", topk=5, engine: str = "", fusion_method="rrf",
                        dataset="ag_news",
                        sparse_collection_name="hf-ag_news-sparse", dense_collection_name="hf-ag_news-dense",
                        tantivy_datapath="./ztmp/tantivy_index", neo4j_db="neo4j",
                        sparse_model_id: str = "naver/efficient-splade-VI-BT-large-query",
                        dense_model_id: str = "sentence-transformers/all-MiniLM-L6-v2",
                        dense_model_type: str = "stransformers",
                        dirdata="ztmp/bench/norm/",
                        dirquery: str = None, colid: str = "text_id", colquestion="question"):
    """Measure performance in Real and bigger dataset.

    python rag/bench.py bench_v1_fusion_run  --dirout ztmp/bench/   --topk 5


    """
    cc = Box({})
    cc.name = "bench_v1_fusion_run"
    cc.engine = engine
    cc.qdrant_url = "http://localhost:6333"
    cc.sparse_collection_name = sparse_collection_name
    cc.dense_collection_name = dense_collection_name
    cc.tantivy_datapath = tantivy_datapath
    cc.neo4j_db = neo4j_db

    cc.model_type = dense_model_type
    cc.model_id = dense_model_id
    cc.topk = topk

    cc.dataset = dataset
    cc.dirquery = f"{dirout}/{dataset}/query/df_search_test.parquet" if dirquery is None else dirquery
    cc.dirdata2 = f"{dirdata}/{dataset}/"

    df_query = query_load_or_create(dirin=cc.dirquery, dirdata=cc.dirdata2)
    # model = EmbeddingModel(cc.model_id, cc.model_type)
    # client = QdrantClient(cc.server_url)

    dense_model = EmbeddingModel(model_id=dense_model_id,
                                 model_type=dense_model_type) if "dense" in engine and dense_model_id and dense_model_type else None
    sparse_model = EmbeddingModelSparse(
        model_id=sparse_model_id) if "sparse" in engine and sparse_collection_name else None
    dfmetrics = pd.DataFrame(columns=["id", "istop_k", "dt", "topk_docids", "topk_scores"])
    for i, row in df_query.iterrows():
        id1 = row[colid]
        query = row[colquestion]
        t0 = time.time()
        fusion_output = fusion_search(query, engine=engine,
                                      sparse_collection_name=sparse_collection_name,
                                      dense_collection_name=dense_collection_name, tantivy_datapath=tantivy_datapath,
                                      dense_model=dense_model,
                                      sparse_model=sparse_model,
                                      neo4j_db=neo4j_db, method=fusion_method)
        # log(f"fusion_output: {fusion_output}")
        results = [{"text_id": text_id, "score": score} for text_id, score in fusion_output.items()]
        results = sorted(results, key=lambda doc: doc["score"], reverse=True)

        dt = time.time() - t0
        topk_ids = [str(doc["text_id"]) for doc in results[:topk]]
        topk_id_str = ";".join(topk_ids)
        topk_scores = [str(doc["score"]) for doc in results[:topk]]
        topk_scores_str = ";".join(topk_scores)
        ####  Add metrics
        istop_k = 1 if id1 in topk_ids else 0
        dfmetrics = pd_append(dfmetrics, [[id1, istop_k, dt, topk_id_str, topk_scores_str]])

    metrics_export(dfmetrics, dataset, dirout, cc, engine=engine)


##########################################################################################
####### Utils   ##########################################################################
# def zzz_pd_append(df:pd.DataFrame, rowlist:list)-> pd.DataFrame:
#   df2 = pd.DataFrame(rowlist, columns= list(df.columns))
#   df  = pd.concat([df, df2], ignore_index=True)
#   return df

def metrics_export(dfmetrics, dataset, dirout, cc, engine="sparse"):
    """Export metrics to a specified path after processing them and saving to a file.
    Args:
        dfmetrics (DataFrame): metrics data to be exported.
        dataset (str)        : dataset name.
        dirout (str)         : output path path.
        cc (object)          : Additional configuration object.
    """
    tunix = date_now(fmt="%Y%m%d/%H%M%S", returnval="str")
    cc.dirout2 = f"{dirout}/{dataset}/{engine}/{tunix}/"
    log(cc)

    ### dfmetrics = pd.DataFrame(metrics, columns=["id", "istop_k", "dt"])
    pd_to_file(dfmetrics, f"{cc.dirout2}/dfmetrics.csv", show=1)
    json_save(cc, f"{cc.dirout2}/config.json")
    log(" Avg time per request", dfmetrics["dt"].mean())
    log(" Percentage accuracy", dfmetrics["istop_k"].mean() * 100)


def str_to_alphanum_only(txt):
    return "".join([c if c.isalnum() else " " for c in txt])


def np_random_subset(txt: str, w_count=20):
    """Generate a random subset ofå words from a given text.
    Args:
        txt (str):  input text.
        w_count (int):  number of words to include in  subset.     : 20.

    Returns:
        str: A string containing  randomly selected subset of words.
    """
    words = txt.split()
    start = np.random.randint(0, len(words) - w_count) if len(words) > w_count else 0
    return " ".join(words[start: start + w_count])


def glob_glob_last_modified(dirpath):
    # print(dirpath)
    files = sorted(glob.glob(dirpath), key=os.path.getctime, reverse=True)
    if len(files) > 0:
        return files[0]  # Latest file


def log_time(s, t0: float = 0):
    import time
    log(f"{s},  dt exec: {time.time() - t0}")


###################################################################################################
if __name__ == "__main__":
    import fire

    # pd.options.mode.chained_assignment = None
    fire.Fire()

######################
'''










################# neo4j benchmarking
# pybench bench_v1_neo4j_run  --dirquery "ztmp/kg/data/agnews_kg_question.parquet" 
Index(['doc_id', 'head', 'question', 'tail', 'type'], dtype='object')
{'name': 'bench_v1_neo4j_run', 'dirquery': 'ztmp/kg/data/agnews_kg_question.parquet', 'dirout2': 'ztmp/bench/ag_news/neo4j/20240530_2326_19/'}
ztmp/bench/ag_news/neo4j/20240530_2326_19//dfmetrics.csv
                      id istop_k        dt
0   12276780668924807370       1  0.527188
1   12276780668924807370       1  0.026353
2   12083816893608411777       1  0.026456
3   12083816893608411777       1  0.022825
4   10737347208811407503       1  0.028634
5   11378796013912527826       1  0.030394
6   13390806072678052578       0  0.021812
7   11675013665304437412       1  0.028671
8   13785821260762704508       1  0.021517
9   12974542679823603965       1  0.020059
10  11698683890797567577       0  0.020678
11  10665815340401200908       0  0.021322
12  11787988978332267796       1  0.023296
13   9909348144263893933       1  0.022990
14  11339024036341566029       1  0.020991
15  13329191152078442376       0  0.019810
16  13017909028899574264       1  0.021842
17  13509060406842014558       1  0.019781
18  10397233788300326534       1  0.020819
19  10407173634313255749       1  0.022162
 Avg time per request 0.04838000535964966
 Percentage accuracy 80.0





'''
