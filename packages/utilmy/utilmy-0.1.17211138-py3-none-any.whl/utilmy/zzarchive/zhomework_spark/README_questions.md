#### Answers to questions



################################################################################
#### 1. Sessionize the web log by IP. Sessionize = aggregrate all page hits by visitor/IP during a session.
    https://en.wikipedia.org/wiki/Session_(web_analytics)
```

### Identifiers
We created 2 identifiers :

    user_id  : (== ipSource)  represents user idenification.
           A better definition would be   
                 user_id == ipSource + Device + OS    or cookie of the browser.

           Example: Ipad in family can be by 2-3 persons at same time..., exact idenitification is difficult.      


    user_session_id : Global unique session_id
          = user_id + Timestamp_start_session.
 
          New_session = 1 if    (current_event_time - prev_event_time  )  > 15 * 60 secs.

  
### Partition of tables:
    To manage large volume of data, we  parititoned data as follow :
          by  YYYYMMDD date, hour of day.
          OR by iphashBucket  (100 buckets) for agg. tables


### Output Schema:
We generate 3 main intermediate tables:


Table in output/full/userlog/
 |-- loggedtimestamp: string (nullable = true)                                                                       
 |-- loggeddate: date (nullable = true)                                                                              
 |-- hour: integer (nullable = true)                                                                                 
 |-- minute: integer (nullable = true)                                                                               
 |-- elb: string (nullable = true)                                                                                   
 |-- sourceIP: string (nullable = true)                                                                              
 |-- request_processing_time: string (nullable = true)                                                               
 |-- backend_processing_time: string (nullable = true)                                                               
 |-- elb_status_code: string (nullable = true)                                                                       
 |-- backend_status_code: string (nullable = true)                                                                   
 |-- received_bytes: string (nullable = true)                                                                        
 |-- sent_bytes: string (nullable = true)                                                                            
 |-- URL: string (nullable = true)                                                                                   
 |-- user_agent: string (nullable = true)                                                                            
 |-- os: string (nullable = true)                                                                                    
 |-- device: string (nullable = true)                                                                                
 |-- browser: string (nullable = true)                                                                               
 |-- user_id: string (nullable = true)                                                                               
 |-- sourceIPPrefix: string (nullable = true)                                                                        
 |-- useragenthash: integer (nullable = false)                                                                       
 |-- ts: long (nullable = true)                                                                                      
 |-- IPHashBucket: integer (nullable = true)  



Table in output/full/usersession/
 |-- user_id: string (nullable = true)                                                                               
 |-- loggedtimestamp: string (nullable = true)                                                                       
 |-- sourceIP: string (nullable = true)                                                                              
 |-- IPHashBucket: integer (nullable = true)                                                                         
 |-- user_agent: string (nullable = true)                                                                            
 |-- useragenthash: integer (nullable = true)                                                                        
 |-- URL: string (nullable = true)                                                                                   
 |-- os: string (nullable = true)                                                                                    
 |-- device: string (nullable = true)                                                                                
 |-- loggeddate: date (nullable = true)                                                                              
 |-- hour: integer (nullable = true)                                                                                 
 |-- ts: long (nullable = true)                                                                                      
 |-- last_event: long (nullable = true)                                                                              
 |-- diff: long (nullable = true)                                                                                    
 |-- user_session_id: string (nullable = true)                                                                       
 |-- is_new_session: integer (nullable = false)                                                                      
                                                 


/usersessionstats/
 |-- user_session_id: string (nullable = true)                                                                       
 |-- user_id: string (nullable = true)                                                                               
 |-- sourceIP: string (nullable = true)                                                                              
 |-- IPHashBucket: integer (nullable = true)                                                                         
 |-- os: string (nullable = true)                                                                                    
 |-- device: string (nullable = true)                                                                                
 |-- hour: integer (nullable = true)                                                                                 
 |-- starttimestamp: string (nullable = true)                                                                        
 |-- endtimestamp: string (nullable = true)                                                                          
 |-- session_duration: long (nullable = true)                                                                        
 |-- n_unique_url: long (nullable = false)                                                                           
 |-- n_events: long (nullable = false)  


```

################################################################################
#### 2. Determine the average session time
```
      2) Output of avg, min and max session duration whole users.
+--------------------+--------------------+--------------------+----------+                                                                  
|min_session_duration|max_session_duration|avg_session_duration|n_sessions|                                                                  
+--------------------+--------------------+--------------------+----------+                                                                  
|                   0|                1164|   83.24408329888384|    116112|                                                                  
+--------------------+--------------------+--------------------+----------+                                                                  

```

                                                                                                                                             



############################################################################################
#### 3. Determine unique URL visits per session. To clarify, count a hit to a unique URL only once per session.
```

     Get Unique URL count per session  (top n_unique_url)
+--------------------+------------+--------+----------------+                                           
|     user_session_id|n_unique_url|n_events|session_duration|                                           
+--------------------+------------+--------+----------------+                                           
|119.81.61.166_201...|        8016|   10540|             877|                                           
|106.186.23.95_201...|        4656|    5114|             299|                                           
|52.74.219.71_2015...|        3998|    4327|            1164|                                           
|119.81.61.166_201...|        3928|    4054|             300|                                           
|119.81.61.166_201...|        3637|    3763|             299|                                           
|52.74.219.71_2015...|        3601|    4531|            1164|                                           
|119.81.61.166_201...|        3334|    3429|             297|                                           
|52.74.219.71_2015...|        3282|    3783|             877|                                           
|119.81.61.166_201...|        2841|    2987|             299|                                           
|119.81.61.166_201...|        2786|    2891|             260|                                           
|106.51.132.54_201...|        2597|    4387|             264|                                           
|52.74.219.71_2015...|        2196|    2931|             876|                                           
|106.186.23.95_201...|        2112|    2208|            1164|                                           
|54.169.20.106_201...|        1896|    1979|             814|                                           
|52.74.219.71_2015...|        1731|    2492|             299|                                           
+--------------------+------------+--------+----------------+                                           
only showing top 15 rows         


Some ips has very high volume of events  
   ---> Mostly, Bots or batch systems.
   --->  119.81.61.166  has few session with high number of events


Table in output/full/usersessionstats/


```





###########################################################################################
#### 4. Find the most engaged users, ie the IPs with the longest session 
```


    Most Engaged : users with longest session duration
+---------------+--------------------+--------------------+--------------------+                                                             
|        user_id|min_session_duration|max_session_duration|avg_session_duration|                                                             
+---------------+--------------------+--------------------+--------------------+                                                             
|   125.19.44.66|                   0|                1164|            316.8125|                                                             
|  106.186.23.95|                 117|                1164|  390.45454545454544|                                                             
|   8.37.225.122|                  63|                1164|               444.0|                                                             
|  115.248.37.69|                  11|                1164|   326.1666666666667|                                                             
|   52.74.219.71|                   7|                1164|   375.9166666666667|                                                             
|  119.81.61.166|                   7|                1164|   384.6666666666667|                                                             
|213.239.204.204|                   2|                1162|   373.1666666666667|                                                             
|  54.251.151.39|                   0|                1162|               360.6|                                                             
|  196.15.16.102|                   2|                1162|               317.6|                                                             
|   59.144.58.37|                   0|                1162|  276.61538461538464|                                                             
+---------------+--------------------+--------------------+--------------------+                                                             
only showing top 10 rows  



Table in output/full/usersessionstats/


```





################################################################################################
####  5. Predict the expected load (requests/second) in the next minute
Plot of load over the full 2 days period.




![image](https://user-images.githubusercontent.com/18707623/120799986-679daa00-c57a-11eb-964a-4dea3bb16009.png)






```

1) Remarks :

   There are blanks (no logs) periods --> Server batch issues/pause ? 
      Not clear if those blanks are repeated daily...

   They are also gap/jump in load at regular period, but noisy.

   Data is not enough to have daily seasonal patterns :  < 24 hours data.
           ---> Model would be in-complete due to lack of full period.


2) Remark 2:

Instead of just prediction, having use actual cases of prediction in mind is more relevant:
   
     --> Infrastructure sizing : Nb of servers needed : static or semi-satic

     --> Idenfication of  'sustained' peak load : Anomalies, recurrent issues (over gap),...


So, MaxLoad prediction is more relevant metric.


3)  We propose to predict this load, called MaxLoad at seach session

   MaxLoad is defined
          P(  Load over period [t, t+1min]  <   MaxLoad   )  = 99%   (Confidence level)     


     We can use MaxLoad to size the infrastructure with 99% level.

    We also predict the median load (50% quantile)


5)

We also tried various models like :
   ARIMA, auto-regressive GARCH, Seasonal ARIMA,...

It does not work very well dues to may gaps (ie random ?)
However, this is nor clear if the discontinuity and gaps are repeated daily at same time,
given the lack of data.
So, having a simple but reliable numbers are preferable (vs complex models and un-stable errors).


6) Prediction is as follow :

    Blue : Actual  Load (request/sec)    
    Orange : 99.9% Quantile level prediction.    
    Green : 50% Quantile level prediction


```

![image](https://user-images.githubusercontent.com/18707623/120880526-29e66300-c606-11eb-80ee-f39637c600a2.png)


```
Potential Imorovements :
     1 month data is more relevant for predicton testing.
     99.999% may be needed for better infrastructure sizing.
     

```



#########################################################################################
#### 6. Predict the session length for a given IP
```

### Reformulation as follow ( question is a bit ambiguous ):

    Predict  the session length of session (i+1) of  IP j (ie user_id),
    with information at session i or before. 



### Solution used:

    At session i, we create Xfeatures for IP based on past data.
    We predct the length of session (i+1)  using Standard regression model (Linear or RandomForest)

    Y(i+1) = Length of session (i+1) for IPsource j

    X(i)  = (x1, .....,xN)   features vector based on past data (until session i).


    Features used :
         Continuous :
         Auto-regressive features (ie past values) in  (i-1), (i-2) sessions.
         Category :  os, dvice  with Hashing Space + One Hot Encoding


### Results Root Mean Square Error
    RMSE_train  : 166.18303497157004                                                                                                                                  
    RMSE_test :   166.0938044859328                 

RMSE Error is a high, due to lack of data, simplified model,



Xfeatures used for the prediction  of Y(i+1)

 |-- user_session_id: string (nullable = true)                                                                       
 |-- user_id: string (nullable = true)                                                                               
 |-- sourceIP: string (nullable = true)                                                                              
 |-- os: string (nullable = true)                                                                                    
 |-- device: string (nullable = true)                                                                                
 |-- hour: integer (nullable = true)                                                                                 
 |-- starttimestamp: string (nullable = true)                                                                        
 |-- endtimestamp: string (nullable = true)                                                                          
 |-- session_duration: long (nullable = true)                                                                        
 |-- n_unique_url: long (nullable = true)                                                                            
 |-- n_events: long (nullable = true)                                                                                
 |-- IPHashBucket: integer (nullable = true)                                                                         
 |-- label: long (nullable = true)                                                                                   
 |-- n_unique_url_lag1: long (nullable = true)                                                                       
 |-- n_events_lag1: long (nullable = true)                                                                           
 |-- session_duration_lag1: long (nullable = true)                                                                   
 |-- n_unique_url_lag2: long (nullable = true)                                                                       
 |-- n_events_lag2: long (nullable = true)                                                                           
 |-- session_duration_lag2: long (nullable = true)                                                                   
 |-- os_enc: double (nullable = false)                                                                               
 |-- device_enc: double (nullable = false)                                                                           
 |-- os_1hot: vector (nullable = true)                                                                               
 |-- device_1hot: vector (nullable = true)                                                                           
 |-- features: vector (nullable = true)                                                                              
 |-- prediction: double (nullable = false) 

code:        src/tables/table_predict_session_length.py        : session length  prediction.


```




#########################################################################################
#### 7. Predict the number of unique URL visits by a given IP
```

Is it the total number of URL visits ? What about the period, 6 months,2 month ?

### Reformulation as follow ( question is ambiguous ):
To make it more 'rationale':

    Predict at session i,  the number of unique URL in the session (i+1) of  IP j (ie user_id).



#### We predict the following :
    Y(i+1) = Nb of unique URL at session (i+1) for IPsource  j
    using X(i) = (x1, ...,xn) features vector base on past data ( until session i)


### Results :

     RMSE_train : 46.45965066603986                                                                                                                                          
     RMSE_test : 23.780115622701583     


Error is a high, due to lack of data, simplified model,



X(i) Features used for the prediction  of Y(i+1)

 |-- user_session_id: string (nullable = true)                                                                       
 |-- user_id: string (nullable = true)                                                                               
 |-- sourceIP: string (nullable = true)                                                                              
 |-- os: string (nullable = true)                                                                                    
 |-- device: string (nullable = true)                                                                                
 |-- hour: integer (nullable = true)                                                                                 
 |-- starttimestamp: string (nullable = true)                                                                        
 |-- endtimestamp: string (nullable = true)                                                                          
 |-- session_duration: long (nullable = true)                                                                        
 |-- n_unique_url: long (nullable = true)                                                                            
 |-- n_events: long (nullable = true)                                                                                
 |-- IPHashBucket: integer (nullable = true)                                                                         
 |-- label: long (nullable = true)                                                                                   
 |-- n_unique_url_lag1: long (nullable = true)                                                                       
 |-- n_events_lag1: long (nullable = true)                                                                           
 |-- session_duration_lag1: long (nullable = true)                                                                   
 |-- n_unique_url_lag2: long (nullable = true)                                                                       
 |-- n_events_lag2: long (nullable = true)                                                                           
 |-- session_duration_lag2: long (nullable = true)                                                                   
 |-- os_enc: double (nullable = false)                                                                               
 |-- device_enc: double (nullable = false)                                                                           
 |-- os_1hot: vector (nullable = true)                                                                               
 |-- device_1hot: vector (nullable = true)                                                                           
 |-- features: vector (nullable = true)                                                                              
 |-- prediction: double (nullable = false) 


code :     src/tables/table_predict_url.py        : nb unique url per ip prediction.

```




