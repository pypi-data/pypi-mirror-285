""" Entries for common utilities
Docs::

     https://github.com/davidaurelio/hashids-python


"""
import json
import os,sys,time, datetime, random,re
from typing import Any, Callable, Sequence, Dict, List, Union,Optional
import mmh3, fire, xxhash
import pandas as pd, numpy as np

try :
  from .utilmy_parallel import (pd_read_file, pd_read_file2)
  from .utilmy_log import log,log2, logw,loge
except:
  from utilmy_parallel import (pd_read_file, pd_read_file2)
  from utilmy_log import log,log2, logw,loge




##########################################################################################    
def config_load(
    config: Union[str, Dict, None] = None,
    to_dataclass: bool = True,
    config_field_name: str = None,
    environ_path_default: str = "config_path_default",
    path_default: str = None,
    config_default: dict = None,
    save_default: bool = False,
    verbose=0,
) -> dict:
    """Universal config loader: .yaml, .conf, .toml, .json, .ini .properties INTO a dict
    Doc::

        config_path:    str  = None,
        to_dataclass:   bool = True,  True, can access dict as dot   mydict.field
        config_field_name :  str  = Extract sub-field name from dict

        --- Default config
        environ_path_default: str = "config_path_default",
        path_default:   str  = None,
        config_default: dict = None,
        save_default:   bool = False,

       -- Priority steps
        1) load config_path
        2) If not, load in USER/.myconfig/.config.yaml
        3) If not, create default save in USER/.myconfig/.config.yaml
        Args:
            config_path:    path of config or 'default' tag value
            to_dataclass:   dot notation retrieval

            path_default :  path of default config
            config_default: dict value of default config
            save_default:   save default config on disk
        Returns: dict config
    """
    import pathlib
    import yaml
    if config is None :
        return {}
    
    if isinstance(config, dict):
        return config

    else:
        config_path = config

    #########Default value setup ###########################################
    if path_default is None:
        default_val = str(os.path.dirname(os.path.abspath(__file__))) + "/myconfig/config.yaml"
        config_path_default = os.environ.get(environ_path_default, default_val)
        path_default = os.path.dirname(config_path_default)
    else:
        config_path_default = path_default
        path_default = os.path.dirname(path_default)

    if config_default is None:
        config_default = {"field1": "test", "field2": {"version": "1.0"}}

    #########Config path setup #############################################
    if config_path is None or config_path == "default":
        log(f"Config: Using {config_path_default}")
        config_path = config_path_default
    else:
        config_path = pathlib.Path(config_path)

    ######### Load Config ##################################################
    try:
        log("Config: Loading ", config_path)
        if config_path.suffix in {".yaml", ".yml"}:
            # Load yaml config file
            with open(config_path, "r") as yamlfile:
                config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)

            if isinstance(config_data, dict):
                cfg = config_data
            else:
                dd = {}
                for x in config_data:
                    for key, val in x.items():
                        dd[key] = val
                cfg = dd

        elif config_path.suffix == ".json":
            cfg = json.loads(config_path.read_text())

        elif config_path.suffix in {".properties", ".ini", ".conf"}:
            from configparser import ConfigParser

            cfg = ConfigParser()
            cfg.read(str(config_path))

        elif config_path.suffix == ".toml":
            cfg = toml.loads(config_path.read_text())
        else:
            raise Exception(f"not supported file {config_path}")

        if config_field_name in cfg:
            cfg = cfg[config_field_name]

        if verbose >= 2:
            log(cfg)

        if to_dataclass:  ### myconfig.val  , myconfig.val2
            from box import Box

            return Box(cfg)
        return cfg

    except Exception as e:
        log(f"Config: Cannot read file {config_path}", e)

    ######################################################################
    log("Config: Using default config")
    log(config_default)
    if save_default:
        log(f"Config: Writing config in {config_path_default}")
        os.makedirs(path_default, exist_ok=True)
        with open(config_path_default, mode="w") as fp:
            yaml.dump(config_default, fp, default_flow_style=False)

    return config_default


def fire_Fire():
    """Executes `fire.Fire()` function while optionally enabling profiling using Pyinstrument.
    Docs::
    
        If the `pyinstrument` environment variable is set to `"1"`, 
        the function starts the Profiler from the Pyinstrument library, 
        executes the `fire.Fire()` function, stops the Profiler, 
        and prints the profiling output. 
    """    
    if os.environ.get('pyinstrument', "0") == "1":
        print("##### Pyinstrument profiling Start ############")            
        import pyinstrument
        profiler = pyinstrument.Profiler()
        profiler.start()

        fire.Fire()
        profiler.stop()  
        print(profiler.output_text(unicode=True, color=True))
    else:
        fire.Fire()




##########################################################################################
def test_cache():
   from src.utils.utilmy_aws import pd_read_file_s3
   os.environ['CACHE_ENABLE'] = "1"
   os.environ['CACHE_DIR']    = "ztmp/cache/mycache2"
   os.environ['CACHE_TTL']    = "100"
   os.environ['CACHE_SIZE']    = "1000000000"

   @diskcache_decorator
   def myfun(x1,x2,y1="y1", y2=None):
     time.sleep(5)
     return f"{x1}-{x2}-{str(y1)}-{str(y2)}"

   v1= myfun("x1", 'x2', ['y1'], y2={'y2'})

   
   t0= time.time()
   v2= myfun("x1", 'x2', ['y1'], y2={'y2'})
   assert v1 == v2
   assert time.time()-t0 < 5.0, "Not cached"


   os.environ['CACHE_ENABLE'] = "0"
   t0= time.time()
   v3= myfun("x1", 'x2', ['y1'], y2={'y2'})
   assert v1 == v3
   assert time.time()-t0 > 5.0, "Error Using cached"


def code_find_duplicates(dirin, dirout="ztmp/df_duplicate.csv"):
    """ Find duplicates in code

      python src/utils/utilmy_base.py  code_find_duplicates  --dirin src/data/


    """
    import os, re

    flist = glob_glob(dirin + "/**/*.py")
    
    # Create a dictionary to store function names and their occurrences
    functions = {}

    # Define a regular expression to match Python function definitions
    regex = r'^def\s+([\w]+)\s*\('

    for fi in flist:
        if not fi.endswith('.py'): continue
        with open(fi, 'r') as file1:
            lines = file1.readlines()

        for line in lines:
            match = re.search(regex, line)
            if match:
                # Get the function name from the match
                function_name = match.group(1)
                functions[function_name] = 1 + functions.get(function_name, 0)  

    res = []
    for function_name, count in functions.items():
        if count > 1:
            res.append([function_name, count])

    res = pd.DataFrame(res, columns=['name', 'cnt'])
    res = res.sort_values(['cnt'], ascending=0)
    pd_to_file(res, dirout, show=1)


def diskcache_load( db_path_or_object="", size_limit=100000000000, verbose=True ):    
    """ val = cache[mykey]
    """
    import diskcache as dc
    from utilmy import os_makedirs
    global cache_diskcache37

    if not isinstance(db_path_or_object, str ) :
       return db_path_or_object

    os_makedirs(db_path_or_object) 

    cache_diskcache37 = dc.Cache(db_path_or_object, size_limit= size_limit)
    log(f"cache_dir: {db_path_or_object}")
    log('Cache size/limit', len(cache_diskcache37), cache_diskcache37.size_limit, str(cache_diskcache37))
    return cache_diskcache37


def diskcache_decorator(func, ttl_sec=None):
    """ Caching of data
    Docs:

       os.environ['CACHE_ENABLE'] = "1"
       os.environ['CACHE_DIR']    = "ztmp/cache/mycache2"
       os.environ['CACHE_TTL']    = "10"
       os.environ['CACHE_SIZE']    = "1000000000"

       dirin= "ztmp/ctr/latest/data/*.parquet"
       df1 = pd_read_file_s3(path_s3= dirin)
       df2 = pd_read_file_s3(path_s3= dirin)
    """ 
    #from src.utils.utilmy_base import hash_int64
    import os
    def wrapper(*arg, **args):
        debug = True if os.environ.get('CACHE_DEBUG', "0") =="1" else False
        if debug : log('cache: start')
        flag = os.environ.get('CACHE_ENABLE', '')
        
        if len(flag) < 1 or flag=='0' :
           # log(os.environ)
           return func(*arg, **args)

        if debug : log('cache: load')
        ttl_sec    = int( os.environ.get('CACHE_TTL', 7200))
        dir0       = os.environ.get('CACHE_DIR', "ztmp/zcache/")
        size_limit = int(os.environ.get('CACHE_SIZE', 10**9) )
        global cache_diskcache37
        try :
           len(cache_diskcache37)
        except : 
           cache_diskcache37 = diskcache_load(dir0, size_limit= size_limit, verbose=True)


        argid = hash_int64( str(arg) + str(args))
        try :
           dfx= cache_diskcache37[argid]
           log("cache: fetched from:", dir0, argid, )
           return dfx
        except :
            dfx = func(*arg, **args)
            cache_diskcache37.set(argid, dfx, expire= ttl_sec)
            log("cache: data from Real, saved in ", argid, )
            return dfx

    return wrapper


##########################################################################################
def test_globfilter():

      flist = [ "s3://l1/l2/fa.parquet",
             "s3://l1/l2/l3/fb.parquet",
             "s3://l1/l2/l3/l4/fc.parquet",
             "s3://l1/l2/l3/l4/l5/fd.parquet",
             "s3://l1/fc.parquet",
      ]

      root = "s3://l1/l2"
      for i in range(0, 3):
         log(i)
         assert len(glob_filter_dirlevel(flist, root,  lower_level=i-1, upper_level=i+1))   == 3

      assert len(glob_filter_dirlevel(flist, root,  lower_level=-2, upper_level=-1)) == 1
      assert len(glob_filter_dirlevel(flist, root,  lower_level=-2, upper_level=-2)) == 0


def test_globlist():
    ll = [   's3://aaa/clk_202308.parquet',   's3://aaa/df_20231109.parquet',  ]
    x1 = glob_filter_filedate(ll, ymd_min=202310, date_size=6) 
    assert ll[1] == x1[0]

    x0 = glob_filter_filedate(ll, ymd_max=202310, date_size=6) 
    assert ll[0] == x0[0]
    log("alll test passed: glob_list_filter")


##########################################################################################
@diskcache_decorator
def pd_to_dict(df:pd.DataFrame, colkey:Union[str,List], colval:str=None, key_merge_sep="-")->Dict:
    """ dataframe into Dict: key:val    key can be a merged-key with "-"
    :param df:
    :param colkey:
    :param colval:
    :return:
    """
    from src.utils.utilmy_aws import pd_read_file_s3
    if isinstance(df, str):
        df = pd_read_file_s3(df)

    if df is None or len(df) < 1 :
        logw("pd_to_dict, empty input dataframe df")
        return {}

    try :
         
        if isinstance(colkey, str): 
            colkey2 = colkey 
        else :
            colkey2     = key_merge_sep.join(colkey)
            df[colkey2] = df.apply(lambda x:  key_merge_sep.join([ str(x[ci]) for ci in colkey     ]) , axis=1 )
            log('using merged key: ', colkey2)
            # log(df) 

        ##### value  
        if isinstance(colval, str) :
           df1 = df.set_index(colkey2)
           df1 = df1[colval].to_dict()  ### Direct Mapping: colkey2 --> val
           return df1

        else :  ### colkey --> { "col1": val1, "col2": val2 }          
           df1 = df.set_index(colkey2)
           df1 = df1.to_dict(orient='index')
           return df1

    except Exception as e:
        logw(" pd_to_dict cannot convert: ", e)
        return {}


def pd_date_add(df:pd.DataFrame, colnew_list:list=None,  colymd='ymd', )->pd.DataFrame:
    """
        %a	Abbreviated weekday name.	Sun, Mon, ...
        %A	Full weekday name.	Sunday, Monday, ...
        %w	Weekday as a decimal number.	0, 1, ..., 6
        %d	Day of the month as a zero-padded decimal.	01, 02, ..., 31

    """
    for colnew in colnew_list:
        if colnew == 'dayweek':
            df[colnew] = df[colymd].apply(lambda x : int(date_now(x, fmt_input='%Y%m%d', fmt='%w', )) if len(str(x)) ==8 else -1 )

        if colnew == 'daymonth':
            df[colnew] = df[colymd].apply(lambda x : str(x)[-2:] )

        if colnew == 'holidays':
            dd= {
                "20220429": "Showa Day",
                "20220503": "Constitution Memorial Day",
                "20220504": "Greenery Day",
                "20220505": "Children's Day",
                "20220718": "Marine Day",
                "20220811": "Mountain Day",
                "20220919": "Respect for the Aged Day",
                "20220923": "Autumnal Equinox Day",
                "20221010": "Sports Day",
                "20221103": "Culture Day",
                "20221123": "Labor Thanksgiving Day",
                "20221231": "Eve New year",

                "20230101": "New Year's Day",
                "20230109": "Coming of Age Day",
                "20230211": "National Foundation Day",
                "20230223": "The Emperor's Birthday",
                "20230321": "Vernal Equinox Day",
                "20230429": "Showa Day",
                "20230503": "Constitution Memorial Day",
                "20230504": "Greenery Day",
                "20230505": "Children's Day",
                "20230717": "Marine Day",
                "20230811": "Mountain Day",
                "20230918": "Respect for the Aged Day",
                "20230923": "Autumnal Equinox Day",
                "20231009": "Sports Day",
                "20231103": "Culture Day",
                "20231123": "Labor Thanksgiving Day",
                "20231231": "Eve New year",

                '20240101': "New Year's Day",
                '20240108': "Coming of Age Day",
                '20240211': "National Foundation Day",
                '20240223': "The Emperor's Birthday",
                '20240320': "Vernal Equinox Day",
                '20240429': "Showa Day",
                '20240503': "Constitution Memorial Day",
                '20240504': "Greenery Day",
                '20240505': "Children's Day",
                '20240715': "Marine Day",
                '20240811': "Mountain Day",
                '20240916': "Respect for the Aged Day",
                '20240923': "Autumnal Equinox Day",
                '20241014': "Sports Day",
                '20241103': "Culture Day",
                '20241104': "National Culture Day Holiday",
                '20241123': "Labor Thanksgiving Day"
            }

            df[colnew] = df[colymd].apply(lambda x : 1 if str(x) in dd else 0  )

    return df


def date_extract(ymd_str, date_size=6):
    import re
    matches=[]
    if date_size==8 : matches = re.findall(r'\d{8}', ymd_str)
    if date_size==6 : matches = re.findall(r'\d{6}', ymd_str)
    return matches


def glob_filter_filedate(flist, ymd_min=190112, ymd_max=21001010, date_size=6, include_error=True):
   """ Filter files based on file name YMD dates
   
   """ 
   flist2 =[]
   for fi in flist :
      try :
          ymd_list = date_extract(fi, date_size)
          ym       = int( ymd_list[0])          
          if  ymd_min <= ym <= ymd_max :
              flist2.append(fi)
      except Exception as e :
          log(e)
          if include_error: 
             flist2.append(fi)

   return flist2 


def glob_filter_dirlevel(flist, root,  lower_level=0,  upper_level=0):
    """ Filter Level to level
    Docs: 
      flist = [ "s3://l1/l2/fa.parquet",
             "s3://l1/l2/l3/fb.parquet",
             "s3://l1/l2/l3/l4/fc.parquet",
            "s3://l1/l2/l3/l4/l5/fd.parquet",
             "s3://l1/fc.parquet",
       ]

      root = "s3://l1/l2"
      glob_filter_dirlevel(flist, root, level=0, lower_level=-1, upper_level=1) 
    """ 
    root   = root if root[-1] == "/" else root +"/"
    nbase  = len(root.split("/")) 
    flist2 = []

    for fi in flist :
        n = len(fi.split("/")) 
        n2= n - nbase
        #log(nbase, n2)
        if lower_level <= n2 <= upper_level:
              flist2.append(fi)

    return flist2 


def json_load(fpath:str)->Dict:
    with open(fpath, mode='r') as fp:
        ddict = json.load(fp)
    return ddict


def json_save(ddict:Dict, fpath:str, indent:int=2, show:int=0, oneline_perkey=1)->None:
    class MyEncoder(json.JSONEncoder):
        ### to handle numpy type 
        ### https://stackoverflow.com/questions/27050108/convert-numpy-type-to-python
        def default(self, obj):
            val = getattr(obj, "tolist", lambda: obj )()
            return val                                        
            #return super(MyEncoder, self).default(obj)
    if show>0:
       log(ddict)

    sep = None
    if oneline_perkey>0:
        txt = json.dumps(ddict, indent=0, cls=MyEncoder,)
        txt = txt.replace(",\n", ",")                        
        txt = txt.replace(",\n", ",")    
        txt = txt.replace("[\n", "[ ")                      
        txt = txt.replace("\n],", " ],\n") 
        txt = txt.replace("},", "},\n\n")     
        txt = txt.replace(",", ", ")     
                      
        with open(fpath, mode='w') as fp:
           fp.write(txt)
    else :
        with open(fpath, mode='w') as fp:
            json.dump(ddict, fp, indent=indent, cls=MyEncoder,)
    log(fpath)


def to_float(x, default=0.0):
    try:
        return float(x)
    except:
        return default


def to_int(x, default=-1):
    try:
        return int(x)
    except:
        return default


def to_int32(x, default=-1):
    try:        
        x1 = int(x)
        if x1> 2147483647 or x1 < -2147483648 :
            return x1 % 2147483648  #### % 2**31-1
        return x1
    except:
        return default



def log_pd(df):
    log(list(df.columns), "\n", df.shape, "\n")


def hash_int32(xstr:str):
  return xxhash.xxh32_intdigest(str(xstr),seed=0)


def hash_int64(xstr:str):
  return xxhash.xxh64_intdigest(str(xstr),seed=0)


##########################################################################################
def str_sanitize_list(xstr:str, sep=",")->str:
    """ Safe String
    """
    slist = xstr.split(sep)
    sall  = ""
    for si in slist:
        s2   = str_sanitize(si)
        sall = sall + "'" + s2 + f"'{sep}"
    return sall[:-1]


def str_sanitize(xstr:str, regex_check='[^a-zA-Z0-9]')->str:
    """ Safe String
    """
    sanitized_string = re.sub(regex_check, '', xstr)
    if len(xstr) != len(sanitized_string):
        logw(f"sql_sanitized: remove char:  {xstr}")
    return sanitized_string


##########################################################################################
def glob_glob(dirin="", file_list=[], exclude="", include_only="",
            min_size_mb=0, max_size_mb=500000,
            ndays_past=-1, nmin_past=-1,  start_date='1970-01-02', end_date='2050-01-01',
            nfiles=99999999, verbose=0, npool=1
    ):
    """ Advanced glob.glob filtering.
    Docs::

        dirin:str = "": get the files in path dirin, works when file_list=[]
        file_list: list = []: if file_list works, dirin will not work
        exclude:str  = ""
        include_only:str = ""
        min_size_mb:int = 0
        max_size_mb:int = 500000
        ndays_past:int = 3000
        start_date:str = '1970-01-01'
        end_date:str = '2050-01-01'
        nfiles:int = 99999999
        verbose:int = 0
        npool:int = 1: multithread not working

        https://www.twilio.com/blog/working-with-files-asynchronously-in-python-using-aiofiles-and-asyncio
    """
    import glob, copy, datetime as dt, time
    if dirin and not file_list:
        files = glob.glob(dirin, recursive=True)
        files = sorted(files)

    if file_list:
        files = file_list

    ####### Exclude/Include  ##################################################
    for xi in exclude.split(","):
        if len(xi) > 0:
            files = [  fi for fi in files if xi not in fi ]

    if include_only:
        tmp_list = [] # add multi files
        for xi in include_only.split(","):
            if len(xi) > 0:
                tmp_list += [  fi for fi in files if xi in fi ]
        files = sorted(set(tmp_list))

    ####### size filtering  ##################################################
    if min_size_mb != 0 or max_size_mb != 0:
        flist2=[]
        for fi in files[:nfiles]:
            try :
                if min_size_mb <= os.path.getsize(fi)/1024/1024 <= max_size_mb :   #set file size in Mb
                    flist2.append(fi)
            except : pass
        files = copy.deepcopy(flist2)

    #######  date filtering  ##################################################
    now    = time.time()
    cutoff = 0

    if ndays_past > -1 :
        cutoff = now - ( abs(ndays_past) * 86400)

    if nmin_past > -1 :
        cutoff = cutoff - ( abs(nmin_past) * 60  )

    if cutoff > 0:
        if verbose > 0 :
            print('now',  dt.datetime.utcfromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S"),
                   ',past', dt.datetime.utcfromtimestamp(cutoff).strftime("%Y-%m-%d %H:%M:%S") )
        flist2=[]
        for fi in files[:nfiles]:
            try :
                t = os.stat( fi)
                c = t.st_ctime
                if c < cutoff:             # delete file if older than 10 days
                    flist2.append(fi)
            except : pass
        files = copy.deepcopy(flist2)

    ####### filter files between start_date and end_date  ####################
    if start_date and end_date:
        start_timestamp = time.mktime(time.strptime(str(start_date), "%Y-%m-%d"))
        end_timestamp   = time.mktime(time.strptime(str(end_date), "%Y-%m-%d"))
        flist2=[]
        for fi in files[:nfiles]:
            try:
                t = os.stat( fi)
                c = t.st_ctime
                if start_timestamp <= c <= end_timestamp:
                    flist2.append(fi)
            except: pass
        files = copy.deepcopy(flist2)

    return files


def os_system(cmd:str, doprint=False):
  """ Get stdout, stderr from Command Line into  a string varables  mout, merr
  Docs::
       Args:
           cmd: Command to run subprocess
           doprint=False: int
       Returns:
           out_txt, err_txt
  """
  import subprocess
  try :
    p          = subprocess.run( cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, )
    mout, merr = p.stdout.decode('utf-8'), p.stderr.decode('utf-8')
    if doprint:
      l = mout  if len(merr) < 1 else mout + "\n\nbash_error:\n" + merr
      print(l)

    return mout, merr
  except Exception as e :
    print( f"Error {cmd}, {e}")


def os_makedirs(dir_or_file:str):
    """function os_makedirs
    Docs::
        Args:
            dir_or_file:
        Returns:
            None
    """
    if os.path.isfile(dir_or_file) or "." in dir_or_file.split("/")[-1] :
        os.makedirs(os.path.dirname(os.path.abspath(dir_or_file)), exist_ok=True)
        f = open(dir_or_file,'w')
        f.close()
    else :
        os.makedirs(os.path.abspath(dir_or_file), exist_ok=True)


def os_file_check(fpath:str):
   """Check file stat info
   Docs::
        Args:
            fpath: str - File patj
        Returns:
            flag: True | False
   """
   import os, time

   flist = glob_glob(fpath)
   flag = True
   for fi in flist :
       try :
           log(fi,  os.stat(fi).st_size*0.001, time.ctime(os.path.getmtime(fi)) )
       except :
           log(fi, "Error File Not exist")
           flag = False
   return flag


def load_function_uri(uri_name: str="MyFolder/myfile.py:my_function")->Any:
    """ Load dynamically Python function/Class Object from string name
    Doc::

        myfun = load_function_uri(uri_name: str="MyFolder/utilmy_base.py:pd_random")

        -- Pandas CSV case : Custom One
        #"dataset"        : "preprocess.generic:pandasDataset"

        -- External File processor :
        "dataset"        : "MyFolder/preprocess/myfile.py:pandasDataset"


        Args:
            package (string): Package's name. Defaults to "mlmodels.util".
            name (string): Name of the function that belongs to the package.

        Returns:
            Returns the function of the package.

        Example:
            from utilmy import utils
            function = utils.load_function_uri("datetime.timedelta",)
            print(function())#0:00:00

    """
    import importlib, sys
    from pathlib import Path


    uri_name = uri_name.replace("\\", "/")

    if ":" in uri_name :
        pkg = uri_name.split(":")
        if ":/" in uri_name:  ### windows case
           pkg = uri_name.split("/")[-1].split(":")

        assert len(pkg) > 1, "  Missing :   in  uri_name module_name:function_or_class "
        package, name = pkg[0], pkg[1]
        package = package.replace(".py", "")

    else :
        pkg = uri_name.split(".")
        package = ".".join(pkg[:-1])
        package = package.replace(".py", "")
        name    = pkg[-1]


    try:
        #### Import from package mlmodels sub-folder
        return  getattr(importlib.import_module(package), name)

    except Exception as e1:
        try:
            ### Add Folder to Path and Load absoluate path module
            path_parent = str(Path(package).parent.parent.absolute())
            sys.path.append(path_parent)
            log(path_parent)

            #### import Absolute Path model_tf.1_lstm
            log(str(package))
            model_name   = Path(package).stem  # remove .py
            package_name = str(Path(package).parts[-2]) + "." + str(model_name)

            log(package_name, model_name)
            return  getattr(importlib.import_module(package_name), name)

        except Exception as e2:
            raise NameError(f"Module {pkg} notfound, {e1}, {e2}")


def load_module_uri(uri_name: str="MyFolder/myfile.py")->Any:
    """ Load dynamically Python Module from string name
    Doc::

        myModule = load_module_uri(uri_name: str="MyFolder/utilmy_base.py)

        -- Pandas CSV case : Custom One
        #"dataset"        : "preprocess.generic"

        -- External File processor :
        "dataset"        : "MyFolder/preprocess/myfile.py"


        Args:
            package (string): Package's name. Defaults to "mlmodels.util".
            name (string): Name of the function that belongs to the package.

        Returns:
            Returns the module

        Example:
            from utilmy import utils
            utils.load_module_uri("datetime",)
            
    """
    import importlib, sys
    from pathlib import Path

    uri_name = uri_name.replace("\\", "/").replace("//","/")
    package  = uri_name.replace(".py", "")

    try:
        modulex = importlib.import_module(package)
        importlib.reload(modulex)
        return modulex        
        # reload a module 

    except Exception as e1:
        try:
            ### Add Folder to Path and Load absoluate path module
            path_parent = str(Path(package).parent.parent.absolute())
            sys.path.append(path_parent)
            log(path_parent)

            #### import Absolute Path model_tf.1_lstm
            # log(str(package))
            model_name   = Path(package).stem  # remove .py
            package_name = str(Path(package).parts[-1]) + "." + str(model_name)

            log(package_name, model_name)
            return  importlib.import_module(package_name)

        except Exception as e2:
            raise NameError(f"Module {uri_name} notfound, {e1}, {e2}")


def os_state_save(obj,list_vars:List[str], path:str)->None:
    """ Save all members of an object on disk

    Docs::

        os_state_save(obj=self, list_vars=['mydict'],  path='ztmp/')

    """
    dirout  = os_path_norm( path )
    os_makedirs(dirout)
    ii = 0
    for x in list_vars:
       try :
          xname = x + ".pkl"
          save( getattr(obj, x ), dirout + f"/{xname}")
          ii = ii+1
       except Exception as e :
          log(e)

    log(f"Save state to {dirout}")


def os_state_load(obj, list_vars:List[str], path:str, show=False)->None:
    """ Load all members of an object on disk

    Docs::

        os_state_load(obj=self, list_vars=['mydict'],  path='ztmp/')

    """
    # from utilmy import load, os_makedirs

    if show:
        log(f"\nLoad state from {path}")
    dirout  = os_path_norm( path )
    ii = 0
    for x in list_vars:
       try :
          xname = x + ".pkl"
          key   = x
          val = load(  dirout + f"/{xname}")
          setattr(obj,key,val)
          if show:
              log(f"   {key}:",   getattr(obj, key))
          ii = ii+1
       except Exception as e :
          log(e)
    log(f"loaded {ii} objects from {dirout}")


def os_path_norm(path:str, to_absolute:bool=True)->Union[str]:
    """ Clean unique normalized path with Unix "/" format
    """
    p1 = path.replace("\\", "/") +"/"
    if to_absolute:
       p1 = os.path.abspath(p1) + "/"
    p1 = p1.replace("//", "/")
    return p1


def os_path_getsize(dirin='mypath/*/', **kw):
    flist = glob_glob(dirin, **kw)
    log(f"N files: {len(flist)}")
    total = 0
    for fi in flist :
      try:
         total = total + os.path.getsize(fi)
      except Exception as e :
         log(fi, e)
    return total      


def os_rename(dirfrom, dirto,):
    try :
      if not os.path.isdir(dirto):
         # os_makedirs(  "".join(dirto.split("/")[:-1]) )
         dirfrom= dirfrom if dirfrom[-1] != "/" else dirfrom[:-1]
         os.rename(dirfrom, dirto)
    except Exception as e :
      log(e)


def save(dd, to_file="", verbose=False):
  """function save
  Args:
      dd:
      to_file:
      verbose:
  Returns:

  """
  import pickle, os
  os.makedirs(os.path.dirname(to_file), exist_ok=True)
  pickle.dump(dd, open(to_file, mode="wb") , protocol=pickle.HIGHEST_PROTOCOL)


def load(to_file=""):
  """function load
  Args:
      to_file:
  Returns:

  """
  import pickle
  dd =   pickle.load(open(to_file, mode="rb"))
  return dd




### Generic Date function   #####################################################
def date_range(start_dt=None, end_dt=None, fmt_input="",   fmt="%Y-%m-%d-%H", freq="H"):
    import datetime

    #start_date = datetime.datetime.now() - datetime.timedelta(weeks=1)
    date_list = pd.date_range(start=start_dt, end=end_dt, freq=freq)

    formatted_dates = [date.strftime(fmt) for date in date_list]
    return formatted_dates


def date_now(datenow:Union[str,int,float,datetime.datetime]="", fmt="%Y%m%d",
             add_days=0,  add_mins=0, add_hours=0, add_months=0,add_weeks=0,
             timezone_input=None,
             timezone='UTC', # 'Asia/Tokyo',
             fmt_input="%Y-%m-%d",
             force_dayofmonth=-1,   ###  01 first of month
             force_dayofweek=-1,
             force_hourofday=-1,
             force_minofhour=-1,
             returnval='str,int,datetime/unix')->Union[str, int, datetime.datetime, ]:
    """ One liner for date Formatter
    Doc::
        datenow: 2012-02-12  or ""  emptry string for today's date.
        fmt:     output format # "%Y-%m-%d %H:%M:%S %Z%z"
        date_now(timezone='Asia/Tokyo')    -->  "20200519"   ## Today date in YYYMMDD
        date_now(timezone='Asia/Tokyo', fmt='%Y-%m-%d')    -->  "2020-05-19"
        date_now('2021-10-05',fmt='%Y%m%d', add_days=-5, returnval='int')    -->  20211001
        date_now(20211005, fmt='%Y-%m-%d', fmt_input='%Y%m%d', returnval='str')    -->  '2021-10-05'
        date_now(20211005,  fmt_input='%Y%m%d', returnval='unix')    -->
         integer, where Monday is 0 and Sunday is 6.
        date_now(1634324632848, fmt='%Y-%m-%d', fmt_input='%Y%m%d', returnval='str')    -->  '2021-10-05'
    """
    from pytz import timezone as tzone
    import datetime, time

    if timezone_input is None:
        timezone_input = timezone

    sdt = str(datenow)

    if isinstance(datenow, datetime.datetime):
        now_utc = datenow

    elif (isinstance(datenow, float) or isinstance(datenow, int))  and  datenow > 1600100100 and str(datenow)[0] == "1"  :  ### Unix time stamp
        ## unix seconds in UTC
        # fromtimestamp give you the date and time in local time
        # utcfromtimestamp gives you the date and time in UTC.
        #  int(time.time()) - date_now( int(time.time()), returnval='unix', timezone='utc') == 0
        now_utc = datetime.datetime.fromtimestamp(datenow, tz=tzone("UTC") )   ##
    elif  len(sdt) >7 :  ## date in string
        if "%" in fmt_input or len(sdt)==8 :
           now_utc = datetime.datetime.strptime(sdt, fmt_input)
        else :
           import dateparser
           now_utc = dateparser.parse(sdt) ###Automatic date parser

    else:
        now_utc = datetime.datetime.now(tzone('UTC'))  # Current time in UTC
    # now_new = now_utc.astimezone(tzone(timezone))  if timezone != 'utc' else  now_utc.astimezone(tzone('UTC'))
    #now_new = now_utc.astimezone(tzone('UTC'))  if timezone in {'utc', 'UTC'} else now_utc.astimezone(tzone(timezone))
    if now_utc.tzinfo is None:
        now_utc = tzone(timezone_input).localize(now_utc)

    now_new = now_utc if timezone in {'utc', 'UTC'} else now_utc.astimezone(tzone(timezone))

    ####  Add months
    now_new = now_new + datetime.timedelta(days=add_days + 7*add_weeks, hours=add_hours, minutes=add_mins,)
    if add_months!=0 :
        from dateutil.relativedelta import relativedelta
        now_new = now_new + relativedelta(months=add_months)


    #### Force dates
    if force_dayofmonth >=0 :
        now_new = now_new.replace(day=force_dayofmonth)

    if force_dayofweek >=0 :
        actual_day = now_new.weekday()
        days_of_difference = force_dayofweek - actual_day
        now_new = now_new + datetime.timedelta(days=days_of_difference)

    if force_hourofday >=0 :
        now_new = now_new.replace(hour=force_hourofday)

    if force_minofhour >=0 :
        now_new = now_new.replace(minute=force_minofhour)


    if   returnval == 'datetime': return now_new ### datetime
    elif returnval == 'int':      return int(now_new.strftime(fmt))
    elif returnval == 'unix':     return datetime.datetime.timestamp(now_new)  #time.mktime(now_new.timetuple())
    else:                         return now_new.strftime(fmt)


##########################################################################################
def do_assert(left, right, msg="", verbose=0):
   try :
      isok = left == right
   except Exception as e :
      log(left)
      log(right)
      raise Exception(e)



##########################################################################################
def pd_to_file(df:pd.DataFrame, filei:str,  check=0, verbose=True, show='shape',   **kw):
  """function pd_to_file.
  Doc::

        Args:
            df:
            filei:
            check:
            verbose:
            show:
            **kw:
        Returns:

  """
  import os, gc
  from pathlib import Path
  parent = Path(filei).parent
  os.makedirs(parent, exist_ok=True)
  ext  = os.path.splitext(filei)[1]
  if   ext == ".pkl" :       df.to_pickle(filei,  **kw)
  elif ext == ".parquet" :   df.to_parquet(filei, **kw)
  elif ext in [".csv" ,".txt"] :  df.to_csv(filei, **kw)
  else :
      log('No Extension, using parquet')
      df.to_parquet(filei + ".parquet", **kw)

  if verbose in [True, 1] :  log(filei)
  if show == 'shape':        log(df.shape)
  if show in [1, True] :     log(df)

  if check in [1, True, "check"] : log('Exist', os.path.isfile(filei))
  gc.collect()


def pd_random(ncols=7, nrows=100):
   """function pd_random
   Args:
       ncols:
       nrows:
   Returns:

   """
   import pandas as pd
   ll = [[ random.random() for i in range(0, ncols)] for j in range(0, nrows) ]
   df = pd.DataFrame(ll, columns = [str(i) for i in range(0,ncols)])
   return df


def pd_generate_data(ncols=7, nrows=100):
    """ Generate sample data for function testing categorical features
    """
    np.random.seed(444)
    numerical    = [[ random.random() for i in range(0, ncols)] for j in range(0, nrows) ]
    df = pd.DataFrame(numerical, columns = [str(i) for i in range(0,ncols)])
    df['cat1']= np.random.choice(  a=[0, 1],  size=nrows,  p=[0.7, 0.3]  )
    df['cat2']= np.random.choice(  a=[4, 5, 6],  size=nrows,  p=[0.5, 0.3, 0.2]  )
    df['cat1']= np.where( df['cat1'] == 0,'low',np.where(df['cat1'] == 1, 'High','V.High'))
    return df


def pd_getdata(verbose=True):
    """data = test_get_data()
    df   = data['housing.csv']
    df.head(3)
    https://github.com/szrlee/Stock-Time-Series-Analysis/tree/master/data
    """
    import pandas as pd
    flist = [
        'https://raw.githubusercontent.com/samigamer1999/datasets/main/titanic.csv',
        'https://github.com/subhadipml/California-Housing-Price-Prediction/raw/master/housing.csv',
        'https://raw.githubusercontent.com/AlexAdvent/high_charts/main/data/stock_data.csv',
        'https://raw.githubusercontent.com/samigamer1999/datasets/main/cars.csv',
        'https://raw.githubusercontent.com/samigamer1999/datasets/main/sales.csv',
        'https://raw.githubusercontent.com/AlexAdvent/high_charts/main/data/weatherdata.csv'
    ]
    data = {}
    for url in flist :
       fname =  url.split("/")[-1]
       log( "\n", "\n", url, )
       df = pd.read_csv(url)
       data[fname] = df
       if verbose: log(df)
       # df.to_csv(fname , index=False)
    log(data.keys() )
    return data


def find_fuzzy(word:str, wlist:list, threshold=0.0):
  """ Find closest fuzzy string
        ll = dir(utilmy)
        log(ll)
        find_fuzzy('help create fun arguu', ll)
  """
  # import numpy as np
  from difflib import SequenceMatcher as SM
  scores = [ SM(None, str(word), str(s2) ).ratio() for s2 in wlist  ]
  #log(scores)
  # imax = np.argmax(scores)
  imax = max(range(len(scores)), key=scores.__getitem__)

  if scores[imax] > threshold :
      most_similar = wlist[imax]
      return most_similar
  else :
      raise Exception( f'Not exist {word}  ; {wlist} ' )



########################################################################################
class toFileSafe(object):
   def __init__(self,fpath):
      """ Thread Safe file writer Class
      Docs::
        tofile = toFileSafe('mylog.log')
        tofile.w("msg")
      """
      import logging
      logger = logging.getLogger('logsafe')
      logger.setLevel(logging.INFO)
      ch = logging.FileHandler(fpath)
      ch.setFormatter(logging.Formatter('%(message)s'))
      logger.addHandler(ch)
      self.logger = logger

   def write(self, *s):
        """ toFileSafe:write
        Args:
            msg:
        Returns:
        """
        msg = " ".join([ str(si) for si in s ])
        self.logger.info( msg)

   def log(self, *s):
        """ toFileSafe:log
        """
        msg = " ".join([ str(si) for si in s ])
        self.logger.info( msg)

   def w(self, *s):
        """ toFileSafe:w
        Args:
            msg:
        Returns:
        """
        msg = " ".join([ str(si) for si in s ])
        self.logger.info( msg)



class Index0(object):
    """ Class Maintain global index,
    Docs::
        file_name = f"{dtmp}/test_file_{int(time.time())}.txt"
        index = m.Index0(file_name, min_chars=8)
        ### 2 save some data
        data   = [ "testestest", 'duplicate', '5char', '### comment line, so skipped',]
        output = [ 'testestest', 'duplicate',  ]
        index.save(data)
        assert set(index.read()) == set(output), f"{output} , {index.read()}"
    """
    def __init__(self, findex:str="ztmp_file.txt", min_chars=5):
        """ Index0:__init__
        Args:
            findex (function["arg_type"][i]) :
        Returns:

        """
        self.findex        = findex
        self.min_chars = min_chars
        log(os.path.dirname(self.findex))
        os.makedirs(os.path.dirname(self.findex), exist_ok=True)
        if not os.path.isfile(self.findex):
            with open(self.findex, mode='a') as fp:
                fp.write("")

    def read(self,):
        """ Index0:read
        Args:
            :
        Returns:

        """
        with open(self.findex, mode='r') as fp:
            flist = fp.readlines()

        if len(flist) < 1 : return []
        flist2 = []
        for t  in flist :
            if len(t) >= self.min_chars and t[0] != "#"  :
              flist2.append( t.strip() )
        return flist2

    def save(self, flist:list):
        """ Index0:save
        Args:
            flist (function["arg_type"][i]) :
        Returns:

        """
        if len(flist) < 1 : return True
        ss = ""
        for fi in flist :
          ss = ss + str(fi) + "\n"
        # log(ss)
        with open(self.findex, mode='a') as fp:
            fp.write(ss )
        return True



##########################################################################################
def create_unique_tag()->str:
    return str(int(time.time()))


def hash_mmh32(xstr:str)->int:
    return mmh3.hash(str(xstr), signed=False)


def hash_mmh64(xstr:str)->int:
    return mmh3.hash64(str(xstr), signed=False)[0]


def hashid_toint(xstr):
    ### 2 ways encoding str to int
    import hashids
    return hashids.decode( str(xstr))


def hashid_tostr(xint):
    import hashids
    return hashids.encode( xint )



########################################################################################
def git_repo_root():
    """function git_repo_root
    Args:
    Returns:

    """
    try :
      cmd = "git rev-parse --show-toplevel"
      mout, merr = os_system(cmd)
      path = mout.split("\n")[0]
      if len(path) < 1:  return None
    except : return None
    return path


def git_current_hash(mode='full'):
    """function git_current_hash
    Args:
        mode:
    Returns:

    """
    import subprocess
    label = None
    try:
        # label = subprocess.check_output(["git", "describe", "--always"]).strip();
        label = subprocess.check_output([ 'git', 'rev-parse', 'HEAD' ]).strip()
        label = label.decode('utf-8')
    except Exception as e:
        log('Error get git hash')
        label=  None
    return label


def direpo(show=0):
    """ Root folder of the repo in Unix / format
    """
    dir_repo1 = os.path.dirname( os.path.dirname(os.path.abspath(__file__))).replace("\\","/") + "/"

    if show>0 :
        log(dir_repo1)
    return dir_repo1


def dirpackage(show=0):
    """ dirname of src/  folder
    """
    dir_repo1 = os.path.dirname(os.path.abspath(__file__)).replace("\\","/") + "/"

    if show>0 :
        log(dir_repo1)
    return dir_repo1


def dir_testinfo(tag="", verbose=1, ):
    """ Test infos:  return dir_repo, dir_tmp
    Docs::

        https://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
    """
    log("\n---------------------------------------------------------------------")
    drepo = direpo()
    dtmp  = os_get_dirtmp()
    assert os.path.exists(dtmp), f"Directory not found {dtmp}"

    import inspect
    fun_name = inspect.stack()[1].function
    if verbose>0 :
        print( inspect.stack()[1].filename,"::", fun_name,)

    dtmp  = dtmp + f"/{tag}/"  if len(tag)  > 0  else dtmp + f"/{fun_name}/"
    os_makedirs(dtmp)

    log('repo: ', drepo)
    log('tmp_: ', dtmp)
    log("\n")
    return drepo, dtmp


def os_get_dirtmp(subdir=None, return_path=False):
    """ return dir temp for testing,...
    """
    import tempfile
    from pathlib import Path
    dirtmp = tempfile.gettempdir().replace("\\", "/")
    dirtmp = dirtmp + f"/{subdir}/" if subdir is not None else dirtmp
    os.makedirs(dirtmp, exist_ok=True)
    return Path(dirtmp) if return_path  else dirtmp



############## Database Class #########################################################
def os_path_size(folder=None):
    """
       Get the size of a folder in bytes
    """
    import os
    if folder is None:
        folder = os.getcwd()
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def db_load_dict(df, colkey, colval, verbose=True)->Dict:
    ### load Pandas dataframe and convert into dict   colkey --> colval
    if isinstance(df, str):
       dirin = df
       log('loading', df)
       df = pd_read_file(dirin, cols= [colkey, colval ], n_pool=3, verbose=True)
    
    df = df.drop_duplicates(colkey)    
    df = df.set_index(colkey)
    df = df[[ colval ]].to_dict()
    df = df[colval] ### dict
    if verbose: log('Dict Loaded', len(df))
    return df
    

def dict_flatten(d: Dict[str, Any],/,*,recursive: bool = True,
    join_fn: Callable[[Sequence[str]], str] = ".".join,
) -> Dict[str, Any]:
    r"""Flatten dictionaries recursively."""
    result: dict[str, Any] = {}
    for key, item in d.items():
        if isinstance(item, dict) and recursive:
            subdict = dict_flatten(item, recursive=True, join_fn=join_fn)
            for subkey, subitem in subdict.items():
                result[join_fn((key, subkey))] = subitem
        else:
            result[key] = item
    return result


def dict_unflatten(d: Dict[str, Any],/,*, recursive: bool = True,
    split_fn: Callable[[str], Sequence[str]] = lambda s: s.split(".", maxsplit=1),
) -> Dict[str, Any]:
    r"""Unflatten dictionaries recursively."""
    result = {}
    for key, item in d.items():
        split = split_fn(key)
        result.setdefault(split[0], {})
        if len(split) > 1 and recursive:
            assert len(split) == 2
            subdict = dict_unflatten(
                {split[1]: item}, recursive=recursive, split_fn=split_fn
            )
            result[split[0]] |= subdict
        else:
            result[split[0]] = item
    return result



def dict_merge_into(dref:Dict, d2:Dict)->Dict:
    """ Merge d2 into dref, preserving original dref values if not exist in d2

    """
    import copy
    def merge_d2_into_d1(d1, d2):
        for key, value in d2.items():
            if isinstance(value, dict):
                if key in d1 and isinstance(d1[key], dict):
                    # Recursively merge the value with the value of d1
                    merge_d2_into_d1(d1[key], value)
                else:
                    d1[key] = value  ##### Overwrite existing key
            elif key not in d1:
                d1[key] = value

        return d1


    dnew = merge_d2_into_d1( copy.deepcopy(dref), d2)
    return dnew


########################################################################################
def code_break():
    """ Break the code running and start local interpreter for debugging
    """
    import pdb 
    pdb.set_trace()

           

########################################################################################
if __name__ == "__main__":
    fire.Fire()


