"""Regression test
Docs::

     source scripts/bins/env.sh


     python tests/regressions/client.py  check1

     python tests/regressions/client.py  check2 --nmax 5  --nclient 3

     python tests/regressions/client.py  check3 --nmax 5  --nclient 3

"""

import os
import sys
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Sequence

import fire
import requests

from src.utils.util_base import multithread_run
from src.utils.util_config import config_load
from src.utils.util_log import log

################################################################################
JSON1 = {
    "data": "iVBORw0KGgoAAAANSUhEUgAAAGQAAAAeCAIAAABVOSykAAAEPklEQVR4nO2aSUgCfRjGH8fU1BbbLlLkITpEUJEttFldAiuIoGt0aIHqHB5LoqIgDwUd6tJ6qFMR1KVDUFBBC6JDkKmHoAUsEsPd+Q5/GMTKZsyPrw/mufn6zjM/nv/MO/8RRQzDQBA3Uf81wP9JQlg8JITFQ0JYPCSExUNCWDwkhMVDQlg8JITFQz+H5XK5gsHgv0fA0f8vYPwQ1vLycnFx8cfHR/KoEvH/IxhgvpfX6yU9b29vcdoSFkf/P4LBMIwws3hICIuPvrvkRkZGYjqvr6/Zbx0Ox9DQkEajkUqlOTk5er3+8PAwxuH+/n5gYECj0Ugkkuzs7NbW1o2NjUgkwsU/KRhms1kqlQKYn5+P9tze3gYgkUhubm44YhAlEtbh4WFaWtrn3A0GA3s4TdNZWVmfewYHB5MVFheMyclJAJmZmc/Pz6Ty/v6uVqsBGI1G7hg/hMV8M/mcTmdGRgaAjo6O8/Nzj8fz+PhoMpnkcjmAra0t0tbV1QWgu7ubpmmfz/fy8mIymSiKAnB5eRnHP7kYoVCoqqoKQH9/P6kMDw8DqKysDAaDvDASCWt0dBRAW1tbOByObl5dXQVQXFxMPhYWFgK4urqK7unr6wMwMTHBi/I3GAzDWK1WmUxGUdTp6enR0RFFUTKZzGKxxPf/UrzDKigoALC7uxvT7Pf7U1NTAdzd3TEMU19fD6CsrGxzc/Pp6Ym7f3IxiGZmZgDk5+erVCoA09PTCWAwfMNyu92fZ0SM9vf3GYbZ29sTiURssbS0dGxs7OLiIgHK32AQhUKh2tpaUq+pqQmFQomFxW/rwIWS9HR2dh4cHFRXV5OixWKZnZ2trq7W6XQvLy+8TvobDCKxWExmKIDm5maxWJzgiXkt6evrK6nQNB1/EVg5HI6lpaWenp7c3FxyrF6v57Wkv8ew2WxKpZIcQnYM8f2/E++ZlZeXB2BlZYULZbTC4fDU1BQAiqL8fj93yl9ihMPhhoYGAI2NjU1NTQDKy8sDgUB8/y8VLyy/309cXC4XW+zt7QWg0Wg8Hk9089nZGXnQPD8/Pzw8iEQihUIRc/qbmxsAKSkphPVL/yRikMrc3BwApVJps9nsdju5xMbHx+P7f6l4YTEMk5KSAmBnZycQCJCHtNVqJY+bmpqa4+Njn8/ncrnW19dzcnIADAwMkANbWloA1NXVHR8fu91uj8dzcnKi1WoBtLe3x/FPLgZN06RtcXGRVBYWFj7fjBwxfgiroqKCnW7sm8T29rZMJvs8/nQ6ndfrJT12u51wx0itVtvt9vj+ycIIBoNkeVpbW9nXrEgkwt6M7L6UI8YPYZnN5rq6OrlcrlKp1tbW2Prt7S1575NKpQqFQqvVmkwmMolY2e32oaGhoqIi0lNSUmIwGGIu9e/8k4JhNBoBpKenO53OaDebzaZQKBC1PeaIIWKE/zpwlvATDQ/9A5KSwHp7nzI6AAAAAElFTkSuQmCC",
    "token": "hi",
}


###############################################################################
def check0(
    cfg: str = "config/dev/config_dev.yaml",
):
    cfgd = config_load(cfg)
    port = cfgd["service"]["port"]
    version = cfgd["service"]["version"]

    url0 = f"http://localhost:{port}/{version}/imgsync"
    log(url0)
    r = requests.post(url0, json=JSON1)
    log(r.json())


def check1(cfg: str = "config/dev/config_dev.yaml"):
    cfgd = config_load(cfg)
    port = cfgd["service"]["port"]
    version = cfgd["service"]["version"]

    url0 = f"http://localhost:{port}/{version}/imgsync"
    x = [(url0, JSON1)]
    fun_async(x)


def check2(cfg: str = "config/dev/config_dev.yaml", nmax=10, nloop=1, nclient=3):
    """imgsync tests
    python tests/regressions/client.py  check2 --nmax 10  --nclient 3

    """
    cfgd = config_load(cfg)
    port = cfgd["service"]["port"]
    version = cfgd["service"]["version"]

    url0 = f"http://localhost:{port}/{version}/imgsync"
    djson = JSON1
    inputs = []
    for i in range(0, nmax * nclient):
        inputs.append([url0, djson])
    res = multithread_run(fun_async, input_list=inputs, n_pool=nclient, verbose=False)
    log("resutl:", res)


def check3(cfg: str = "config/dev/config_dev.yaml", nmax=10, nloop=1, nclient=3):
    """imgasync tests
    python tests/regressions/client.py  check3 --nmax 10  --nclient 3

    """
    cfgd = config_load(cfg)
    port = cfgd["service"]["port"]
    version = cfgd["service"]["version"]
    url0 = f"http://localhost:{port}/{version}/imgasync"
    djson = JSON1
    inputs = []
    for i in range(0, nmax * nclient):
        inputs.append([url0, djson])
    res = multithread_run(fun_async, input_list=inputs, n_pool=nclient, verbose=False)
    log("resutl:", res)


def fun_async(args_batch):
    """Asynchronous function that takes a batch of arguments and sends POST requests for each argument,
       collecting JSON responses.

    Args:
        args_batch: List of argument tuples, where each tuple contains a URL and JSON data to be sent in POST request.

    Returns:
        List: List of JSON responses received from POST requests.
    """
    res = []
    for ii, arg in enumerate(args_batch):
        log("pid: ", ii, "nargs:", len(arg))
        r = requests.post(arg[0], json=arg[1])
        res.append(r.json())
    return res


######################################################################################
if __name__ == "__main__":
    fire.Fire()
