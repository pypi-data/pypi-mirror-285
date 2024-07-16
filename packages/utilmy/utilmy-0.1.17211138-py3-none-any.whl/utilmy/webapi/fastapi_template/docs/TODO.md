

### TOOD
```

 - fastAPI default backgrounTask does not have timeLimit per task,
     Time Limit is only implemented at the pytessaract level.
     Max queue size of jobs :  Need to use 3rd task queue managemet tool (Celery,...).

 -  Storage of jobid, async resuts are done using diskcache :  
             async storage on disk and multithread.

    Implement Key valueStore Wrapper (ie Redis) for storage for In/Out of jobid and results for dsitributed setup (write, read)


 - Add configuration of background tasks in global yaml config.

 - Make global yaml dynamically reloadable, without server start.

 - Add better stress tests client with report in csv: at various time, latency load.
 
 - Create Nested dataclass for configuration validation (type).

 - Implement basic authentification.

 - Implement Middlewware for origin check.

 - Normalize the JSON response (error, no error) based on other specifications.


```

