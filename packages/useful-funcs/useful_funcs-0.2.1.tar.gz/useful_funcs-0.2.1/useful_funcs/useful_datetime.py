'''
    This code is for handling operations related to datetime
    such as comparison, time difference, etc.
'''
__author__ = "Surya Datta Sudhakar"
__copyright__ = "Copyright 2023, INCOIS"

import datetime
import zoneinfo as zi
import pandas as pd
import numpy as np


'''
https://docs.python.org/3/library/datetime.html

d = date(2005, 7, 14)
t = time(12, 30)
datetime.datetime.combine(d, t)

dt1 = datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
dt2 = datetime.datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")

MINYEAR <= year <= MAXYEAR,
1 <= month <= 12,
1 <= day <= number of days in the given month and year,
0 <= hour < 24,
0 <= minute < 60,
0 <= second < 60,
0 <= microsecond < 1000000,

'''


def print_timezones():
    """This function prints all the available timezones.

    -------
    Requires
    --------
    tzdata

    (mostly available internally for Linux Users)

    Notes
    -----
    If zoneinfo._common.ZoneInfoNotFoundError: 'No time zone found with key <***/*****>'.

    Try performing `pip install tzdata` or `pip install --upgrade tzdata`
    """
    timezones = list(zi.available_timezones())
    timezones.sort()
    for tz in timezones:
        print(tz)


def datetime_compare(date1: datetime.datetime, date2: datetime.datetime) -> int:
    '''date1 gives output as YYYY-mm-dd HH:MM:SS
        <class 'datetime.datetime'>

    Parameters
    ----------
    date1: datetime.datetime

    date2: datetime.datetime

    Returns
    -------
    Returns 1 if your date1 is greater than date2
    Returns 0 if your date1 is equal to date2
    Returns -1 if your date1 is less than date2
    Returns -99999 if your date1 is not related to date2     
    '''
    try:
        if not (isinstance(date1, datetime.datetime) and isinstance(date2, datetime.datetime)):
            raise TypeError()
    except TypeError:
        print("Kindly send in datetime.datetime objects")
    else:
        if date1 > date2:
            return 1
        elif date1 == date2:
            return 0
        elif date1 < date2:
            return -1
        else:
            return -99999


def datetime_hour_compare(date1: datetime.datetime, date2: datetime.datetime) -> int:
    '''date1.time().hour gives output as HH
        <class 'int'> HH

    --------
    Returns
    -------
        1. Returns 1 if your date1.time().hour is greater than date2.time().hour
        2. Returns 0 if your date1.time().hour is equal to date2.time().hour
        3. Returns -1 if your date1.time().hour is less than date2.time().hour
        4. Returns -99999 if your date1.time().hour is not related to date2.time().hour   
    '''
    try:
        if not (isinstance(date1, datetime.datetime) and isinstance(date2, datetime.datetime)):
            raise TypeError()
    except TypeError:
        print("Kindly send in datetime.datetime objects")
    else:
        if date1.date() > date2.date():
            return -99999
        elif date1.date() == date2.date():
            print(type(date1.time().hour), date1.time().hour)
            if date1.time().hour > date2.time().hour:
                return 1
            elif date1.time().hour == date2.time().hour:
                return 0
            elif date1.time().hour < date2.time().hour:
                return -1
            else:
                return -88888
        elif date1.date() < date2.date():
            return -99999
        else:
            return -99999


def epoch_to_date(epoch_time):
    date_time = datetime.datetime.fromtimestamp(epoch_time)
    print("Given epoch time:", date_time)


def datetime_date_compare(date1: datetime.datetime, date2: datetime.datetime) -> int:
    """date1.date() gives output as YYYY-MM-DD

    --------
    <class 'datetime.datetime.date'>

    --------

    Returns
    -------
        1 if your date1.date() is greater than date2.date()
    
        0 if your date1.date() is equal to date2.date()
    
        -1 if your date1.date() is less than date2.date()
    
        -99999 if your date1.date() is not related to date2.date()
    """
    try:
        if not (isinstance(date1, datetime.datetime) and isinstance(date2, datetime.datetime)):
            raise TypeError()
    except TypeError:
        print("Kindly send in datetime.datetime objects")
    else:
        if date1.date() > date2.date():
            return 1
        elif date1.date() == date2.date():
            return 0
        elif date1.date() < date2.date():
            return -1
        else:
            return -99999
        

def extract_times(date_time_list, **kwargs):
    """
    Parameters
    ----------
    date_time_list: 
        any list/numpy list/pandas series containing datetimes
    
    useful_hours: 
        default useful Datetimes here mean that the hour value of the date
    is either 11, 12 or 13 with first preference given to 12, then to 11 and then to 13.
    However any other set of dates can be given as a list with the first element of the list
    having higest priority and the last element having lowest priority.

    Returns
    -------
    list containing useful datetimes
    
    """

    useful_hours = kwargs.get("useful_hours", [11, 12, 13])
    list_of_useful_datetime = []
    date_np_array = date_returner(date_time_list)
    
    for date in date_np_array:
        if type(date) is np.datetime64:
            date = np.datetime64(date).astype(datetime.datetime)
            date = datetime.datetime.utcfromtimestamp(date * 1e-9)
        
        if date.hour in useful_hours:
            list_of_useful_datetime.append(date)

    i = 0
    while (i < len(list_of_useful_datetime)):
        if list_of_useful_datetime[i].hour == 11:
            try:
                if list_of_useful_datetime[i].date() == list_of_useful_datetime[i+1].date():
                    if list_of_useful_datetime[i+1].hour == 12:
                        list_of_useful_datetime.pop(i)
                    elif list_of_useful_datetime[i+1].hour == 13:
                        list_of_useful_datetime.pop(i+1)
            except Exception:
                pass

        if list_of_useful_datetime[i].hour == 12:
            try:
                if list_of_useful_datetime[i].date() == list_of_useful_datetime[i+1].date():
                    if list_of_useful_datetime[i+1].hour == 13:
                        list_of_useful_datetime.pop(i+1)
            except Exception:
                pass
        i += 1
    
    return np.array(list_of_useful_datetime)


def date_returner(date_list) -> np.ndarray:
    """DATE RETURNER -> converts dates as numpy datetime64, pandas Timestamps, strings
    into datetime.datetime objects.
    
    --------
    Parameters
    ----------
    date_time_list: list / np.ndarray
        should contain dates as numpy datetime64, pandas Timestamps, strings objects

        
    Returns
    -------
    date_list_output: np.ndarray
        contains all the input dates as datetime.datetime objects
    """
    if all(type(x) is datetime.datetime for x in date_list):
        if (type(date_list) is np.ndarray):
            return date_list
        else:
            return np.array(date_list)

    elif all(type(x) is np.datetime64 for x in date_list) or\
        all(type(x) is pd._libs.tslibs.timestamps.Timestamp for x in date_list):

        if (type(date_list) is pd.core.series.Series):
            date_list = date_list.array.asi8
            def date_return(date: int):
                date = datetime.datetime.utcfromtimestamp(date * 1e-9)
                return date
            date_vec = np.vectorize(date_return)
            date_list_output = date_vec(date_list)
            return date_list_output

        elif (isinstance(date_list, np.ndarray)):
            date_list = date_list.tolist()
            def date_return(date: int):
                date = datetime.datetime.utcfromtimestamp(date * 1e-9)
                return date
            date_vec = np.vectorize(date_return)
            date_list_output = date_vec(date_list)
            return date_list_output
        

    elif all(type(x) is str for x in date_list):
        def date_return(date: str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            return date
            
        date_vec = np.vectorize(date_return)
        date_list_output = date_vec(date_list)
        return date_list_output
    
    else:
        raise TypeError


def common_dates(date_list1: list, date_list2: list, **kwargs):
    """Accepts two datetime lists and returns the common dates in both of them.

    --------
    Uses date_returner function

    --------
    Parameters
    ----------
    date_list1: 
        Regular list or numpy or pandas list of datetimes

    date_list2: 
        Regular list or numpy or pandas list of datetimes
    
    Kwargs
    ------
    mode: str
        'datetime','date' values accepted.
        'datetime' -> retains the time component of datetime object
        'date' -> discards the time component of datetime object

        If time component is needed in the return values, use 'datetime'.
        If time component is not needed in the return values, use 'date'.


    lr: str
        'left', 'right' values accepted. 
        lr is useless if mode selected is 'date'.

        Left sends common parts of left list. 
        Right sends common parts of right list.
        
        Both of them will have same dates but either of the list could have time values as well.
        
        Example:
            left_list object  |   right_list object
            2023-08-31  |   2023-08-31 08:50:00
        
        left would return the list with date alone.
        right would return the list with datetime. It could be either. 
        No rule on which should be what.

    """
    lr = kwargs.get('lr', 'left')
    mode = kwargs.get('mode','datetime')

    date1 = date_list1
    date2 = date_list2
    if all(type(x) is datetime.datetime for x in date_list1)\
        and all(type(x) is datetime.datetime for x in date_list2):
        pass
    else:
        date1 = date_returner(date_list1)
        date2 = date_returner(date_list2)
    

    if mode == 'datetime':
        date1.sort()
        date2.sort()
        len1 = date1.__len__()
        len2 = date2.__len__()

        common_dates_left = []
        common_dates_right = []
        i, j = 0, 0
        try:
            while (i < len1 and j < len2):
                if date1[i].date() > date2[j].date():
                    j += 1
                elif date1[i].date() < date2[j].date():
                    i += 1
                elif date1[i].date() == date2[j].date():
                    common_dates_left.append(date1[i])
                    common_dates_right.append(date2[j])
                    i += 1
                    j += 1
                else:
                    print('Check the datetime lists passed to the function')
                    break
        except Exception:
            print('Error at')
            print('i=',i,' , j=', j)
            print('date1:', date1[i].date())
            print('date2:', date2[j].date())
        
        if lr == 'left':
            return np.array(common_dates_left)
        elif lr == 'right':
            return np.array(common_dates_right)
        
    elif mode == 'date':
        date1 = [x.date() for x in date1]
        date2 = [x.date() for x in date2]
        
        date_set1 = set(date1)
        date_set2 = set(date2)

        common_dates = list(set.intersection(date_set1, date_set2))
        common_dates.sort()
        return np.array(common_dates)


def simpleJulianToDateTime(julian_date: float, **kwargs):
    """Reduced Julian Date

    JD - 2400000
    
    12:00 November 16, 1858	(i.e. afternoon of 16-Nov-1858) -> 2400000   
    
    Suitable for years after 1858.
    
    --------

    References
    ----------
    https://en.wikipedia.org/wiki/Julian_day

    Kwargs
    ------
    include_time: bool
        False/Default -> Returns only date.
        True -> Returns date and time.
    """
    
    reduced_julian_date = julian_date - 2400000
    ref_date = datetime.datetime.strptime("1858-11-16 12:00:00", "%Y-%m-%d %H:%M:%S")
    reg_date = ref_date + datetime.datetime.timedelta(days=reduced_julian_date)
    
    include_time = kwargs.get("include_time", False)

    if include_time:
        return reg_date
    else:
        return reg_date.date()





