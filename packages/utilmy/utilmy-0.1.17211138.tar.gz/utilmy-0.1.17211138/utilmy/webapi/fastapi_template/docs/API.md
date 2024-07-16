

###  API Entry/Points
``` 
   Docs is available at API start on 
   http://localhost:7919/docs


  /v1/imgsync
      POST JSON :
          {
            "data": "string",  ## image encoded in b64 string
            "lang": "string",  ## Optional language
            "token": "string"  ## Token (optional)
          }

      OUTPUT JSON :
          {
            "text": "string",    ## Extracted text.
            "ts": 0,             ## Unix Timestamp in seconds.
            "version": "string"
            "status": "string",
          }


  /v1/imgasync
      POST JSON :
          {
            "data": "string", ## image encoded in b64 string
            "lang": "string",
            "token": "string"
          }


      OUTPUT JSON :
          {
            "jobid": "string",   ## jobid of the async job.
            "ts": 0,             ## Unix Timestamp in seconds.
            "version": "string"
            "status": "string",
          }


  /v1/imgasyncget
      POST JSON :
          {
            "jobid": "string",
            "token": "string"
          }

      OUTPUT JSON :
          {
            "jobid": "string",
            "text": "string",
            "ts": 0,             ## Unix Timestamp in seconds
            "version": "string"
            "status": "string",
          }

  Example of CURL command is here:
     scripts/local/test_client.sh 


```
