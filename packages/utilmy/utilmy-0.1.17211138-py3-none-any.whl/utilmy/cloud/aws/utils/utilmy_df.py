""" utilities for dataframe
Docs::


"""
import os,sys,time, datetime, random,re, json
from typing import Any, Callable, Sequence, Dict, List, Union,Optional
import mmh3, fire, xxhash
import pandas as pd, numpy as np, polars as pl
from datetime import timedelta  #  Need timedelta for shifting dates

try :
  from .utilmy_parallel import (pd_read_file, pd_read_file2)
  from .utilmy_log import log,log2, logw,loge
  from .utilmy_base import (pd_to_dict, hash_int32, log_pd, to_int, json_load, json_save, glob_glob, os_rename, date_now)
except:
  from utilmy_parallel import (pd_read_file, pd_read_file2)
  from utilmy_log import log,log2, logw,loge
  from utilmy_base import (pd_to_dict, hash_int32, log_pd, to_int, json_load, json_save, glob_glob, os_rename, date_now)



pd_dataframe = Union[pd.DataFrame, pl.DataFrame]


##########################################################################################################
#### Tests ##############################
def test(): 
   # df = polars_random_date(dt_end='2023-03-01', ncat_col=2, nfloat_col=1)
   df = pd_random_date(dt_end='2023-03-01', ncat_col=2, nfloat_col=1)
   df.columns = [ 'ymd', 'hh',  'fe', 'qkey', 'n_clk', 'n_imp' ]  # updated to match with pandas test
   log(df)

   df = pl.DataFrame(df)  #  Convert to polars df
   dfres = polars_add_rolling_window_sum(df, colsgroupby=[ 'fe', 'qkey', 'hh' ], 
                                  colsum='n_clk', window=30, cfg=None, mode='train',
                                  window_shift=1, colnew='avg')

   print(dfres)
   return dfres


def pd_groupby_lenlist(df, colkey='qkey', colstr:str='fe', colnew=None)->pd.DataFrame:
    """
         Group the dataframe `df` by the column `colkey` 
         and calculate the length of the values in the column `colstr` for each group. 
    """
    colnew = 'n_' + colstr if colnew is None else colnew
    grouped_df = df.groupby(colkey).apply(lambda dfi :    len(dfi[colstr].values) ).reset_index(name=colnew)   
    df = df.merge(grouped_df[[ colkey, colnew  ]], on=colkey, how='left')
    return df




def pd_random_date(dt_end='2023-04-01', ncat_col=2, nfloat_col=2):
    """Generate a pandas DataFrame with random dates and columns.

    Parameters:
    - dt_end (str)    : end date for date range (default: '2023-04-01').
    - ncat_col (int)  : number of categorical columns to generate (default: 2).
    - nfloat_col (int): number of float columns to generate (default: 2).

    Returns:
    - df (pandas.DataFrame): generated DataFrame with random dates and columns.
    """  
    df = pd.DataFrame()
    df['dt'] = pd.date_range('2022-01-01', dt_end, freq='1H')  #  Changed start date to '2022-01-01' for more data, Otherwise df.sample() in line 23 will throw error.
    df['ymd']= df['dt'].apply(lambda x : x.year*10000 + x.month* 100 + x.day )
    df['hh'] = df['dt'].apply(lambda x  : x.hour)
    del df['dt']

    nrows = len(df)
    df[ f"fe"]   = np.random.randint(0, 50,  size= (nrows, 1))
    df[ f"qkey"] = np.random.randint(0, 10,   size= (nrows, 1))

    df[ f"n_clk"] = np.random.randint(0, 75,  size= (nrows, 1))
    df[ f"n_imp"] = np.random.randint(0, 100, size= (nrows, 1))

    ### Create Missing dates !
    df = df.sample(n=10000)
    df = df.sort_values(['ymd', 'hh'])

    return df


##########################################################################################################
def polars_add_rolling_window_sum(df:pd_dataframe, colsgroupby=None, colsum='n_clk', window=30,  window_shift=1, colnew='avg',
                                            cfg=None, mode='train', returnval='pandas')->pd_dataframe:
    """
    Add a rolling window sum feature to a DataFrame.

    Args:
        df (pd.DataFrame or pl.DataFrame): input DataFrame.
        colsgroupby (list)               : Columns to group by (default: ['fe', 'hh']).
        colsum (str)                     : Column name to sum (default: 'n_clk').
        window (int)                     : Size of rolling window (default: 30).
        cfg (None)                       : Configuration object (default: None).
        mode (str)                       : Mode of operation (default: 'train').
        window_shift (int)               : Shift of rolling window (default: 1).
        colnew (str)                     : New column name for rolling window sum (default: 'avg').

    Returns:
        pd.DataFrame: DataFrame with rolling window sum feature added.
    """
    from datetime import timedelta  #  Need timedelta for shifting dates
    colsgroupby = [  'fe', 'hh'] if colsgroupby is None else colsgroupby
    colsgroupby = [ci for ci in colsgroupby if ci not in {'ymd'}]

    if colnew in df.columns :
       log(f"{colnew} already exists, skipping")
       return df

    if isinstance(df, pd.DataFrame):
        df = pl.DataFrame(df)

    #  Converting 'ymd' to date type and sorting by (colsgroupby + ['ymd'])
    df = df.with_columns([
        pl.col('ymd').cast(pl.Utf8).str.to_datetime(format="%Y%m%d").dt.date()
    ]).sort(colsgroupby + ['ymd'])

    #  Aggregating to 30 calendar day sums: use actual days
    agg_df = df.groupby_dynamic(
        index_column="ymd", every="1d", period=f"{window}d", closed="left", by=colsgroupby, offset=f"-{window}d"
    ).agg([
        pl.col(colsum).sum().alias(colnew)
    ]).with_columns(
        pl.col('ymd') + timedelta(days=window - 1 + window_shift)
    )

    #  Join back to main df, fill nulls, type correction, and sorting.
    dfres_new = df.join( agg_df, on=colsgroupby + ['ymd'] , how='left'
    ).with_columns([
        pl.col(colnew).fill_null(0.0),
        pl.col('ymd').dt.strftime('%Y%m%d').cast(pl.Int64)
    ]).sort([ci for ci in colsgroupby if ci not in {'hh'}] +   [ 'hh', 'ymd'])

    #### return pandas dataframe
    if returnval == 'pandas':
        return dfres_new.to_pandas()
    return dfres_new



def polars_add_rolling_window_sum_mutiple(df, colkeys, window_list:List, shift=1, returnval='pandas'):
    """Applies rolling aggregation to a Polars DataFrame.
        Args:
            df (pl.DataFrame)      : input Polars DataFrame.
            colkeys (List[str])    : list of column keys to consider for aggregation.
            window_list (List[int]): list of window sizes for rolling aggregation.
            shift (int, optional)  : number of days to shift results. Defaults to 1.
            
        Returns:
            pd.DataFrame: resulting pandas DataFrame.
    """
    clist = [ ci for ci in df.columns if ci not in colkeys + ['ymd', 'hh']]  #  Exclude 'hh' as no need to take sum of hours
    clist = [ ci for ci in clist if df[ci].is_numeric()] #  filter out non numeric cols
    gkeys = [ ci for ci in colkeys if ci not in ['ymd'] ]

    #  Convert 'ymd' to datetime format
    df = df.with_columns([
        pl.col('ymd').cast(pl.Utf8).str.to_datetime(format="%Y%m%d").dt.date()
    ]).sort(gkeys + ['ymd'])  #  Should be sorted for 'groupby_dynamic' to work.

    prev_agg_df = None
    for window in window_list :
        #  Aggregate df
        agg_df = df.groupby_dynamic(
            index_column="ymd", every="1d", period=f"{window}d", closed="left", by=gkeys, offset=f"-{window}d"
        ).agg([
            pl.col(col).sum().alias(f"{col}_{window}D") for col in clist
        ]).with_columns(
            pl.col('ymd') + timedelta(days=window - 1 + shift)
        )

        if prev_agg_df is not None:
            #  Join to previous agg_df. Not merging to df directly as it would be slower
            agg_df = prev_agg_df.join( agg_df, on=gkeys + ['ymd'] , how='outer')

        prev_agg_df = agg_df

    #  Join back to agg_df.
    df = df.join(prev_agg_df, on=gkeys + ['ymd'] , how='left'
    ).with_columns(
        [pl.col(f"{col}_{window}D").fill_null(0.0) for col in clist for window in window_list]  #  Fill nulls
        + [pl.col('ymd').dt.strftime('%Y%m%d').cast(pl.Int64)]  #  'ymd' back to %Y%m%d format
    )

    #  Code inside try: catch:
    df = df.with_columns([
        (pl.col(f"n_clk_{window}D")/pl.col(f"n_imp_{window}D")).alias(f"ctr_{window}D") for window in window_list
        if (f"n_clk_{window}D" in df.columns) and (f"n_imp_{window}D" in df.columns)
    ])

    #### return pandas dataframe
    if returnval == 'pandas':
        return df.to_pandas()
    return df




###### In/ Out Polars ###################################################################################
def pl_read_file_s3(path_s3="s3://mybucket", suffix=None,npool=2, dataset=False,show=0, nrows=1000000000, session=None,
                    lower_level=0, upper_level=0,**kw):
    """ Read files into Polars:


    https://s3fs.readthedocs.io/en/latest/api.html#s3fs.core.S3FileSystem.glob
    """
    import polars as pl, pyarrow as pa
    import pyarrow.parquet as pq
    import s3fs
    from src.utils.utilmy_aws import aws_get_session


    session = aws_get_session()
    fs = s3fs.S3FileSystem(session=session)

    path_s3 = path_s3.replace("//", "/").replace("s3:/", "s3://")
    flist = fs.glob(path_s3)

    dfall= None
    for pathi in flist:
        if pathi.endswith(".parquet"):
            dataset = pq.ParquetDataset(pathi, filesystem=fs)
            dfi = pl.from_arrow(dataset.read())
            dfall = pl.concat((dfall, dfi)) if dfall is not None else dfi

    if show>0 :
        print(dfall)

    return dfall





def pa_read_file_s3(path_glob="tmp/mybucket/*.parquet",
                ignore_index=True,  cols=None, verbose=1, nrows=-1, nfile=1000000, concat_sort=True, n_pool=1, npool=None,
                 drop_duplicates=None, col_filter:str=None,  col_filter_vals:list=None,
                 dtype_reduce=None, fun_apply=None, use_ext=None,  returnval:str='polars',  **kw):
    """Read file in parallel from S3 or local file system.

    Docs::

        Args:
            path_glob (str)        : list of pattern, or sep by ";"
            ignore_index (bool)    :
            cols (list)            : list of columns to read
            verbose (bool)         :
            nrows (int)            : number of rows to read, read all if <=0
            nfile (int)            : number of files to read
            concat_sort (bool)     :
            n_pool (int)           :
            npool                  :
            drop_duplicates        : subset of columns to drop duplicates
            col_filter (str)       : column name to filter
            col_filter_vals (list) : list of values to filter
            dtype_reduce (bool)    : reduce dtype to save memory
            fun_apply (func)       : function to apply on dataframe
            use_ext                :
            returnval (str)        : return type, polars or pandas
            **kw                   :
        Returns:
            dfall (df)          : output dataframe
            
        Example:
            df = pa_read_file_s3(
                path_glob="tmp/mybucket/*.parquet", cols=['key', 'int0', 'flo0', 'str0'], nrows=300,
                drop_duplicates=['flo0', 'str0'], col_filter='int0', col_filter_vals=[1,2,3,4,5],
                dtype_reduce=True)

        # https://arrow.apache.org/docs/python/generated/pyarrow.fs.S3FileSystem.html                
    """
    import glob, gc, os, pyarrow as pa
    from multiprocessing.pool import ThreadPool
    import pyarrow.parquet as pq
    import pyarrow.dataset as ds



    if not isinstance(path_glob, str )  and not isinstance(path_glob, list ) : return path_glob   ### return Table or Dataframe

    n_pool  = npool if isinstance(npool, int)  else n_pool ## alias
    verbose = True if (isinstance(verbose, int) and verbose ==1)  or (verbose is True) else False

    def log(*s, **kw):
        print(*s, flush=True, **kw)


    #### Filesytem Open  ############################################
    if "s3:" in path_glob :
       from src.utils.utilmy_aws import aws_get_session
       import s3fs
       session = aws_get_session()
       fs      = s3fs.S3FileSystem(session=session)
    else:
       fs = pa.fs.LocalFileSystem()


    #### File name fetching #########################################
    if isinstance(path_glob, list):  path_glob = ";".join(path_glob)
    path_glob = path_glob.split(";")
    file_list = []
    for pi in path_glob :
        if "*" in pi :
          if "s3:" in pi:
            file_list.extend( sorted( fs.glob(pi) ) )
          else:
            file_list.extend( sorted( glob.glob(pi) ) )
        else :
          file_list.append( pi )

    file_list = sorted(list(set(file_list)))
    file_list = file_list[:nfile]
    n_file    = len(file_list)
    if verbose: log(file_list)


    #### Pool count  ###############################################
    if n_pool < 1 :  n_pool = 1
    if n_file <= 0:  m_job  = 0
    elif n_file <= 2:
       m_job  = n_file
       n_pool = 1
    else  :
       m_job  = 1 + n_file // n_pool  if n_file >= 3 else 1
    if verbose : log(n_file,  n_file // n_pool )


    ### TODO : use with kewyword arguments
    def fun_async(filej:str):
        ### Reading pattern
        ### https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Dataset.html#pyarrow.dataset.Dataset.scanner
        ###
        ext  = os.path.splitext(filej)[1]
        if ext is None or ext == '': ext ='.parquet'

        try :
           dfi = ds.dataset(filej, filesystem=fs)  ### format="parquet"
        except Exception as e :
           log(e)
           return  pa.Table.from_arrays([], [])


        scanner_args = {}
        if cols is not None : scanner_args['columns'] = cols
        if col_filter is not None :       scanner_args['filter'] = ds.field(col_filter).isin(col_filter_vals)
        dfi = dfi.scanner(**scanner_args).to_table()
        return dfi


    pool  = ThreadPool(processes=n_pool)
    dfall = None
    for j in range(0, m_job ) :
        if verbose : log("Pool", j, end=",")
        job_list = []
        for i in range(n_pool):
           if n_pool*j + i >= n_file  : break

           filei         = file_list[n_pool*j + i]
           job_list.append( pool.apply_async(fun_async, (filei, )))
           if verbose : log(j, filei)

        for i in range(n_pool):
            try :
                if i >= len(job_list): break
                dfi   = job_list[ i].get()
                dfall = pa.concat_tables( (dfall, dfi)) if dfall is not None else dfi
                ## #log("Len", n_pool*j + i, len(dfall))
                del dfi; gc.collect()
            except Exception as e:
                log('error', filei, e)


    pool.close() ; pool.join() ;  pool = None
    if m_job>0 and verbose : log(n_file, j * n_file//n_pool )

    # dfall = pl.from_arrow(dfall)
    # if drop_duplicates is not None  : dfall = dfall.unique(subset=drop_duplicates)
    # if fun_apply is not None  :       dfall = dfall.apply(fun_apply)
    # if nrows > 0        :             dfall = dfall.slice(0, nrows)
    #
    # if dtype_reduce:
    #    for col, dtype in dfall.schema.items():
    #       if dtype in [pl.Int16, pl.Int32, pl.Int64, pl.UInt16, pl.UInt32, pl.UInt64]:
    #          for downtype in [pl.UInt8, pl.Int8, pl.UInt16, pl.Int16, pl.UInt32, pl.Int32]:
    #             try:
    #                 dfall = dfall.with_columns([pl.col(col).cast(downtype)])
    #                 break
    #             except:
    #                 pass
    #       elif dtype in [pl.Float64, pl.Decimal]:
    #          for downtype in [pl.Float32, pl.Float64]:
    #             try:
    #                 dfall = dfall.with_columns([pl.col(col).cast(downtype)])
    #                 break
    #             except:
    #                 pass


    if returnval == 'pandas':
        dfall = dfall.to_pandas()

    elif returnval == 'polars':
        import polars as pl
        dfall = pl.from_arrow(dfall)

    return dfall




def pd_create_df(dirout:str):
    nmin = 2
    nmax=5000
    # df = pd_create_random(nmax=5000000)
    df = pd.DataFrame()
    df['key'] = np.arange(0, nmax)
    for i in range(0, nmin):
        df[ f'int{i}'] = np.random.randint(0, 100,size=(nmax, ))
        df[ f'flo{i}'] = np.random.rand(1, nmax)[0]
        df[ f'str{i}'] =  [ ",".join([ str(t) for t in np.random.randint(10000000,999999999,size=(500, )) ] )  for k in range(0,nmax) ]
        print(df.head)
    df.to_parquet(dirout)


def pd_compare(*dfs):
    """function pd_compare.
        Compare dataframes with all hashable columns.

    Docs::

        Args:
            *args : list of dataframes
        Returns:
            bool : True if all dataframes are identical
    """
    if len(dfs) == 1 : return True

    # Check if all dataframes have the same columns
    cols = set(dfs[0].columns)
    if any([cols != set(df.columns) for df in dfs[1:]]):
        return False

    # Check if all dataframes have the same shape
    shape = dfs[0].shape
    if any([shape != df.shape for df in dfs[1:]]):
        return False

    # Reset indices, column order and sort rows before comparing
    cols = list(cols)
    dfs = [df[cols].sort_values(cols).reset_index(drop=True) for df in dfs]

    # Check if values are the same
    df0 = dfs[0]
    return all([all([(df0[col] == df[col]).all() for col in cols]) for df in dfs[1:]])



##########################################################################################
def pd_del(df, cols):
   for ci in cols: 
      try:
        del df[ci]
      except Exception as e:
         pass





def test_pa_read_file():
   import os
   os.makedirs("tmp/mybucket", exist_ok=True)
   pd_create_df('tmp/mybucket/a.parquet')

   df = pd.read_parquet('tmp/mybucket/a.parquet', columns=['key', 'int0', 'flo0', 'str0'])
   df = df[df['int0'].isin([1,2,3,4,5])]
   df = df.drop_duplicates(['flo0', 'str0'])
   df = df.iloc[:300,:]

   df_out = pa_read_file_s3(
      path_glob="tmp/mybucket/*.parquet", cols=['key', 'int0', 'flo0', 'str0'], nrows=300,
      drop_duplicates=['flo0', 'str0'], col_filter='int0', col_filter_vals=[1,2,3,4,5],
      returnval='pandas')

   assert pd_compare(df, df_out), "Incorrect output from pl_groupby_join"




########################################################################################
if __name__ == "__main__":
    fire.Fire()


