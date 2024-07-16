'''
    This code is for handling operations related to datetime
    such as comparison, time difference, etc.
'''
__author__ = "Surya Datta Sudhakar"
__copyright__ = "Copyright 2023, INCOIS"

import datetime

'''
https://docs.python.org/3/library/datetime.html

d = date(2005, 7, 14)
t = time(12, 30)
datetime.combine(d, t)

dt1 = datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0)
dt2 = datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M")

MINYEAR <= year <= MAXYEAR,
1 <= month <= 12,
1 <= day <= number of days in the given month and year,
0 <= hour < 24,
0 <= minute < 60,
0 <= second < 60,
0 <= microsecond < 1000000,

'''
def datetime_compare(date1: datetime.datetime, date2: datetime.datetime) -> int:
    '''
        date1 gives output as YYYY-mm-dd HH:MM:SS
        <class 'datetime.datetime'>

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




