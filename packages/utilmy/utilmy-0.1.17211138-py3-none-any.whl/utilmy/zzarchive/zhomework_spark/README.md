##### 1) Continuous Integration CI Tests  + Full size Run
```
Run with Docker,
Spark 2.4 setup as 1 Master + 1 node (standalone cluster)


##### Unit Testing
   With Spark Docker + Github Actions CI + Pytest
      Results:  https://github.com/arita37/zesresr/actions
      config:  .github/workflows/pytest.yaml


#### Full Run
   With Spark Docker + Github Actions CI + Full data size
      Results:  https://github.com/arita37/zesresr/actions
      config:  .github/workflows/main.yaml


```




                                                                                               
##### 2) Tests + Coverage Result                                   
```

==== 8 passed, 3 warnings in 96.03s (0:01:36) =======================

Name                                        Stmts   Miss  Cove                                                      
--------------------------------------------------------------                                                      
src\__init__.py                                 0      0   100%                                                      
src\functions\GetFamiliesFromUserAgent.py       8      0   100%                                                      
src\tables\table_predict_volume.py             74     56    24%                                                      
src\tables\table_user_log.py                   37      2    95%                                                      
src\tables\table_user_session_log.py           29      0   100%                                                      
src\tables\table_user_session_stats.py         24      0   100%                                                      
src\util_models.py                             54     54     0%                                                      
src\utils.py                                   36      6    83%                                                     
---------------------------------------------------------------                                                     
TOTAL                                         262    118    55%



#### Command
pytest --cov=src/  --html=output/tests/report.html --self-contained-html  tests/   


```




##### 3) Answer to questions
```







```





#### 4) Install and Running full data
```
##### Check Dockerfile, Docker-compose.yml as follow :


#### Local 
    cd repo
    python main.py  --onfig_path  config/config.yaml


#### Spark Submit  (Need to edit the pats
   script/sparkrunscript.sh


```






##### 5) Log Output
```
Copy Paste of the CI






```












