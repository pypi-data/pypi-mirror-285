""" Entries for common utilities
Docs::

"""

import datetime
import os
import re
import subprocess
import uuid
from multiprocessing.pool import ThreadPool
from typing import Any, Callable, Dict, Optional, Sequence, Union

import mmh3

from .util_log import log, logw


def uniqueid_create() -> str:
    return str(uuid.uuid4())


##########################################################################################
def to_float(xstr: str, default: float = -1.0) -> float:
    try:
        return float(xstr)
    except Exception as e:
        return default


def str_sanitize_list(xstr: str, sep=",") -> str:
    """Safe String"""
    slist = xstr.split(sep)
    sall = ""
    for si in slist:
        s2 = str_sanitize(si)
        sall = sall + "'" + s2 + f"'{sep}"
    return sall[:-1]


def str_sanitize(xstr: str, regex_check="[^a-zA-Z0-9]") -> str:
    """Safe String"""
    sanitized_string = re.sub(regex_check, "", xstr)
    if len(xstr) != len(sanitized_string):
        logw(f"sql_sanitized: remove char:  {xstr}")
    return sanitized_string


##########################################################################################
def os_makedirs(dir_or_file: str):
    """function os_makedirs
    Docs::
        Args:
            dir_or_file:
        Returns:
            None
    """
    if os.path.isfile(dir_or_file) or "." in dir_or_file.split("/")[-1]:
        os.makedirs(os.path.dirname(os.path.abspath(dir_or_file)), exist_ok=True)
        f = open(dir_or_file, "w")
        f.close()
    else:
        os.makedirs(os.path.abspath(dir_or_file), exist_ok=True)


### Generic Date function   #####################################################
def date_now(
    datenow: Optional[Union[str, int, float, datetime.datetime]] = "",
    fmt="%Y%m%d",
    add_days=0,
    add_mins=0,
    add_hours=0,
    add_months=0,
    add_weeks=0,
    timezone="Asia/Tokyo",
    fmt_input="%Y-%m-%d",
    force_dayofmonth=-1,  ###  01 first of month
    force_dayofweek=-1,
    force_hourofday=-1,
    force_minofhour=-1,
    returnval="str,int,datetime/unix",
):
    """One liner for date Formatter
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

    sdt = str(datenow)

    if isinstance(datenow, datetime.datetime):
        now_utc = datenow

    elif (
        isinstance(datenow, float) or isinstance(datenow, int)
    ) and datenow > 1600100100:  ### Unix time stamp
        ## unix seconds in UTC
        # fromtimestamp give you date and time in local time
        # utcfromtimestamp gives you date and time in UTC.
        #  int(time.time()) - date_now( int(time.time()), returnval='unix', timezone='utc') == 0
        now_utc = datetime.datetime.fromtimestamp(datenow)  ##

    elif len(sdt) > 7:  ## date in string
        now_utc = datetime.datetime.strptime(sdt, fmt_input)

    else:
        now_utc = datetime.datetime.now(tzone("UTC"))  # Current time in UTC

    # now_new = now_utc.astimezone(tzone(timezone))  if timezone != 'utc' else  now_utc.astimezone(tzone('UTC'))
    now_new = (
        now_utc.astimezone(tzone("UTC"))
        if timezone in {"utc", "UTC"}
        else now_utc.astimezone(tzone(timezone))
    )

    ####  Add months
    now_new = now_new + datetime.timedelta(
        days=add_days + 7 * add_weeks,
        hours=add_hours,
        minutes=add_mins,
    )
    if add_months != 0:
        from dateutil.relativedelta import relativedelta

        now_new = now_new + relativedelta(months=add_months)

    #### Force dates
    if force_dayofmonth > 0:
        now_new = now_new.replace(day=force_dayofmonth)

    if force_dayofweek > 0:
        actual_day = now_new.weekday()
        days_of_difference = force_dayofweek - actual_day
        now_new = now_new + datetime.timedelta(days=days_of_difference)

    if force_hourofday > 0:
        now_new = now_new.replace(hour=force_hourofday)

    if force_minofhour > 0:
        now_new = now_new.replace(minute=force_minofhour)

    if returnval == "datetime":
        return now_new  ### datetime
    elif returnval == "int":
        return int(now_new.strftime(fmt))
    elif returnval == "unix":
        return datetime.datetime.timestamp(now_new)  # time.mktime(now_new.timetuple())
    else:
        return now_new.strftime(fmt)


##########################################################################################
def hash_mmh32(xstr: str) -> int:
    # pylint: disable=E1136
    return mmh3.hash(str(xstr), signed=False)


def hash_mmh64(xstr: str) -> int:
    # pylint: disable=E1136
    return mmh3.hash64(str(xstr), signed=False)[0]


########################################################################################
def os_system(cmd: str, doprint=False):
    """Get stdout, stderr from Command Line into  a string varables  mout, merr
    Docs::
         Args:
             cmd: Command to run subprocess
             doprint=False: int
         Returns:
             out_txt, err_txt
    """
    try:
        # pylint: disable=W1510
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        mout, merr = p.stdout.decode("utf-8"), p.stderr.decode("utf-8")
        if doprint:
            l = mout if len(merr) < 1 else mout + "\n\nbash_error:\n" + merr
            log(l)

        return mout, merr
    except Exception as e:
        merr = f"Error {cmd}, {e}"
        log(merr)
        return None, merr


def git_repo_root():
    """function git_repo_root
    Args:
    Returns:

    """
    try:
        cmd = "git rev-parse --show-toplevel"
        mout, merr = os_system(cmd)
        path = mout.split("\n")[0]
        if len(path) < 1:
            return None
    except Exception as e:
        return None
    return path


def git_current_hash(mode="full"):
    """function git_current_hash
    Args:
        mode:
    Returns:

    """
    label = None
    try:
        # label = subprocess.check_output(["git", "describe", "--always"]).strip();
        label = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
        label = label.decode("utf-8")
    except Exception as e:
        log("Error get git hash")
        label = None
    return label


def direpo(show=0):
    """Root folder of the repo in Unix / format"""
    dir_repo1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/") + "/"

    if show > 0:
        log(dir_repo1)
    return dir_repo1


def dirpackage(show=0):
    """dirname of src/  folder"""
    dir_repo1 = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/"

    if show > 0:
        log(dir_repo1)
    return dir_repo1


def dir_testinfo(
    tag="",
    verbose=1,
):
    """Test infos:  return dir_repo, dir_tmp
    Docs::

        https://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python
    """
    log("\n---------------------------------------------------------------------")
    drepo = direpo()
    dtmp = os_get_dirtmp()
    assert os.path.exists(dtmp), f"Directory not found {dtmp}"

    import inspect

    fun_name = inspect.stack()[1].function
    if verbose > 0:
        print(
            inspect.stack()[1].filename,
            "::",
            fun_name,
        )

    dtmp = dtmp + f"/{tag}/" if len(tag) > 0 else dtmp + f"/{fun_name}/"
    os_makedirs(dtmp)

    log("repo: ", drepo)
    log("tmp_: ", dtmp)
    log("\n")
    return drepo, dtmp


def os_get_dirtmp(subdir=None, return_path=False):
    """return dir temp for testing,..."""
    import tempfile
    from pathlib import Path

    dirtmp = tempfile.gettempdir().replace("\\", "/")
    dirtmp = dirtmp + f"/{subdir}/" if subdir is not None else dirtmp
    os.makedirs(dirtmp, exist_ok=True)
    return Path(dirtmp) if return_path else dirtmp


############## Database Class #########################################################
def dict_flatten(
    d: Dict[str, Any],
    /,
    *,
    recursive: bool = True,
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


def dict_unflatten(
    d: Dict[str, Any],
    /,
    *,
    recursive: bool = True,
    split_fn: Callable[[str], Sequence[str]] = lambda s: s.split(".", maxsplit=1),
) -> Dict[str, Any]:
    r"""Unflatten dictionaries recursively."""
    result = {}
    for key, item in d.items():
        split = split_fn(key)
        result.setdefault(split[0], {})
        if len(split) > 1 and recursive:
            assert len(split) == 2
            subdict = dict_unflatten({split[1]: item}, recursive=recursive, split_fn=split_fn)
            result[split[0]] |= subdict
        else:
            result[split[0]] = item
    return result


############## Multithread async runner ################################################
def multithread_run(
    fun_async,
    input_list: list,
    n_pool=5,
    start_delay=0.1,
    verbose=True,
    input_fixed: dict = None,
    npool=None,
    **kw,
):
    import functools
    import time

    n_pool = npool if isinstance(npool, int) else n_pool  ## alias

    #### Input xi #######################################
    if len(input_list) < 1:
        return []

    if input_fixed is not None:
        fun_async = functools.partial(fun_async, **input_fixed)

    #### Input xi #######################################
    xi_list = [[] for t in range(n_pool)]
    for i, xi in enumerate(input_list):
        jj = i % n_pool
        xi_list[jj].append(xi)  ### xi is already a tuple

    if verbose:
        for j in range(len(xi_list)):
            log("thread ", j, len(xi_list[j]))
        # time.sleep(6)

    #### Pool execute ###################################
    import multiprocessing as mp

    # pool     = multiprocessing.Pool(processes=3)
    pool = mp.pool.ThreadPool(processes=n_pool)
    job_list = []
    for i in range(n_pool):
        time.sleep(start_delay)
        log("starts", i)
        job_list.append(pool.apply_async(fun_async, (xi_list[i],)))
        if verbose:
            log(i, xi_list[i])

    res_list = []
    for i in range(len(job_list)):
        res_list.append(job_list[i].get())
        log(i, "job finished")

    pool.close()
    pool.join()
    pool = None
    log("n_processed", len(res_list))
    return res_list


def multiproc_tochunk(flist: list, npool=2):
    ll = []
    chunk = len(flist) // npool
    for i in range(npool):
        i2 = i + 1 if i < npool - 1 else 3 * (i + 1)
        ll.append(flist[i * chunk : i2 * chunk])
    log(len(ll), str(ll)[:100])
    return ll
