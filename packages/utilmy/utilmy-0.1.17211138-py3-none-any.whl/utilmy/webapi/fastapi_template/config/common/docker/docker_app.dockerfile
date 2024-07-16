##### Base Docker  ###################################################
FROM  artia37/mldock:base_20240324_25ff97d as BASE

#### Custom dirs ####################################################


#####  Copy Repo  ###################################################
RUN mkdir -p /opt/app
COPY  .  /opt/app 

### Gigthub Actions : Make Sure files timestamp are valid
RUN   chmod -R 777 /opt/app/scripts/  && ls /opt/app/scripts/ 


#####  entrypoint. ##################################################
WORKDIR /opt/app/
#EXPOSE 8888


ENTRYPOINT ["/bin/bash"]
