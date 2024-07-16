# -*- coding: utf-8 -*-
import os, sys, datetime, fire, pytz

from src.utils.utilmy_base import date_now
from src.utils.utilmy_log import log,log2,log3,loge
################################################################################################



########################################################################################
##### Date #############################################################################
def now_weekday_isin(day_week=None, timezone='Asia/Tokyo'):
    """Check if today is in the list of weekday numbers.
    Docs::
    
        true if now() is in the list of weekday numbers, false if not
        Args:
            day_week          :  [1,2,3],  0 = Sunday, 1 = Monday, ...   6 = Saturday           
            timezone (string) :  Timezone :  'UTC', 'Asia/Tokyo'  
    """
    # 0 is sunday, 1 is monday
    if not day_week:
        day_week = {0, 1, 2,4,5,6}

    # timezone = {'jp' : 'Asia/Tokyo', 'utc' : 'utc'}.get(timezone, 'utc')
    
    now_weekday = (datetime.datetime.now(tz=pytz.timezone(timezone)).weekday() + 1) % 7
    if now_weekday in day_week:
        return True
    return False


def now_hour_between(hour1="12:45", hour2="13:45", timezone="Asia/Tokyo"):
    """Check if the time is between   hour1 <  current_hour_time_zone < hour2
    Docs::

        Args:
            hour1 (string)    :     start format "%H:%M",  "12:45".
            hour2 (string)    :     end,  format "%H:%M",  "13:45".
            timezone (string) :  'Asia/Tokyo', 'utc' 
        Returns: true if the time is between two hours, false otherwise.
    """
    # Daily Batch time is between 2 time.
    # timezone = {'jp' : 'Asia/Tokyo', 'utc' : 'utc'}.get(timezone, 'utc')
    format_time = "%H:%M"
    hour1 = datetime.datetime.strptime(hour1, format_time).time()
    hour2 = datetime.datetime.strptime(hour2, format_time).time()
    now_weekday = datetime.datetime.now(tz=pytz.timezone(timezone)).time()       
    if hour1 <= now_weekday <= hour2:
        return True
    return False


def now_daymonth_isin(day_month, timezone="Asia/Tokyo"):
    """Check if today is in a List of days of the month in numbers
    Docs::

        Args:
            day_month (list of int) : List of days of the month in numbers.
            timezone (string)       : Timezone of time now. (Default to "Asia/Tokyo".)  
        Returns:
            Bool, true if today is in the list "day_month", false otherwise.
    """
    # 1th day of month
    #timezone = {'jp' : 'Asia/Tokyo', 'utc' : 'utc'}.get(timezone, 'utc')

    if not day_month:
        day_month = [1]

    now_day_month = datetime.datetime.now(tz=pytz.timezone(timezone)).day

    if now_day_month in day_month:
        return True
    return False


def time_sleep(nmax=5, israndom=True):
    """Time sleep function with random feature.
    Docs::

        Args:
            nmax (int)      : Seconds for the time sleep. (Default to 5.)   
            israndom (bool) : True if the argument "nmax" the max seconds will be chosen randomly. (Default to True.)
        Returns: None.
        Example:
            from utilmy import util_batch
            import datetime
            timezone = datetime.timezone.utc
            now_day_month = datetime.datetime.now(tz=timezone).day
            util_batch.time_sleep(nmax = 10, israndom=False)
    """
    import random, time
    if israndom:
       time.sleep( random.randrange(nmax) )
    else :
       time.sleep( nmax )





#####################################################################################################
if __name__ == '__main__':
    fire.Fire()
