""" Entries for common utilities
Docs::

     https://github.com/davidaurelio/hashids-python


"""
import os,sys,time, datetime, random,re,pathlib, string
from typing import Any, Callable, Sequence, Dict, List, Union,Optional
from pathlib import Path
from box import Box
import fire, msgpack, json, traceback, sqlalchemy, pandas as pd
from sqlitedict import SqliteDict
from dataclasses import dataclass, asdict
import dacite


from utilmy_base import (os_makedirs, date_now, os_file_check)
from utilmy_log import log,log2, logw,loge
###############################################################################################





###############################################################################################
def testall():
    test3()


def test_get_cfg()->Dict:
    cfg = {}
    cfg['cache'] ={
        "dir":       "ztmp/cache/cache_ctrquadkey.sqlite",
        "tablename": "quadkey_features",
    }
    return cfg['cache']


def test3():
    """ Insert, Load sqlite dict  0.8 sec for 20k Insert
    Docs::

        #/dev/shm/  ### get in nano-secon : 100 nano
    """
    cfg = test_get_cfg()
    cache_path = cfg["dir"]
    tablename  = cfg['tablename']

    db = cache_get_session(cfg, encoding_engine='msgpack', max_retry=3)
    log(db)

    dd = {'feat-list' : [ ( fake_get_id(),  fake_get_id() )   for i in range(200)  ]}
    ddmsg = dd
    x0    =  str(dd)[:100]
    #ddmsg = msgpack.packb(dd, use_bin_type=False)
    kkey  = '13300211231200023203'  # fake_get_id()
    ### 3 micro sec to pack-unpack
    # %timeit msgpack.unpackb(msgpack.packb(dd, use_bin_type=False), raw=True, use_list=False)

    t0 = time.time()
    for i in range(0,1000):
      for j in range(0, 10):
         keyi       = f"quad-{kkey}{i}{j}"
         db[ keyi ] = ddmsg
      db.commit()

    log('time',  time.time() - t0)
    log('n_key', len(db) )
    log('cache_path:', os_file_check(cache_path ))
    x1 = str( db[ keyi ] )[:100]
    log('Decode:', x1 )

    # log( str(msgpack.unpackb( db[ keyi ]))[:100] )
    db.close()


    #### Check by SQLITE
    df = cache_check(cache_path, tablename=tablename)
    v  = df['value'].values[-1]
    x2 = str(msgpack.unpackb( v ))[:100]
    log('Decode using sqlite\n', x2 )
    log('ref\n',x0)
    assert x1 == x2, f'mismatch retrieved vs actual,\n{str(dd)[:100]},\n{x2}'



###############################################################################################
@dataclass
class cfgCache:
    ## dacite.from_dict(data_class=cfgCache, data= cfg['cache'])
    dir:             Path
    cache_path:      Path
    replace_symlink: bool
    keep_at_least  : int
    tablename      : str



############################################################################################
############################################################################################
def fake_get_id(k=25):
   return  ''.join(random.choices(string.ascii_uppercase +  string.digits, k=k))



def cache_sync_file(cfg:Dict):
    """ Sync cache with correct name,   From Adserver make_cache
    Docs::

    """

    try:
        cfg_cache = cache_get_cfg(cfg['cache'])

        log(f"Loaded: {cfg_cache}")
        if cfg_cache.replace_symlink:
            sym = cfg_cache.dir / pathlib.Path("cache.db")

            # If "cache.db" already exists, first create "tmp.db" and swap with "cache.db"
            if sym.exists() or sym.is_symlink():
                tmp = cfg_cache.dir / "tmp.db"
                if tmp.exists() or tmp.is_symlink():
                    os.remove(tmp)
                os.symlink(cfg_cache.cache_path, tmp)
                os.rename(tmp, sym)
            else:
                os.symlink(cfg_cache.cache_path, sym)

        if cfg_cache.keep_at_least > 1:
            cache_files = sorted(cfg_cache.dir.glob("cache-*-*.db"), key=os.path.getmtime)
            number_delete = len(cache_files) - cfg_cache.keep_at_least
            if number_delete > 0:
                for file in cache_files[:number_delete]:
                    log.info(f"Deleting old cache: {file}")
                    file.unlink()

    except Exception as e:
        loge(e)
        logw(traceback.format_exc())
        if cfg_cache.cache_path.exists():
            os.remove(cfg_cache.cache_path)
        return 1

    return 0



def cache_get_cfg(cfg:Dict)-> dataclass:

   try :
       cfg_cache = dacite.from_dict(data_class=cfgCache, data= cfg)
       return cfg_cache
   except Exception as e :
       log(e)


def cache_get_session(cfg:Dict, encoding_engine=None, max_retry=3):
    """ get a session to store the key,value

    Args:
        cfg (Dict): config as Dict-like dot notation
        encoding_engine (str, optional): encoding

    Returns:
        _type_: _description_
    """
    cache_path  = cfg.get('dir',       "ztmp/example.sqlite" )
    cache_table = cfg.get('tablename', "keyvalue")
    ii = 0
    while ii < max_retry :
        try :
            os_makedirs(cache_path)

            if encoding_engine == 'msgpack':
                db = SqliteDict(cache_path, tablename= cache_table, outer_stack=False,
                                encode=msgpack.packb, decode=msgpack.unpackb )
            else :
                db = SqliteDict(cache_path, tablename= cache_table, outer_stack=False,
                                encode=json.dumps, decode=json.loads )

            return db
        except Exception as e :
            logw(e)
            time.sleep(ii*5)
            log(f"Retry {ii+1}")


def cache_check(cache_path:str, tablename:str="ctr_quakey", nrows=100)->pd.DataFrame:
    #### Check sqlite
    dbEngine=sqlalchemy.create_engine('sqlite:///' + cache_path )
    df = pd.read_sql(f'select * from {tablename} LIMIT {nrows} ',dbEngine)
    log(df)
    return df



def cache_update(db, df:pd.DataFrame=None, colkey:str='key', colval:str='value', kbatch=30):
    """ Update cache from dataframe

    """
    vv = df[[ colkey, colval ]].values
    n_insert = 0
    for ii in range(0, len(df)):
        try:
           db[ vv[ii, 0] ] = vv[ii, 1]
           n_insert += 1
           if ii % kbatch == 0 :
              db.commit()
        except Exception as e :
           log(e)

    db.close()
    return n_insert






########################################################################################
if __name__ == "__main__":
    fire.Fire()








