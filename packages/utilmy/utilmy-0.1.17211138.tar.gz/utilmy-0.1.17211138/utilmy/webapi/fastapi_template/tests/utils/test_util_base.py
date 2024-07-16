# -*- coding: utf-8 -*-
""" Entries for common utilities
Docs::
"""

from src.utils.util_base import *
from src.utils.util_log import log

###################################################################################################


###################################################################################################
###### Test #######################################################################################
def to_file(txt: str, fpath: str, mode="a"):
    """Write argument "s" in a file.

    Docs::

        Args:
            s (string):     string to write in file.
            filep (string): Path of file to write.
    """
    os_makedirs(fpath)  ### create folder
    txt = str(txt)
    try:
        with open(fpath, mode=mode) as fp:
            fp.write(txt)
        return True
    except Exception as e:
        time.sleep(5)
        with open(fpath, mode=mode) as fp:
            fp.write(txt)
        return True


#################################################################################################
def test_str_sanitize():
    # Test with a string that contains special characters
    assert str_sanitize("abc$%^123") == "abc123"

    # Test with a string that doesn't contain special characters
    assert str_sanitize("abc123") == "abc123"


def test_str_sanitize_list():
    # Test with a list of strings that contain special characters
    assert str_sanitize_list("abc$%^123,def&*()456") == "'abc123','def456'"

    # Test with a list of strings that don't contain special characters
    assert str_sanitize_list("abc123,def456") == "'abc123','def456'"


def test_str():
    x0 = "'a'b'c"
    x1 = str_sanitize(x0, regex_check="[^a-zA-Z0-9]")
    assert x1 == "abc"

    x0 = "'a,'b',c"
    x1 = str_sanitize_list(x0)
    assert x1 == "'a','b','c'", f"{x1}"


def test_datenow():
    import time

    log("\n####", date_now)
    assert date_now(timezone="Asia/Tokyo")  # -->  "20200519"   ## Today date in YYYMMDD
    assert date_now(timezone="Asia/Tokyo", fmt="%Y-%m-%d")  # -->  "2020-05-19"

    x = date_now("2020-12-10", fmt="%Y%m%d", add_days=-5, returnval="int")
    assert not log(x) and x == 20201205, x  # -->  20201205

    x = date_now(20211005, fmt_input="%Y%m%d", returnval="unix")
    assert not log(x) and int(x) > 1603424400, x  # -->  1634324632848

    x = date_now(20211005, fmt="%Y-%m-%d", fmt_input="%Y%m%d", returnval="str")  # -->  '2021-10-05'
    assert not log(x) and x == "2021-10-05", x  # -->  1634324632848

    assert (
        date_now("2020-05-09", add_months=-2, fmt="%Y-%m-%d") == "2020-03-09"
    )  # Test adding -2 months
    assert date_now(
        "2012-12-06 12:00:00", returnval="datetime", add_mins=20, fmt_input="%Y-%m-%d %H:%M:%S"
    ) == date_now(
        "2012-12-06 12:20:00", returnval="datetime", fmt_input="%Y-%m-%d %H:%M:%S"
    )  # Test adding 20 minutes
    assert date_now(
        "2012-12-06 12:00:00", returnval="datetime", add_hours=11, fmt_input="%Y-%m-%d %H:%M:%S"
    ) == date_now(
        "2012-12-06 23:00:00", returnval="datetime", fmt_input="%Y-%m-%d %H:%M:%S"
    )  # Test adding 11 hours
    assert date_now(
        "2012-12-06 12:00:00", returnval="datetime", add_days=5, fmt_input="%Y-%m-%d %H:%M:%S"
    ) == date_now(
        "2012-12-11 12:00:00", returnval="datetime", fmt_input="%Y-%m-%d %H:%M:%S"
    )  # Test adding 5 days
    # assert date_now('2012-12-06 19:00:00',returnval='datetime',force_dayofweek=0,fmt_input="%Y-%m-%d %H:%M:%S") == date_now('2012-12-03 19:00:00',returnval='datetime',fmt_input="%Y-%m-%d %H:%M:%S") #Test forcing day 3 of week

    x = date_now(time.time(), returnval="datetime")
    x = date_now(time.time(), returnval="datetime", timezone="utc")
    x = date_now(int(time.time()), returnval="datetime")

    log("check unix epoch timezone time.time() ")
    assert (
        abs(int(time.time()) - date_now(int(time.time()), returnval="unix", timezone="utc")) < 1e-2
    ), ""

    ts = time.time()
    datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    dtu = datetime.datetime.fromtimestamp(ts)  # .strftime('%Y-%m-%d %H:%M:%S')
    datetime.datetime.timestamp(dtu)

    #### Minhour
    dstr = date_now(force_minofhour=59, add_hours=1, fmt="%Y%m%d-%H:%M")
    dunix = date_now(
        force_minofhour=59, add_hours=1, fmt="%Y%m%d-%H:%M", returnval="unix"
    )  ##  1674935977.681208
    dstr2 = date_now(
        dunix,
        fmt="%Y%m%d-%H:%M",
    )
    assert dstr == dstr2


def test1():

    drepo, dtmp = dir_testinfo()

    ###################################################################
    log("\n##### git_repo_root  ", git_repo_root())
    assert not git_repo_root() == None, "err git repo"

    log("\n##### git_current_hash  ", git_current_hash())
    assert not git_current_hash() == None, "err git hash"

    ####################################################################

    ####################################################################
    log("\n####", os_get_dirtmp)
    assert os_get_dirtmp(), "FAILED -> os_get_dirtmp"
    assert os_get_dirtmp(subdir="test"), "FAILED -> os_get_dirtmp"
    assert os_get_dirtmp(subdir="test", return_path=True), "FAILED -> os_get_dirtmp"


def test_hash_mmh32():
    # Test with a string
    assert hash_mmh32("test") == 0xBA6BD213, "FAILED 1 -> hash_mmh32"

    # Test with a string that contains special characters
    assert hash_mmh32("abc$%^123") == 0x550327AC, "FAILED 2 -> hash_mmh32"

    # Test with a string that doesn't contain special characters
    assert hash_mmh64("test") == 0xAC7D28CC74BDE19D, "FAILED -> hash_mmh64"
