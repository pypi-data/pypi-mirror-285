# coding=utf-8
"""# Parallel utilities
Doc::

  
"""
import itertools, time, multiprocessing,  pickle, gc, os
from typing import Callable, Tuple, Union, Optional, Dict, List

from multiprocessing.pool import ThreadPool
from threading import Thread
import fire, pandas as pd, numpy as np


#################################################################################################
from src.utils.utilmy_log import log, log2


##################################################################################################
##################################################################################################
def pd_read_file(path_glob=r"*.pkl", ignore_index=True,  cols=None, verbose=False, nrows=-1, nfile=1000000, concat_sort=True,
                 n_pool=1, npool=None,
                 drop_duplicates=None, col_filter:str=None,  col_filter_vals:list=None, dtype_reduce=None,
                 fun_apply=None, use_ext=None,   **kw)->pd.DataFrame:
    """  Read file in parallel from disk : very Fast.
    Doc::

        path_glob: list of pattern, or sep by ";"
        :return:
    """
    import glob, gc,  pandas as pd, os

    if isinstance(path_glob, pd.DataFrame ) : return path_glob   ### Helpers

    n_pool = npool if isinstance(npool, int)  else n_pool ## alias
    def log(*s, **kw):  print(*s, flush=True, **kw)
    readers = {
            ".pkl"     : pd.read_pickle, ".parquet" : pd.read_parquet,
            ".tsv"     : pd.read_csv, ".csv"     : pd.read_csv, ".txt"     : pd.read_csv, ".zip"     : pd.read_csv,
            ".gzip"    : pd.read_csv, ".gz"      : pd.read_csv,
     }

    #### File
    if isinstance(path_glob, list):  path_glob = ";".join(path_glob)
    path_glob = path_glob.split(";")
    file_list = []
    for pi in path_glob :
        if "*" in pi : file_list.extend( sorted( glob.glob(pi) ) )
        else :         file_list.append( pi )

    file_list = sorted(list(set(file_list)))
    file_list = file_list[:nfile]
    if verbose: log(file_list)

    ### TODO : use with kewyword arguments ###############
    def fun_async(filei):
            ext  = os.path.splitext(filei)[1]
            if ext is None or ext == '': ext ='.parquet'

            pd_reader_obj = readers.get(ext, None)
            # dfi = pd_reader_obj(filei)
            try :
               dfi = pd_reader_obj(filei, **kw)
            except Exception as e:
               log('Error', filei, e)
               return pd.DataFrame()

            # if dtype_reduce is not None:    dfi = pd_dtype_reduce(dfi, int0 ='int32', float0 = 'float32')
            if col_filter is not None :       dfi = dfi[ dfi[col_filter].isin( col_filter_vals) ]
            if cols is not None :             dfi = dfi[cols]
            if nrows > 0        :             dfi = dfi.iloc[:nrows,:]
            if drop_duplicates is not None  : dfi = dfi.drop_duplicates(drop_duplicates, keep='last')
            if fun_apply is not None  :       dfi = dfi.apply(lambda  x : fun_apply(x), axis=1)
            return dfi



    ### Parallel run #################################
    import concurrent.futures
    dfall  = pd.DataFrame(columns=cols) if cols is not None else pd.DataFrame()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_pool) as executor:
        futures = []
        for i,fi in enumerate(file_list) :
            if verbose : log("file ", i, end=",")
            futures.append( executor.submit(fun_async, fi ))

        for future in concurrent.futures.as_completed(futures):
            try:
                dfi   = future.result()
                dfall = pd.concat( (dfall, dfi), ignore_index=ignore_index, sort= concat_sort)
                del dfi; gc.collect()
            except Exception as e:
                log('error', e)
    return dfall



def pd_read_file2(path_glob="*.pkl", ignore_index=True,  cols=None, verbose=False, nrows=-1, nfile=1000000, concat_sort=True, n_pool=1, npool=None,
                 drop_duplicates=None, col_filter:str=None,  col_filter_vals:list=None, dtype_reduce=None, fun_apply=None, use_ext=None,  **kw)->pd.DataFrame:
    """  Read file in parallel from disk, Support high number of files.
    Doc::

        path_glob: list of pattern, or sep by ";"
        return: pd.DataFrame
    """
    import glob, gc,  pandas as pd, os
    if isinstance(path_glob, pd.DataFrame ) : return path_glob   ### Helpers
    n_pool = npool if isinstance(npool, int)  else n_pool ## alias

    def log(*s, **kw):
        print(*s, flush=True, **kw)
    readers = {
            ".pkl"     : pd.read_pickle, ".parquet" : pd.read_parquet,
            ".tsv"     : pd.read_csv, ".csv"     : pd.read_csv, ".txt"     : pd.read_csv, ".zip"     : pd.read_csv,
            ".gzip"    : pd.read_csv, ".gz"      : pd.read_csv,
     }
    from multiprocessing.pool import ThreadPool

    #### File
    if isinstance(path_glob, list):  path_glob = ";".join(path_glob)
    path_glob  = path_glob.split(";")
    file_list = []
    for pi in path_glob :
        if "*" in pi :
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
    pd_reader_obj2 = None

    def fun_async(filei):
        ext  = os.path.splitext(filei)[1]
        if ext is None or ext == '': ext ='.parquet'

        pd_reader_obj = readers.get(ext, None)
        try :
          dfi = pd_reader_obj(filei)
        except Exception as e :
          log(e)

        # if dtype_reduce is not None:    dfi = pd_dtype_reduce(dfi, int0 ='int32', float0 = 'float32')
        if col_filter is not None :       dfi = dfi[ dfi[col_filter].isin(col_filter_vals) ]
        if cols is not None :             dfi = dfi[cols]
        if nrows > 0        :             dfi = dfi.iloc[:nrows,:]
        if drop_duplicates is not None  : dfi = dfi.drop_duplicates(drop_duplicates)
        if fun_apply is not None  :       dfi = dfi.apply(lambda  x : fun_apply(x), axis=1)
        return dfi

    pool   = ThreadPool(processes=n_pool)
    dfall  = pd.DataFrame(columns=cols) if cols is not None else pd.DataFrame()
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
                  dfall = pd.concat( (dfall, dfi), ignore_index=ignore_index, sort= concat_sort)
                  #log("Len", n_pool*j + i, len(dfall))
                  del dfi; gc.collect()
            except Exception as e:
                log('error', filei, e)


    pool.close() ; pool.join() ;  pool = None
    if m_job>0 and verbose : log(n_file, j * n_file//n_pool )
    return dfall




############################################################################################################
def pd_groupby_parallel2(df, colsgroup=None, fun_apply=None,
                        npool: int = 1, **kw,
                        )->pd.DataFrame:
    """Performs a Pandas groupby operation in parallel, using multi-processing
    Doc::

        Example usage:
            df = pd.DataFrame({'A': [0, 1], 'B': [100, 200]})
            df.groupby('A').apply( lambda dfi: fun_apply(dfi))

    """
    import pandas as pd
    from functools import partial

    groupby_df = df.groupby(colsgroup)

    start = time.time()
    npool = int(multiprocessing.cpu_count()) - 1
    log("\nUsing {} CPUs in parallel...".format(npool))
    with multiprocessing.Pool(npool) as pool:
        queue = multiprocessing.Manager().Queue()
        result = pool.starmap_async(fun_apply, [(group, name) for name, group in groupby_df])
        cycler = itertools.cycle('\|/―')
        while not result.ready():
            log("Percent complete: {:.0%} {}".format(queue.qsize() / len(groupby_df), next(cycler)))
            time.sleep(0.4)
        got = result.get()
    # log("\nProcessed {} rows in {:.1f}s".format(len(groupby_df), time.time() - start))
    return pd.concat(got)


def pd_groupby_parallel(df, colsgroup=None, fun_apply=None, n_pool=4, npool=None)->pd.DataFrame:
    """Use of multi-thread on group by apply when order is not important.
    Doc::

        df  = pd_random(1*10**5, ncols=3)

        def test_fun_sum_inv(group, name=None):         # Inverse cumulative sum
            group["inv_sum"] = group.iloc[::-1]["1"].cumsum()[::-1].shift(-1).fillna(0)
            return group

        colsgroup = ['0']
        df1 = df.groupby(colsgroup).apply(lambda dfi : test_fun_sum_inv(dfi ) )

        from utils.utilmy_base import parallel as par
        df2 = par.pd_groupby_parallel(df, colsgroup, fun_apply= test_fun_sum_inv, npool=4 )

    """
    n_pool = npool if isinstance(npool, int)  else n_pool ## alias
    import pandas as pd, concurrent.futures

    dfGrouped = df.groupby(colsgroup)

    with concurrent.futures.ThreadPoolExecutor(max_workers=npool) as executor:
        futures = []
        for name, group in dfGrouped:
            futures.append(executor.submit(fun_apply, group))

        del dfGrouped; gc.collect()

        df_out = pd.DataFrame()
        for future in concurrent.futures.as_completed(futures):
            dfr    = future.result()
            df_out = pd.concat(( df_out, dfr ))
            del dfr; gc.collect()

    return df_out



def pd_apply_parallel(df, fun_apply=None, npool=5, verbose=True )->pd.DataFrame:
    """ Pandas parallel apply, using multi-thread
    Doc::

        df  = pd_random(1*10**5, ncols=3)
        def test_sum(x):
            return  x['0'] + x['1']


        from utils.utilmy_base import parallel as par
        df['s1'] = pd_apply_parallel(df, fun_apply= test_sum, npool=7 )   ### Failed due to groupby part

    """
    import pandas as pd, numpy as np, time, gc

    def f2(df):
        return df.apply(lambda x : fun_apply(x), axis=1)

    if npool == 1 : return f2(df)

    #### Pool execute ###################################
    import concurrent.futures
    size = int(len(df) // npool)

    with concurrent.futures.ThreadPoolExecutor(max_workers=npool) as executor:
        futures = []
        for i in range(npool):
            i2  = 3*(i + 2) if i == npool - 1 else i + 1
            dfi = df.iloc[i*size:(i2*size), :]
            futures.append( executor.submit(f2, dfi,) )
            if verbose: log('start', i, dfi.shape)
            del dfi

        dfall = None
        for future in concurrent.futures.as_completed(futures):
            dfi = future.result()
            dfall = pd.concat((dfall, dfi)) if dfall is not None else dfi
            del dfi
            print(i, 'done' , end="," )

    return dfall


############################################################################################################
def multiproc_run(fun_async, input_list: list, n_pool=5, start_delay=0.1, input_fixed:dict=None, npool=None,  verbose=True, **kw):
    """  Run a function into mutiprocessing
    Doc::

        def test_fun_sum2(list_vars, const=1, const2=1):
            print( list_vars )
            si = 0
            for xi in list_vars :
                print(xi)
                si = si + xi if isinstance(xi, int) else si + sum(xi)
            return si

        input_list  = [ [1,1,], [2,2, ], [3,3, ], [4,4,], [5,5, ], [6,6, ], [7,7, ],  ]
        input_fixed = {'const': 50, 'const2': i}

        from utils.utilmy_base import parallel as par
        res = par.multiproc_run(test_fun_sum2, input_list= input_list, input_fixed= input_fixed, n_pool= 3 )
        print(  res,  )



    """
    import time, functools
    n_pool = npool if isinstance(npool, int)  else n_pool ## alias
    #### Input xi #######################################
    #if not isinstance(input_list[0], list ) and not isinstance(input_list[0], tuple ) :
    #     input_list = [  (t,) for t in input_list]  ## Must be a list of list

    if len(input_list) < 1 : return []

    if input_fixed is not None:  #### Fixed keywword variable
        fun_async = functools.partial(fun_async, **input_fixed)

    xi_list = [[] for t in range(n_pool)]
    for i, xi in enumerate(input_list):
        jj = i % n_pool
        xi_list[jj].append( xi )  ### xi is already a tuple

    if verbose:
        for j in range(len(xi_list)):
            log('proc ', j, len(xi_list[j]))
        # time.sleep(6)

    #### Pool execute ###############################################
    import multiprocessing as mp
    pool = mp.Pool(processes=n_pool)
    # pool     = mp.pool.ThreadPool(processes=n_pool)
    job_list = []
    for i in range(n_pool):
        time.sleep(start_delay)
        log('starts', i)
        job_list.append(pool.apply_async(fun_async, (xi_list[i],) ))
        if verbose: log(i, xi_list[i])

    res_list = []
    for i in range(len(job_list)):
        res_list.append(job_list[i].get())
        log(i, 'job finished')

    pool.close(); pool.join(); pool = None
    log('n_processed', len(res_list))
    return res_list


def multithread_run(fun_async, input_list: list, n_pool=5, start_delay=0.1, verbose=True, input_fixed:dict=None, npool=None, **kw):
    """  Run Multi-thread fun_async on input_list.
    Doc::

        def test_fun(list_vars, const=1, const2=1):
            print(f'Var: {list_vars[0]}')
            print('Fixed Const: ', const)
            return f"{const*const2} {str(list_vars[0])}"

        input_arg   = [ ( [1,2, "Hello"], [2,4, "World"], [3,4, "Thread3"], [4,5, "Thread4"], [5,2, "Thread5"], ),    ]
        input_fixed = {'const': 50, 'const2': i}

        from utils.utilmy_base import parallel as par
        res = par.multithread_run(test_fun, input_arg, n_pool=3, input_fixed=input_fixed)
        print(res)


    """
    import time, functools
    n_pool = npool if isinstance(npool, int)  else n_pool ## alias

    #### Input xi #######################################
    #if not isinstance(input_list[0], list ) and not isinstance(input_list[0], tuple ) :
    #     input_list = [  (t,) for t in input_list]  ## Must be a list of lis
    if len(input_list) < 1 : return []

    if input_fixed is not None:
        fun_async = functools.partial(fun_async, **input_fixed)

    #### Input xi #######################################
    xi_list = [[] for t in range(n_pool)]
    for i, xi in enumerate(input_list):
        jj = i % n_pool
        xi_list[jj].append( xi )  ### xi is already a tuple

    if verbose:
        for j in range(len(xi_list)):
            log('thread ', j, len(xi_list[j]))
        # time.sleep(6)

    #### Pool execute ###################################
    import multiprocessing as mp
    # pool     = multiprocessing.Pool(processes=3)
    pool = mp.pool.ThreadPool(processes=n_pool)
    job_list = []
    for i in range(n_pool):
        time.sleep(start_delay)
        log('starts', i)
        job_list.append(pool.apply_async(fun_async, (xi_list[i],) ))
        if verbose: log(i, xi_list[i])

    res_list = []
    for i in range(len(job_list)):
        res_list.append(job_list[i].get())
        log(i, 'job finished')

    pool.close(); pool.join(); pool = None
    log('n_processed', len(res_list))
    return res_list


def multiproc_tochunk(flist:list, npool=2 ):
    """ Create chunk of a list for mutlti-processing.
        1 processor = 1 chunk  --> list of arg values.
    Doc::

       returns list of list

    """
    ll = []
    chunk = len(flist) // npool
    for i in range( npool ) :
         i2 = i+1 if i < npool-1 else 3*(i+1)
         ll.append( flist[i*chunk:i2*chunk] )
    log(len(ll), str(ll)[:100])
    return ll



def multithread_run_list(**kwargs):
    """ Creating n number of threads.
    Docs::

        1 thread per function,    starting them and waiting for their subsequent completion
        os_multithread(function1=(test_print, ("some text",)),
                            function2=(test_print, ("bbbbb",)),
                            function3=(test_print, ("ccccc",)))
    """

    class ThreadWithResult(Thread):
        def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
            def function():
                self.result = target(*args, **kwargs)

            super().__init__(group=group, target=function, name=name, daemon=daemon)

    list_of_threads = []
    for thread in kwargs.values():
        # print(thread)
        t = ThreadWithResult(target=thread[0], args=thread[1])
        list_of_threads.append(t)

    for thread in list_of_threads:
        thread.start()

    results = []
    for thread, keys in zip(list_of_threads, kwargs.keys()):
        thread.join()
        results.append((keys, thread.result))

    return results





############################################################################################################
if __name__ == '__main__':
    fire.Fire()








