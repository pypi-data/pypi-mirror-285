# -*- coding: utf-8 -*-
""" Universal logger
Doc::

    bash ENV variables
        export log_verbosity=10
        export log_type='logging'   #  / 'base' / 'loguru'
        export log_format="%(asctime)s.%(msecs)03dZ %(levelname)s %(message)s"
        export log_config="log_level:DEBUG;log_file:ztmp/log/log;rotate_time:midnight;rotate_interval:1"


    # The severity levels
    # Level name    Severity value  Logger method
    # TRACE         5               logger.trace()
    # DEBUG         10              logger.debug()
    # INFO          20              logger.info()
    # SUCCESS       25              logger.success()
    # WARNING       30              logger.warning()
    # ERROR         40              logger.error()
    # CRITICAL      50              logger.critical()

    Format
        %(asctime)s         -> 2022-03-30 14:48:06,054 -> 時刻 (人が読める形式)
        %(created)f         -> 1648619286.054090 -> 時刻 (time.time()形式)
        %(filename)s        -> app_main.py -> ファイル名
        %(funcName)s        -> test_formats -> 関数名
        %(levelname)s       -> DEBUG -> ロギングレベルの名前
        %(levelno)s         -> 10 -> ロギングレベルの数値
        %(lineno)d          -> 77 -> 行番号
        %(module)s          -> app_main -> モジュールの名前
        %(msecs)d           -> 54 -> 時刻のミリ秒部分 (milliseconds)
        %(name)s            -> __main__ -> ロガーの名前
        %(pathname)s        -> F:\apps\data\app_main.py -> ファイルパス
        %(process)d         -> 9848 -> プロセスID (PID)
        %(processName)s     -> MainProcess -> プロセス名
        %(relativeCreated)d -> 15 -> logging モジュール読み込みからの時刻 (ミリ秒)
        %(thread)d          -> 9384 -> スレッドID (TID)
        %(threadName)s      -> MainThread -> スレッド名

"""
import os, sys, json, fire
from typing import Any, Union
from logging.handlers import SocketHandler
from pathlib import Path


######################################################################################
##### Global settting  ###############################################################
LOG_CONFIG = {}
LOG_TYPE   ='base'

try:
    LOG_CONFIG_FILE = os.environ.get('log_config_path',  os.getcwd() + "/log_config.json" )
    with open(LOG_CONFIG_FILE, mode='r') as f:
        LOG_CONFIG = json.load(f)
except Exception as e:
    pass

THISFILE_PATH = Path(__file__).resolve().parent


def log_reload(set_verbosity:int=None):
    global LOG_CONFIG, VERBOSITY, LOG_TYPE
    LOG_CONFIG['log_verbosity']= os.environ.get('log_verbosity', LOG_CONFIG.get('log_verbosity',10))

    #### base, logging, loguru
    LOG_CONFIG['log_type']     = os.environ.get('log_type',      LOG_CONFIG.get('log_type',"base"))
    LOG_CONFIG['log_format']   = os.environ.get('log_format',    LOG_CONFIG.get('log_format', None))
    LOG_CONFIG['log_config']   = os.environ.get('log_config',    LOG_CONFIG.get('log_config', None))


    if isinstance(set_verbosity, int ):
        LOG_CONFIG['log_verbosity']=set_verbosity

    VERBOSITY   = int(LOG_CONFIG["log_verbosity"])
    LOG_TYPE    = LOG_CONFIG["log_type"]


log_reload()



######### Debug  ##############################################################################
def logi(*s):
    for si in  s:
       print(si, eval(si), "")




##############################################################################################
if LOG_TYPE == 'base':
    def log(*s):
        """function log.
        """
        print(*s, flush=True)


    def log2(*s):
        """function log2.
        """
        if VERBOSITY >=2 : print(*s, flush=True)


    def log3(*s):  ### Debugging level 2
        """function log3.
        """
        if VERBOSITY >=3 : print(*s, flush=True)


    def logw(*s):
        """function log warning
        """
        if os.environ.get('log_warning_disable', "") =="1":
            print(*s, flush=True)            
        else:
            print('warning:',*s, flush=True)


    def logc(*s):
        """function log critical
        """
        print('critical:',*s, flush=True)


    def loge(*s):
        """function log error
        """
        print('error:',*s, flush=True)


    def logr(*s):
        """function logr.
        """
        print(*s, flush=True)



    #########################################################################################
    def test_log():
        """function test.
        Doc::
        """
        log3("debug2")
        log2("debug")
        log("info")
        logw("warning")
        loge("error")
        logc("critical")

        try:
            a = 1 / 0
        except Exception as e:
            logr("error", e)
            loge("Catcch"), e



##############################################################################################
if LOG_TYPE == 'logging':
    import logging, socket
    ################### Logs #################################################################
    FORMAT ={
     "FORMAT_1":  logging.Formatter("%(levelname)-7s,%(message)s")
    ,"FORMAT_3":  logging.Formatter("%(levelname)-7s,%(filename)s:%(funcName)s:%(lineno)d,%(message)s")
    ,"FORMAT_6":  logging.Formatter("%(asctime)s,  %(name)s, %(levelname)s, %(message)s")
    ,"FORMAT_2":  logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s' )
    ,"FORMAT_4":  logging.Formatter("%(asctime)s, %(process)d, %(filename)s,    %(message)s")
    ,"FORMAT_5":  logging.Formatter(
        "%(asctime)s, %(process)d, %(pathname)s%(filename)s, %(funcName)s, %(lineno)s,  %(message)s")
    }


    ########################################################################################
    ################### Logger #############################################################
    def logger_setup( logger_name=None,
        formatter=None,
        log_file=None,
        rotate_time="midnight",
        isconsole_output=True,
        logging_level=None,
    ):
        """  Python logger setup
        Docs::

            export log_config="logging_level:DEBUG;log_file:ztmp/log/log;rotate_time:midnight;rotate_interval:1"            
            logger = logger_setup()

            rotate_time :
                Calculate the real rollover interval, which is just the number of
                seconds between rollovers.  Also set the filename suffix used when
                a rollover occurs.  Current 'when' events supported:
                S - Seconds
                M - Minutes
                H - Hours
                D - Days
                midnight - roll over at midnight
                W{0-6} - roll over on a certain day; 0 - Monday

        """

        cfgs = os.environ.get('log_config', '')
        cfgs = cfgs.split(";")
        cfg  = {}
        for si in cfgs :
            if len(si) < 3: continue
            try :
               si = si.split(":")
               cfg[ si[0].strip() ] = si[1].strip()
            except:
                pass

        logger_name      = cfg.get('logger_name',    logger_name)
        logging_level    = cfg.get('log_level',      logging_level)
        log_file         = cfg.get('log_file',       log_file)
        rotate_time      = cfg.get("rotate_time",    rotate_time)
        rotate_interval  = int( cfg.get("rotate_interval",    1))

        logging_level = {'DEBUG':    logging.DEBUG,
                         "CRITICAL": logging.CRITICAL,
                         'INFO' :    logging.INFO  }.get(logging_level, 'DEBUG')
        print('log_config', cfg)

        # Gets the root logger or local one
        logger = logging.getLogger(logger_name)  if logger_name is not None  else logging.getLogger()

        if isinstance(formatter, str):
            formatter = FORMAT.get(formatter, formatter)
        else :
            if 'log_format' in os.environ :
                formatter = logging.Formatter(os.environ.get('log_format'))

        if formatter is None :
            formatter = FORMAT['FORMAT_1']


        logger.setLevel(logging_level)  # better to have too much log than not enough

        if isconsole_output:
            logger.addHandler(logger_handler_console(formatter))

        if log_file is not None:
            logger.addHandler(logger_handler_file(formatter=formatter, log_file_used=log_file, rotate_time=rotate_time,
                                                  interval= rotate_interval))

        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False
        return logger


    def logger_handler_console(formatter=None):
        formatter = FORMAT["FORMAT_1"] if formatter is None else formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        return console_handler


    def logger_handler_file(rotate_time:str="midnight", formatter=None, log_file_used=None,
                            interval=1, backupCount=5):
        from logging.handlers import TimedRotatingFileHandler
        formatter = FORMAT["FORMAT_1"] if formatter is None else formatter
        if rotate_time is not None:
            ### "midnight"
            print("Rotate log", rotate_time)
            fh = TimedRotatingFileHandler(log_file_used, when=rotate_time, interval=interval, backupCount= backupCount)
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
        """function log."""
        logger.info(",".join([str(t) for t in s]))


    def log2(*s):
        """function log2."""
        if VERBOSITY >=2:  logger.info(",".join([str(t) for t in s]))


    def log3(*s):  ### Debuggine level 2
        """function log3."""
        if VERBOSITY >=3 :logger.info(",".join([str(t) for t in s]))


    def logd(*s):
        """function log2."""
        logger.debug(",".join([str(t) for t in s]))


    def logw(*s):
        """function logw."""
        logger.warning(",".join([str(t) for t in s]))


    def logc(*s):
        """function logc."""
        logger.critical(",".join([str(t) for t in s]))


    def loge(*s):
        """function loge."""
        logger.error(",".join([str(t) for t in s]))


    def logr(*s):
        """function logr."""
        logger.info(",".join([str(t) for t in s]))


    #########################################################################################
    def test_log():
        """function test.
        """
        log3("debug2")
        log2("debug")
        log("info")
        logw("warning")
        loge("error")
        logc("critical")

        try:
            a = 1 / 0
        except Exception as e:
            logr("error", e)
            loge("Catcch"), e



##############################################################################################
if LOG_TYPE == 'logging2':
    import logging
    ################### Logs #################################################################
    FORMAT ={
     ### Correct Filename, functionName
     "FORMAT_1":  logging.Formatter("%(levelname)-5s,%(filename2)s:%(funcName2)s,%(message)s"),
     "FORMAT_2":  logging.Formatter("%(levelname)-7s,%(funcName2)-7s,%(message)s"),
     "FORMAT_3":  logging.Formatter("%(levelname)-7s,%(message)s"),
     "FORMAT_8":  logging.Formatter("%(levelname)-7s,%(filename)s:%(funcName)s:%(lineno)d,%(message)s"),

     "FORMAT_4":  logging.Formatter("%(asctime)s,  %(name)s, %(levelname)s, %(message)s"),
     "FORMAT_5":  logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s' ),
     "FORMAT_6":  logging.Formatter("%(asctime)s, %(process)d, %(filename)s,    %(message)s"),
     "FORMAT_7":  logging.Formatter(
        "%(asctime)s, %(process)d, %(pathname)s%(filename)s, %(funcName)s, %(lineno)s,  %(message)s")
    }


    ########################################################################################
    ################### Logger #############################################################
    def logger_setup( logger_name=None,
        formatter=None,
        log_file=None,
        rotate_time="midnight",
        isconsole_output=True,
        logging_level=None,
    ):
        """  Python logger setup
        Docs::

            export log_config="logging_level:DEBUG;log_file:ztmp/log/log;rotate_time:midnight;rotate_interval:1"
            logger = logger_setup()

            rotate_time :
                Calculate the real rollover interval, which is just the number of
                seconds between rollovers.  Also set the filename suffix used when
                a rollover occurs.  Current 'when' events supported:
                S - Seconds
                M - Minutes
                H - Hours
                D - Days
                midnight - roll over at midnight
                W{0-6} - roll over on a certain day; 0 - Monday

        """

        cfgs = os.environ.get('log_config', '')
        cfgs = cfgs.split(";")
        cfg  = {}
        for si in cfgs :
            if len(si) < 3: continue
            try :
               si = si.split(":")
               cfg[ si[0].strip() ] = si[1].strip()
            except:
                pass

        logger_name      = cfg.get('logger_name',    logger_name)
        logging_level    = cfg.get('log_level',      logging_level)
        log_file         = cfg.get('log_file',       log_file)
        rotate_time      = cfg.get("rotate_time",    rotate_time)
        rotate_interval  = int( cfg.get("rotate_interval",    1))

        logging_level = {'DEBUG':    logging.DEBUG,
                         "CRITICAL": logging.CRITICAL,
                         'INFO' :    logging.INFO  }.get(logging_level, 'DEBUG')
        print('log_config', cfg)

        # Gets the root logger or local one
        logger = logging.getLogger(logger_name)  if logger_name is not None  else logging.getLogger()

        if isinstance(formatter, str):
            formatter = FORMAT.get(formatter, formatter)
        else :
            if 'log_format' in os.environ :
                formatter = logging.Formatter(os.environ.get('log_format'))

        if formatter is None :
            formatter = FORMAT['FORMAT_1']


        logger.setLevel(logging_level)  # better to have too much log than not enough

        if isconsole_output:
            logger.addHandler(logger_handler_console(formatter))

        if log_file is not None:
            logger.addHandler(logger_handler_file(formatter=formatter, log_file_used=log_file, rotate_time=rotate_time,
                                                  interval= rotate_interval))

        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False
        return logger


    def logger_handler_console(formatter=None):
        formatter = FORMAT["FORMAT_1"] if formatter is None else formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        return console_handler


    def logger_handler_file(rotate_time:str="midnight", formatter=None, log_file_used=None,
                            interval=1, backupCount=5):
        from logging.handlers import TimedRotatingFileHandler
        formatter = FORMAT["FORMAT_1"] if formatter is None else formatter
        if rotate_time is not None:
            ### "midnight"
            print("Rotate log", rotate_time)
            fh = TimedRotatingFileHandler(log_file_used, when=rotate_time, interval=interval, backupCount= backupCount)
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
        """function log."""
        ff = sys._getframe(1)
        logger.info(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                          'filename2': ff.f_code.co_filename, })

    def log2(*s):
        """function log2."""
        if VERBOSITY >=2:
            ff = sys._getframe(1)
            logger.info(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                              'filename2': ff.f_code.co_filename, })

    def log3(*s):  ### Debuggine level 2
        """function log3."""
        if VERBOSITY >=3 :
            ff = sys._getframe(1)
            logger.info(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                              'filename2': ff.f_code.co_filename, })

    def logd(*s):
        """function log2."""
        ff = sys._getframe(1)
        logger.debug(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                           'filename2': ff.f_code.co_filename, })

    def logw(*s):
        """function logw."""
        ff = sys._getframe(1)
        logger.warning(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                             'filename2': ff.f_code.co_filename, })

    def logc(*s):
        """function logc."""
        ff = sys._getframe(1)
        logger.critical(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                              'filename2': ff.f_code.co_filename, })

    def loge(*s):
        """function loge."""
        ff = sys._getframe(1)
        logger.error(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                           'filename2': ff.f_code.co_filename, })

    def logr(*s):
        """function logr."""
        ff = sys._getframe(1)
        logger.info(",".join([str(t) for t in s]), extra={'funcName2': ff.f_code.co_name,
                                                          'filename2': ff.f_code.co_filename, })


    #########################################################################################
    def test_log():
        """function test.
        """
        log3("debug2")
        log2("debug")
        log("info")
        logw("warning")
        loge("error")
        logc("critical")

        try:
            a = 1 / 0
        except Exception as e:
            logr("error", e)
            loge("Catch"), e


##############################################################################################
if LOG_TYPE == 'basecolor':
    #
    # Colors: https://github.com/termcolor/termcolor
    #

    from termcolor import cprint
    import time
    from models import PromptRequest, PromptResponse, ActionResponse


    class Logger:
        def __init__(self) -> None:
            self.moving_time = time.time()

        def _get_timing(self):
            now = time.time()
            delta = now - self.moving_time
            stats = "[{:.1f}s | +{:.1f}s]".format(now, delta)
            self.moving_time = now
            return stats

        def log_info(self, message: str):
            cprint(message, "magenta", "on_black")

        def log_success(self, message: str):
            print(self._get_timing(), end=" ")
            cprint(message, "green", "on_black")

        def log_warning(self, message: str):
            print(self._get_timing(), end=" ")
            cprint(message, "yellow", "on_black")

        def log_error(self, message: str):
            print(self._get_timing(), end=" ")
            cprint(message, "red", "on_black")

        def log_neutral(self, message: str):
            print(self._get_timing(), end=" ")
            cprint(message, "dark_grey", "on_black")

        def log_human(self, message: PromptRequest):
            self.log_neutral("[sid={}]".format(message.session_id))
            cprint(message.text, "white", "on_blue")

        def log_ai(self, message: PromptResponse, is_first_message: bool):
            log_fn = self.log_warning if is_first_message else self.log_neutral
            log_fn(
                "[sid={} | HTTP{} | chunk={}/{} | +{:.1f}s]".format(
                    message.session_id,
                    message.status,
                    message.chunk_prefix,
                    message.chunk_prompt_length,
                    message.time_from_request,
                )
            )
            cprint(message.text, "white", "on_cyan")

        def log_action(self, message: ActionResponse):
            self.log_neutral("[chunk_id={}]".format(message.chunk_id))
            cprint(message.raw, "white", "on_magenta")

        def log_separator(self):
            cprint("-" * 80, "dark_grey", "on_black")




########################################################################################
if __name__ == "__main__":
    fire.Fire()





