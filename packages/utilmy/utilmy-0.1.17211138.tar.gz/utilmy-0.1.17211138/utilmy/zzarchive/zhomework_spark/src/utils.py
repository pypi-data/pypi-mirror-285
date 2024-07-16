# -*- coding: utf-8 -*-
import os
import yaml
import pyspark
from loguru import logger

##########################################################################################
################### Logs Wrapper #########################################################
def log(*s):
    logger.info(",".join([ str(t) for t in s  ]) )

def log2(*s):
    logger.warn(",".join([ str(t) for t in s  ]) )

def log3(*s):
    logger.debug(",".join([ str(t) for t in s  ]) )


def log(*s):
    print(*s)

def log_sample(*s):
    print(*s)


##########################################################################################
def config_load(config_path:str):
    """  Load Config file into a dict
    Args:
        config_path: path of config
    Returns: dict config
    """
    #Load the yaml config file
    with open(config_path, "r") as yamlfile:
        config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)

    dd = {}
    for x in config_data :
        for key,val in x.items():
           dd[key] = val

    return dd


def spark_check(df:pyspark.sql.DataFrame, path:str, nsample:int=10 , save=True, verbose=True , returnval=False):
    """ Snapshot logs check for dataframe
    Args:
        df:
        path:
        nsample:
        save:
        verbose:
        returnval:
    Returns:
    """


    if save or returnval or verbose:
        df1 =   df.limit(nsample).toPandas()

    if save :
        ##### Need HDFS version
        os.makedirs( path , exist_ok=True )
        df1.to_csv(path + '/table.csv', sep='\t', index=False)

    if verbose :
        log(df1.head(2).T)
        log( df.printSchema() )

    if returnval :    
        return df1



##########################################################################################
class to_namespace(object):
    def __init__(self, d):

        self.__dict__ = d







