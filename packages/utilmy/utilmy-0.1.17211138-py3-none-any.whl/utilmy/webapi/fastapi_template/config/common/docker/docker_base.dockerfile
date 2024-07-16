##### Install Debian APT-GET  #########################################################
### https://hub.docker.com/_/ubuntu/tags
FROM ubuntu:23.10 as BASE



##### APT Get     ###################################################################
RUN apt-get update   && apt-get upgrade -y \
  && apt-get install -y git \
    software-properties-common \
    apt-transport-https  ca-certificates \
    wget nano  vim  curl  openssl  unzip rsync  procps htop \
    gcc   g++   gfortran libc6-dev \
    build-essential \
    tesseract-ocr  libtesseract-dev


######## Workdir  ###################################################################
RUN  mkdir -p /opt/work/
WORKDIR /opt/work/



#### Install kubctl.  ##############################################################
## https://hub.docker.com/r/bitnami/kubectl
# RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.15.1/bin/linux/amd64/kubectl   && \ 
#    chmod u+x kubectl && mv kubectl /bin/kubectl




#### Clean-up. ###################################################################
RUN apt-get autoremove -y \
    && apt-get clean -y





#################################################################################
###### Miniconda
### https://repo.anaconda.com/miniconda/

ENV CONDA_DIR=/opt/miniconda
ENV PATH=$CONDA_DIR/bin:$PATH

ENV PYTHONDONTWRITEBYTECODE=true

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py39_23.10.0-1-Linux-x86_64.sh  -O miniconda.sh && \
    chmod a+x miniconda.sh && \
    ./miniconda.sh -b -p $CONDA_DIR && \
    rm ./miniconda.sh 



###### PIP   ##################################################################
ENV PIP_LIST_DIR="config/common/pip/pip_app.txt"
ENV PIP_LIST="pip_app.txt"
COPY "./$PIP_LIST_DIR"   /opt/work/


RUN cat "/opt/work/$PIP_LIST" && \
    pip  install -r  "/opt/work/$PIP_LIST"  --no-cache-dir  && \
    pip list



##### Clean up ###############################################################
RUN  rm -rf /var/lib/apt/lists/*  \
    && conda clean -tpy \
    && rm -rf /root/.cache/pip/
    #&& find $CONDA_DIR -follow -type f -name '*.a' -delete \
    #&& find $CONDA_DIR -follow -type f -name '*.pyc' -delete \
    #&& find $CONDA_DIR -follow -type f -name '*.js.map' -delete 



#### Custom dirs ############################################################



#####  Entry Point.  ########################################################
ENTRYPOINT ["/bin/bash"]




