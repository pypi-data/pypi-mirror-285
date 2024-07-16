# pylint: disable=W,C,R,E
# -*- coding: utf-8 -*-
"""
Docs:
   Global logger for python, defined with ENV variables at Bash Level.


### Code usage: Just import Alias :
from utils.utils_log import log,log2,log3,logd,logw,loge, log_error, log_warning

  log:  logging.info
  log2: logging.info  and print only if os.environ['log_verbositty] >=2 , Extra logging at low running cost
  log3: logging.info  and print only if os.environ['log_verbositty] >=3 , Extra logging at low running cost

  logw, log_warning: logging.warning
  loge, log_error:   logging.error


### Usage:
  In current bash, define those ENV

  With any ENV variable set, values are
    log_verbosity=10
    log_type="base"   ### stdout print

  Ex1: use only print as stdout, verbosity is set to 3
    export log_verbosity=3
    export log_type="base"    ### stdout print

  Ex2: use python default logging class and level is set to DEBUG
    export log_type="logging"
    export log_verbosity=1
    export log_config="log_level:DEBUG"


  Ex3: Use python default logging
    export log_type="logging"
    export log_verbosity=3

    ## Export to ztmp/log/log_YMD.log
    export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30"

    ## Pre-defined format (only for logging)
    export log_format="FORMAT_1"  ## 5  default format available : FORMAT_1, ..., FORMAT_5

    ### Setup own python logging format
    export log_format="%(asctime)s, %(process)d, %(pathname)s%(filename)s, %(funcName)s, %(lineno)s,  %(message)s"


  Ex4: Using JSON config
     export log_config_path="./my_log_config.json"
     {
         'log_type': 'logging',
         'log_level': 'DEBUG',
         'log_verbosity': 3,
         'log_config': "log_level:DEBUG;log_file:ztmp/log/log;rotate_time:s;rotate_interval:30",
     }

### Logging mode/type:
   'base'      :   stdout print
   'logging'   :   python logging class
   'basecolor' :   stdout color print
   'logging2'  :   python logging class with function name print ('ie debugging purpose)


"""

import json
import os
import sys
from pathlib import Path

import fire

######################################################################################
##### Global settting  ###############################################################
global LOG_CONFIG, VERBOSITY, LOG_TYPE, THISFILE_PATH
LOG_CONFIG = {}
LOG_TYPE = "base"

try:
    LOG_CONFIG_FILE = os.environ.get("log_config_path", os.getcwd() + "/log_config.json")
    with open(LOG_CONFIG_FILE, mode="r") as f:
        LOG_CONFIG = json.load(f)
except Exception as e:
    pass

THISFILE_PATH = Path(__file__).resolve().parent


def log_reload(set_verbosity: int = 1):
    global LOG_CONFIG, VERBOSITY, LOG_TYPE
    LOG_CONFIG["log_verbosity"] = os.environ.get(
        "log_verbosity", LOG_CONFIG.get("log_verbosity", 10)
    )

    #### base, logging, loguru
    LOG_CONFIG["log_type"] = os.environ.get("log_type", LOG_CONFIG.get("log_type", "base"))
    LOG_CONFIG["log_format"] = os.environ.get("log_format", LOG_CONFIG.get("log_format", None))
    LOG_CONFIG["log_config"] = os.environ.get("log_config", LOG_CONFIG.get("log_config", None))

    if isinstance(set_verbosity, int):
        LOG_CONFIG["log_verbosity"] = set_verbosity

    VERBOSITY = int(LOG_CONFIG["log_verbosity"])
    LOG_TYPE = LOG_CONFIG["log_type"]


log_reload()


######### Debug  ##############################################################################
def logi(*s):
    for si in s:
        print(si, eval(si), "")


##############################################################################################
if LOG_TYPE == "base":

    def log(*s):
        print(*s, flush=True)

    def log2(*s):
        if VERBOSITY >= 2:
            print(*s, flush=True)

    def log3(*s):  ### Debugging level 2
        if VERBOSITY >= 3:
            print(*s, flush=True)

    def logw(*s):
        if os.environ.get("log_warning_disable", "") == "1":
            print(*s, flush=True)
        else:
            print("warning:", *s, flush=True)

    def logc(*s):
        print("critical:", *s, flush=True)

    def loge(*s):
        print("error:", *s, flush=True)

    def logd(*s):
        print(*s, flush=True)


##############################################################################################
if LOG_TYPE == "logging":
    import logging

    ################### Logs #################################################################
    FORMAT = {
        "FORMAT_1": logging.Formatter("%(levelname)-7s,%(message)s"),
        "FORMAT_3": logging.Formatter(
            "%(levelname)-7s,%(filename)s:%(funcName)s:%(lineno)d,%(message)s"
        ),
        "FORMAT_6": logging.Formatter("%(asctime)s,  %(name)s, %(levelname)s, %(message)s"),
        "FORMAT_2": logging.Formatter(
            "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
        ),
        "FORMAT_4": logging.Formatter("%(asctime)s, %(process)d, %(filename)s,    %(message)s"),
        "FORMAT_5": logging.Formatter(
            "%(asctime)s, %(process)d, %(pathname)s%(filename)s, %(funcName)s, %(lineno)s,  %(message)s"
        ),
    }

    ########################################################################################
    ################### Logger #############################################################
    def logger_setup(
        logger_name=None,
        formatter=None,
        log_file=None,
        rotate_time="midnight",
        isconsole_output=True,
        logging_level=None,
    ):
        cfgs = os.environ.get("log_config", "")
        cfgs = cfgs.split(";")
        cfg = {}
        for si in cfgs:
            if len(si) < 3:
                continue
            try:
                si = si.split(":")
                cfg[si[0].strip()] = si[1].strip()
            except:
                pass

        logger_name = cfg.get("logger_name", logger_name)
        logging_level = cfg.get("log_level", logging_level)
        log_file = cfg.get("log_file", log_file)
        rotate_time = cfg.get("rotate_time", rotate_time)
        rotate_interval = int(cfg.get("rotate_interval", 1))

        logging_level = {
            "DEBUG": logging.DEBUG,
            "CRITICAL": logging.CRITICAL,
            "INFO": logging.INFO,
        }.get(logging_level, "DEBUG")
        print("log_config", cfg)

        # Gets root logger or local one
        logger = logging.getLogger(logger_name) if logger_name is not None else logging.getLogger()

        if isinstance(formatter, str):
            formatter = FORMAT.get(formatter, formatter)
        else:
            if "log_format" in os.environ:
                formatter = logging.Formatter(os.environ.get("log_format"))

        if formatter is None:
            formatter = FORMAT["FORMAT_1"]

        logger.setLevel(logging_level)  # better to have too much log than not enough

        if isconsole_output:
            logger.addHandler(logger_handler_console(formatter))

        if log_file is not None:
            logger.addHandler(
                logger_handler_file(
                    formatter=formatter,
                    log_file_used=log_file,
                    rotate_time=rotate_time,
                    interval=rotate_interval,
                )
            )

        # with this pattern, it's rarely necessary to propagate error up to parent
        logger.propagate = False
        return logger

    def logger_handler_console(formatter=None):
        formatter = FORMAT["FORMAT_1"] if formatter is None else formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        return console_handler

    def logger_handler_file(
        rotate_time: str = "midnight", formatter=None, log_file_used=None, interval=1, backupCount=5
    ):
        from logging.handlers import TimedRotatingFileHandler

        formatter = FORMAT["FORMAT_1"] if formatter is None else formatter
        if rotate_time is not None:
            ### "midnight"
            print("Rotate log", rotate_time)
            fh = TimedRotatingFileHandler(
                log_file_used, when=rotate_time, interval=interval, backupCount=backupCount
            )
            fh.setFormatter(formatter)
            return fh
        else:
            fh = logging.FileHandler(log_file_used)
            fh.setFormatter(formatter)
            return fh

    #######################################################################################
    ##### Alias ###########################################################################
    logger = logger_setup()

    def log(*s):
        logger.info(",".join([str(t) for t in s]))

    def log2(*s):
        if VERBOSITY >= 2:
            logger.info(",".join([str(t) for t in s]))

    def log3(*s):  ### Debuggine level 2
        if VERBOSITY >= 3:
            logger.info(",".join([str(t) for t in s]))

    def logd(*s):
        logger.debug(",".join([str(t) for t in s]))

    def logw(*s):
        logger.warning(",".join([str(t) for t in s]))

    def logc(*s):
        logger.critical(",".join([str(t) for t in s]))

    def loge(*s):
        logger.error(",".join([str(t) for t in s]))

    def logr(*s):
        logger.info(",".join([str(t) for t in s]))


##### Alias ##############################################################################
log_debug = logd
log_error = loge
log_warning = logw


########################################################################################
if __name__ == "__main__":
    fire.Fire()
