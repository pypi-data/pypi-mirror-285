Thursday 09 May 2024 03:38:27 PM IST
```bash


### dense run
{'name': 'bench_v1_dense_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-dense', 'model_type': 'stransformers', 'model_id': 'sentence-transformers/all-MiniLM-L6-v2', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/query/df_synthetic_queries_20240509_171632.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench//ag_news/dense/20240509_1908_45/'}
ztmp/bench//ag_news/dense/20240509_1908_45//dfmetrics.csv
                       id  istop_k        dt
0    11095120374133649132        1  0.014053
1    11095120374133649132        1  0.009587
2    11095120374133649132        1  0.010143
3    11095120374133649132        1  0.009755
4    11095120374133649132        1  0.009556
..                    ...      ...       ...
994  13758416053061127359        1  0.009890
995  13758416053061127359        1  0.010180
996  13758416053061127359        1  0.009946
997  13758416053061127359        1  0.010331
998  13758416053061127359        1  0.010781

[999 rows x 3 columns]
 Avg time per request: 0.011344309683676597
 Percentage accuracy: 66.06606606606607%



 
### sparse run
{'name': 'bench_v1_sparse_run', 'server_url': 'http://localhost:6333', 'collection_name': 'hf-ag_news-sparse', 'model_type': 'stransformers', 'model_id': 'naver/efficient-splade-VI-BT-large-query', 'topk': 5, 'dataset': 'ag_news', 'dirquery': 'ztmp/bench/ag_news/query/df_synthetic_queries_20240509_171632.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'dirout2': 'ztmp/bench/ag_news/sparse/20240509_1909_11/'}
ztmp/bench/ag_news/sparse/20240509_1909_11//dfmetrics.csv
                       id  istop_k        dt
0    11095120374133649132        1  0.023240
1    11095120374133649132        1  0.018617
2    11095120374133649132        1  0.016978
3    11095120374133649132        1  0.018087
4    11095120374133649132        1  0.015860
..                    ...      ...       ...
994  13758416053061127359        1  0.014443
995  13758416053061127359        1  0.016068
996  13758416053061127359        1  0.015921
997  13758416053061127359        1  0.016173
998  13758416053061127359        1  0.016873

[999 rows x 3 columns]
 Avg time per request 0.018465570978693537
 Percentage accuracy 86.08608608608608






### tantivy run
{'name': 'bench_v1_tantivy_run', 'dirquery': 'ztmp/bench/ag_news/query/df_synthetic_queries_20240509_171632.parquet', 'dirdata2': 'ztmp/bench/norm//ag_news/', 'datapath': 'ztmp/bench/tantivy_index/hf-ag_news', 'dirout2': 'ztmp/bench/ag_news/tantivy/20240509_1909_19/'}
ztmp/bench/ag_news/tantivy/20240509_1909_19//dfmetrics.csv
                       id  istop_k        dt
0    11095120374133649132        1  0.002947
1    11095120374133649132        1  0.002528
2    11095120374133649132        0  0.001922
3    11095120374133649132        1  0.002650
4    11095120374133649132        1  0.002776
..                    ...      ...       ...
994  13758416053061127359        1  0.001467
995  13758416053061127359        1  0.002935
996  13758416053061127359        1  0.002137
997  13758416053061127359        1  0.002622
998  13758416053061127359        1  0.004000

[999 rows x 3 columns]
 Avg time per request: 0.0034035507503811183
 Percentage accuracy: 75.77577577577578
```
---
Thu
