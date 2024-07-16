##### Copy of Log files

```
######  Load userlog table                                                                   
                              0                    1                                                  
loggeddate           2015-07-22           2015-07-22                                                  
ds          22-07-2015 11:40:06  22-07-2015 11:40:07                                                  
y                            27                   62                                                  
                              0                    1                                                  
loggeddate           2015-07-22           2015-07-22                                                  
ds          22-07-2015 11:40:06  22-07-2015 11:40:07                                                  
y                            27                   62                                                  
####### Train  Run  ##############################                                                    
   loggeddate                   ds   y                                                                
0  2015-07-22  22-07-2015 11:40:06  27                                                                
1  2015-07-22  22-07-2015 11:40:07  62                                                                
####### Prediction Run ###########################                                                    
####### Prediction output ########################                                                    
+-------------------+-----+----------+-----------+-------------+                                      
|                 ds|    y|y_pred_max|y_pred_mean|training_date|                                      
+-------------------+-----+----------+-----------+-------------+                                      
|22-07-2015 11:40:06| 27.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:07| 62.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:08| 56.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:09|112.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:10| 58.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:11| 58.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:12| 67.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:13| 85.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:14|160.0|   272.092|       85.0|   2021-06-05|                                      
|22-07-2015 11:40:15| 57.0|   272.092|       85.0|   2021-06-05|                                      
+-------------------+-----+----------+-----------+-------------+                                      
only showing top 10 rows                                                                              
                                                                                                      
####### Predict check: 4269                                                                           
                                 0                    1                                               
ds             22-07-2015 11:40:06  22-07-2015 11:40:07                                               
y                               27                   62                                               
y_pred_max                 272.092              272.092                                               
y_pred_mean                     85                   85                                               
training_date           2021-06-05           2021-06-05                                               
                                                                                                      
SUCCESS: The process with PID 17996 (child process of PID 15576) has been terminated.                 
SUCCESS: The process with PID 15576 (child process of PID 3156) has been terminated.                  
SUCCESS: The process with PID 3156 (child process of PID 13808) has been terminated. 
```









#### Part A) pyspark program which
```
  main.py          :  Command Line Input        : main.py   with  config.yaml
  spark_submit.sh :  Spark Submit bash script   + different arguments on the node size....
  

1. Sessionize the web log by IP. Sessionize = aggregrate all page hits by visitor/IP during a session.
    https://en.wikipedia.org/wiki/Session_(web_analytics)

2. Determine the average session time

3. Determine unique URL visits per session. To clarify, count a hit to a unique URL only once per session.

4. Find the most engaged users, ie the IPs with the longest session times

```





#### part B) Using Spark MLLib,
```
5. Predict the expected load (requests/second) in the next minute

6. Predict the session length for a given IP

7. Predict the number of unique URL visits by a given IP
```



#### Add units tests

     Units tests in tests/ folder

     #### Runnsable code  pyppark 2.4
     cd repo
     python main.py




##### Infos
- For this dataset,  sessionization by time window rather than navigation. 
Feel free to determine the best session window time on your own, or start with 15 minutes.


log file format is
http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/access-log-collection.html#access-log-entry-format








```












D:\_devs\Python01\gitdev\arepo\zesresr (main -> origin)                                                                      
? python main.py  --config_path  config/config.yaml                                                                          
Using config/config.yaml                                                                                                     
21/06/03 23:48:50 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes
 where applicable                                                                                                            
Using Spark's default log4j profile: org/apache/spark/log4j-defaults.properties                                              
Setting default log level to "WARN".                                                                                         
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).                                 
21/06/03 23:48:51 WARN Utils: Service 'SparkUI' could not bind on port 4040. Attempting port 4041.                           
######  Load usersessionstats table and Preprocesss #############                                                            
######### coly: label  ######################################################                                                
########### Numerical features   ############################################                                                
########## Auto-Regressive features : Past   #################################                                               
########## Auto-Regressive features : Past   ##################################                                              
######### Categorical Variables  ##############################################                                              
+--------------------+-------------+-------------+-------+------+----+--------------------+--------------------+-------------
---+------------+--------+------------+-----+-----------------+-------------+---------------------+-----------------+--------
-----+---------------------+------+----------+--------------+----------------+                                               
|     user_session_id|      user_id|     sourceIP|     os|device|hour|      starttimestamp|        endtimestamp|session_durat
ion|n_unique_url|n_events|IPHashBucket|label|n_unique_url_lag1|n_events_lag1|session_duration_lag1|n_unique_url_lag2|n_events
_lag2|session_duration_lag2|os_enc|device_enc|       os_1hot|     device_1hot|                                               
+--------------------+-------------+-------------+-------+------+----+--------------------+--------------------+-------------
---+------------+--------+------------+-----+-----------------+-------------+---------------------+-----------------+--------
-----+---------------------+------+----------+--------------+----------------+                                               
|1.186.108.242_201...|1.186.108.242|1.186.108.242|Windows| Other|  16|2015-07-22T16:22:...|2015-07-22T16:22:...|             
  3|           3|       3|          12|    6|             null|         null|                 null|             null|        
 null|                 null|   0.0|       0.0|(32,[0],[1.0])|(1464,[0],[1.0])|                                               
+--------------------+-------------+-------------+-------+------+----+--------------------+--------------------+-------------
---+------------+--------+------------+-----+-----------------+-------------+---------------------+-----------------+--------
-----+---------------------+------+----------+--------------+----------------+                                               
only showing top 1 row                                                                                                       
                                                                                                                             
None                                                                                                                         
######### Merge  ##############################################################                                              
                                                                       0                                                  1  
user_session_id                  1.186.79.11_2015-07-22T16:11:36.857234Z           1.187.122.83_2015-07-22T18:03:38.654014Z  
user_id                                                      1.186.79.11                                       1.187.122.83  
sourceIP                                                     1.186.79.11                                       1.187.122.83  
os                                                               Windows                                            Android  
device                                                             Other                                         Samsung SM  
hour                                                                  16                                                 18  
starttimestamp                               2015-07-22T16:11:36.857234Z                        2015-07-22T18:03:38.654014Z  
endtimestamp                                 2015-07-22T16:44:04.817748Z                        2015-07-22T18:04:50.955723Z  
session_duration                                                    1948                                                 72  
n_unique_url                                                          65                                                 63  
n_events                                                              67                                                 63  
IPHashBucket                                                          12                                                 12  
label                                                                 72                                                 35  
n_unique_url_lag1                                                     80                                                 65  
n_events_lag1                                                         80                                                 67  
session_duration_lag1                                                  6                                               1948  
n_unique_url_lag2                                                      3                                                 80  
n_events_lag2                                                          3                                                 80  
session_duration_lag2                                                  3                                                  6  
os_enc                                                                 0                                                  1  
device_enc                                                             0                                                  2  
os_1hot                (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  
device_1hot            (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  
features               (65.0, 67.0, 1948.0, 80.0, 80.0, 6.0, 3.0, 3.0...  (63.0, 63.0, 72.0, 65.0, 67.0, 1948.0, 80.0, 8...  
[Stage 18:>                                                         (0 + 1) / 8]21/06/03 23:50:00 WARN BLAS: Failed to load i
mplementation from: com.github.fommil.netlib.NativeSystemBLAS                                                                
21/06/03 23:50:00 WARN BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeRefBLAS                      
[Stage 24:====================================>                     (5 + 1) / 8]                                             
--------------+------------+--------+------------+-----+-----------------+-------------+---------------------+----
-------------+-------------+---------------------+------+----------+--------------+----------------+              
|1.186.108.242_201...|1.186.108.242|1.186.108.242|Windows| Other|  16|2015-07-22T16:22:...|2015-07-22T16:22:...|  
             3|           3|       3|          12|    6|             null|         null|                 null|    
         null|         null|                 null|   0.0|       0.0|(32,[0],[1.0])|(1464,[0],[1.0])|              
+--------------------+-------------+-------------+-------+------+----+--------------------+--------------------+--
--------------+------------+--------+------------+-----+-----------------+-------------+---------------------+----
-------------+-------------+---------------------+------+----------+--------------+----------------+              
only showing top 1 row                                                                                            
                                                                                                                  
None                                                                                                              
######### Merge  ##############################################################                                   
                                                                       0                                          
        1                                                                                                         
user_session_id                  1.186.79.11_2015-07-22T16:11:36.857234Z           1.187.122.83_2015-07-22T18:03:3
8.654014Z                                                                                                         
user_id                                                      1.186.79.11                                       1.1
87.122.83                                                                                                         
sourceIP                                                     1.186.79.11                                       1.1
87.122.83                                                                                                         
os                                                               Windows                                          
  Android                                                                                                         
device                                                             Other                                         S
amsung SM                                                                                                         
hour                                                                  16                                          
       18                                                                                                         
starttimestamp                               2015-07-22T16:11:36.857234Z                        2015-07-22T18:03:3
8.654014Z                                                                                                         
endtimestamp                                 2015-07-22T16:44:04.817748Z                        2015-07-22T18:04:5
0.955723Z                                                                                                         
session_duration                                                    1948                                          
       72                                                                                                         
n_unique_url                                                          65                                          
       63                                                                                                         
n_events                                                              67                                          
       63                                                                                                         
IPHashBucket                                                          12                                          
       12                                                                                                         
label                                                                 72                                          
       35                                                                                                         
n_unique_url_lag1                                                     80                                          
       65                                                                                                         
n_events_lag1                                                         80                                          
       67                                                                                                         
session_duration_lag1                                                  6                                          
     1948                                                                                                         
n_unique_url_lag2                                                      3                                          
       80                                                                                                         
n_events_lag2                                                          3                                          
       80                                                                                                         
session_duration_lag2                                                  3                                          
        6                                                                                                         
os_enc                                                                 0                                          
        1                                                                                                         
device_enc                                                             0                                          
        2                                                                                                         
os_1hot                (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
 0.0, ...                                                                                                         
device_1hot            (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
 0.0, ...                                                                                                         
features               (65.0, 67.0, 1948.0, 80.0, 80.0, 6.0, 3.0, 3.0...  (63.0, 63.0, 72.0, 65.0, 67.0, 1948.0, 8
0.0, 8...                                                                                                         
[Stage 18:>                                                         (0 + 1) / 8]21/06/03 23:50:00 WARN BLAS: Faile
d to load implementation from: com.github.fommil.netlib.NativeSystemBLAS                                          
21/06/03 23:50:00 WARN BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeRefBLAS           
21/06/03 23:51:09 WARN Utils: Truncated the string representation of a plan since it was too large. This behavior 
can be adjusted by setting 'spark.debug.maxToStringFields' in SparkEnv.conf.                                      
[Stage 29:=============================>                            (4 + 1) / 8]    









?  python main.py  --config_path  config/config.yaml                                                         
Using config/config.yaml                                                                                     
21/06/04 00:50:42 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable                                                                            
Using Spark's default log4j profile: org/apache/spark/log4j-defaults.properties                              
Setting default log level to "WARN".                                                                         
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).                 
21/06/04 00:50:43 WARN Utils: Service 'SparkUI' could not bind on port 4040. Attempting port 4041.           
######  Load Raw features table and Preprocesss #################                                            
########## Load userssionsta  ###############################################                                
########## coly: label  #####################################################                                
########## Numerical features : T  ##########################################                                
########## Auto-Regressive features : T-1  ##################################                                
########## Auto-Regressive features : T-2  ##################################                                
######### Categorical Variables  ############################################                                
+--------------------+-------------+-------------+-------+------+----+--------------------+--------------------+----------------+------------+--------+------------+-----+-----------------+-------------+---------------------+-----------------+-------------+---------------------+------+----------+--------------+----------------+                                                                                                            
|     user_session_id|      user_id|     sourceIP|     os|device|hour|      starttimestamp|        endtimestamp|session_duration|n_unique_url|n_events|IPHashBucket|label|n_unique_url_lag1|n_events_lag1|session_duration
_lag1|n_unique_url_lag2|n_events_lag2|session_duration_lag2|os_enc|device_enc|       os_1hot|     device_1hot
|                                                                                                            
+--------------------+-------------+-------------+-------+------+----+--------------------+------------------
--+----------------+------------+--------+------------+-----+-----------------+-------------+----------------
-----+-----------------+-------------+---------------------+------+----------+--------------+----------------
+                                                                                                            
|1.186.108.242_201...|1.186.108.242|1.186.108.242|Windows| Other|  16|2015-07-22T16:22:...|2015-07-22T16:22:.
..|               3|           3|       3|          12|   80|             null|         null|                
 null|             null|         null|                 null|   0.0|       0.0|(32,[0],[1.0])|(1464,[0],[1.0])
|                                                                                                            
+--------------------+-------------+-------------+-------+------+----+--------------------+------------------
--+----------------+------------+--------+------------+-----+-----------------+-------------+----------------
-----+-----------------+-------------+---------------------+------+----------+--------------+----------------
+                                                                                                            
only showing top 1 row                                                                                       
                                                                                                             
None                                                                                                         
######### Merge  ############################################################                                
                                                                       0                                     
             1                                                                                               
user_session_id                  1.186.79.11_2015-07-22T16:11:36.857234Z           1.187.122.83_2015-07-22T18
:03:38.654014Z                                                                                               
user_id                                                      1.186.79.11                                     
  1.187.122.83                                                                                               
sourceIP                                                     1.186.79.11                                     
  1.187.122.83                                                                                               
os                                                               Windows                                     
       Android                                                                                               
device                                                             Other                                     
    Samsung SM                                                                                               
hour                                                                  16                                     
            18                                                                                               
starttimestamp                               2015-07-22T16:11:36.857234Z                        2015-07-22T18
:03:38.654014Z                                                                                               
endtimestamp                                 2015-07-22T16:44:04.817748Z                        2015-07-22T18
:04:50.955723Z                                                                                               
session_duration                                                    1948                                     
            72                                                                                               
n_unique_url                                                          65                                     
            63                                                                                               
n_events                                                              67                                     
            63                                                                                               
IPHashBucket                                                          12                                     
            12                                                                                               
label                                                                 63                                     
             2                                                                                               
n_unique_url_lag1                                                     80                                     
            65                                                                                               
n_events_lag1                                                         80                                     
            67                                                                                               
session_duration_lag1                                                  6                                     
          1948                                                                                               
n_unique_url_lag2                                                      3                                     
            80                                                                                               
n_events_lag2                                                          3                                     
            80                                                                                               
session_duration_lag2                                                  3                                     
             6                                                                                               
os_enc                                                                 0                                     
             1                                                                                               
device_enc                                                             0                                     
             2                                                                                               
os_1hot                (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
 0.0, 0.0, ...                                                                                               
device_1hot            (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
 0.0, 0.0, ...                                                                                               
features               (65.0, 67.0, 1948.0, 80.0, 80.0, 6.0, 3.0, 3.0...  (63.0, 63.0, 72.0, 65.0, 67.0, 1948
.0, 80.0, 8...                                                                                               
[Stage 11:=============================>                            (4 + 1) / 8]                             
[Stage 18:>                                                         (0 + 1) / 8]21/06/04 00:51:53 WARN BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeSystemBLAS                                                                  
21/06/04 00:51:53 WARN BLAS: Failed to load implementation from: com.github.fommil.netlib.NativeRefBLAS                       
21/06/04 00:52:58 WARN Utils: Truncated the string representation of a plan since it was too large. This behavior can be adjusted by setting 'spark.debug.maxToStringFields' in SparkEnv.conf.                                                              
RMSE_train 52.283032475594375                                                                                                 
RMSE_test 25.871734327648998                                                                                                  
                                                                       0                                                  1   
user_session_id                  1.186.79.11_2015-07-22T16:11:36.857234Z           1.187.122.83_2015-07-22T18:03:38.654014Z   
user_id                                                      1.186.79.11                                       1.187.122.83   
sourceIP                                                     1.186.79.11                                       1.187.122.83   
os                                                               Windows                                            Android   
device                                                             Other                                         Samsung SM   
hour                                                                  16                                                 18   
starttimestamp                               2015-07-22T16:11:36.857234Z                        2015-07-22T18:03:38.654014Z   
endtimestamp                                 2015-07-22T16:44:04.817748Z                        2015-07-22T18:04:50.955723Z   
session_duration                                                    1948                                                 72   
n_unique_url                                                          65                                                 63   
n_events                                                              67                                                 63   
IPHashBucket                                                          12                                                 12   
label                                                                 63                                                  2   
n_unique_url_lag1                                                     80                                                 65   
n_events_lag1                                                         80                                                 67   
session_duration_lag1                                                  6                                               1948   
n_unique_url_lag2                                                      3                                                 80   
n_events_lag2                                                          3                                                 80   
session_duration_lag2                                                  3                                                  6   
os_enc                                                                 0                                                  1   
device_enc                                                             0                                                  2   
os_1hot                (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...   
device_1hot            (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...  (0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, ...   
features               (65.0, 67.0, 1948.0, 80.0, 80.0, 6.0, 3.0, 3.0...  (63.0, 63.0, 72.0, 65.0, 67.0, 1948.0, 80.0, 8...   
prediction                                                       33.0154                                            38.0677   
                            0             1                                                                                   
user_id           1.186.79.11  1.187.122.83                                                                                   
session_duration         1948            72                                                                                   
label                      63             2                                                                                   
prediction            33.0154       38.0677       
























#### Part A) Write a clean pyspark program which
```
  main.py          :  Command Line Input        : main.py   with  config.yaml
  spark_submit.sh :  Spark Submit bash script   + different arguments on the node size....
  
  preprocess_session.py
  preprocess_features.py
 
 

1. Sessionize the web log by IP. Sessionize = aggregrate all page hits by visitor/IP during a session.
    https://en.wikipedia.org/wiki/Session_(web_analytics)

2. Determine the average session time

3. Determine unique URL visits per session. To clarify, count a hit to a unique URL only once per session.

4. Find the most engaged users, ie the IPs with the longest session times


Intermediate tables on disk /parquet files on DISK
with partition


   Need to create 2 GLOBAL unique id :
           user_id          : Track user unique identifier.

          user_session_id  :  track session of user.
        

    user_id = ip + user_agent  (+ cookie_XXX)   ( == login user in windows/Mac/IOS ....)
    
    user_session_id =   user_id + TimeStampStart   (bots can have muttiple events per user_id.... at same miliseconds timestamps: multi-thread bots)
    



session_table  ==  Structure version of original table.

###  user_session_id,  ip, dt, date, day, hour, min,  .... other fields

   partition by (date, hour)
   dt : original timestamp
   date :  2021-05-01  (string)
   user_session_id  == ip+user_agent_hash+Timestamp
 

### ip_stats_session_table
  ip, date,  ip_prefix, ip_hash, n_events, n_session, session_time_avg, session_nunique_url, session_time_max, session_time_min,
      user_agent, device, os, browser, ...

   partition by (ip_hash)

   ip_hash   :  HASH(ip) into 500 buckets.
   ip_prefix :  AA.BB.CC    only top 3 components i


### user_session_stats table

user_session_id, start_dt, end_dt, duration, n_events





time_stats_agg

  date, hour, min,  n_unqiue_ip, n_events,   n_events_per_ip,


```


