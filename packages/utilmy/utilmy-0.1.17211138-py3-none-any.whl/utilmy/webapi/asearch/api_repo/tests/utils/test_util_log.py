# -*- coding: utf-8 -*-
""" Test for universal logger
Docs::


"""
import importlib
import json
import logging
import os

from src.utils.util_base import dir_testinfo
from src.utils.util_log import log, log2, log3, logc, loge, logw


##############################################################################
def test1():
    """function test1.

    Testing functions log3, log2, log, logw, loge, logc, logr

    # These libraries are for testing output.
    # https://stackoverflow.com/questions/33767627/python-write-unittest-for-console-print

    """
    os.environ["log_verbosity"] = "10"
    os.environ["log_type"] = "base"

    with open("config.json", mode="w") as f:
        f.write(json.dumps({"log_verbosity": 10, "log_type": "base"}, indent=4))

    log3("debug2")
    log2("debug")
    log("info")
    logw("warning")
    logc("critical")

    try:
        a = 1 / 0
    except Exception as e:
        loge("Exception"), e

    log("finish")


def test_logging():
    """function test_logging.

    Testing functions in util_log.py

    """
    os.environ["log_verbosity"] = "10"
    os.environ["log_type"] = "logging"

    with open("config.json", mode="w") as f:
        f.write(json.dumps({"log_verbosity": 10, "log_type": "logging"}, indent=4))

    from src.utils import util_log

    importlib.reload(util_log)

    s = "test logger_name"
    print("\ntest logger_name")
    logger = util_log.logger_setup(logger_name="test_logging")
    log2(s)

    # test isrotate
    s = "test isrotate"
    logger = util_log.logger_setup(rotate_time="minight")
    log2(s)

    # test isconsole_output
    s = "test isconsole_output"
    print("\ntest isconsole_output ")
    logger = util_log.logger_setup(isconsole_output=False)
    log2(s)

    # test logging_level
    print("\ntest logging levels")
    log_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]

    for log in log_levels:
        logger = util_log.logger_setup(logging_level=log)
        if log == logging.CRITICAL:
            s = "critical"
            logc(s)
        elif log == logging.ERROR:
            s = "error"
            loge(s)
        elif log == logging.WARNING:
            s = "warning"
            logw(s)
        elif log == logging.INFO:
            s = "info"
            log2(s)
        elif log == logging.DEBUG:
            s = "debug"
            log3(s)

    # test log_file
    s = "test log_file"
    print("\ntest log_file test.log")
    logger = util_log.logger_setup(log_file="test.log")
    log2(s)


def test4():
    """function test4.

    Testing functions log2 and log3 with verbosity equals to 1.

    """
    import io
    import sys

    os.environ["log_verbosity"] = "1"
    os.environ["log_type"] = "base"

    with open("config.json", mode="w") as f:
        f.write(json.dumps({"log_verbosity": 1, "log_type": "base"}, indent=4))

    log("####### log2() ..")
    captured_output = io.StringIO()
    sys.stdout = captured_output
    log2("testing log2")
    sys.stdout = sys.__stdout__
    result_value = captured_output.getvalue()
    assert result_value == "", "FAILED base  log return value isn't expected"

    log("####### log3() ..")
    captured_output = io.StringIO()
    sys.stdout = captured_output
    log3("testing log3")
    sys.stdout = sys.__stdout__
    result_value = captured_output.getvalue()
    assert result_value == "", "FAILED base  log return value isn't expected"


def test5():
    """function test5.

    Testing functions in util_log.py.

    """

    from src.utils import util_log as util_log

    drepo, dirtmp = dir_testinfo()

    util_log.log("Testing default env values")
    importlib.reload(util_log)
    assert util_log.VERBOSITY == int(
        os.environ.get("log_verbosity", 10)
    ), "FAILED; VERBOSITY wasn't expected"
    assert util_log.LOG_TYPE == "base", "FAILED; LOG_TYPE wasn't expected"

    util_log.log("Testing log_verbosity and log_type")
    os.environ["log_verbosity"] = "1"
    os.environ["log_type"] = "logging"
    importlib.reload(util_log)
    assert util_log.VERBOSITY == 1, "FAILED; VERBOSITY wasn't expected"
    assert util_log.LOG_TYPE == "logging", "FAILED; LOG_TYPE wasn't expected"
    os.environ.pop("log_verbosity", None)
    os.environ.pop("log_type", None)


############################################################################
if __name__ == "__main__":
    fire.Fire()
