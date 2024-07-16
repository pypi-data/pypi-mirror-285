import calendar
from datetime import datetime, timedelta

def datesList(year: int, **kwargs):
    '''Returns a list containing of all the dates in string format "yyyy_mm_dd"

    --------
    Notes
    -----
    kwargs:
    sep: char
        The separating character. ex: '/' -> "yyyy/mm/dd"
    month: int
        If provided, returns the dates of that month alone
    
    '''
    sep = kwargs.get("sep", "_")
    month = kwargs.get("month", False)

    dates = []
    if month:
        date = calendar.monthrange(year, month)
        
        for i in range(date[1]):
            dates.append(f"{year:04d}{sep}{month:02d}{sep}{(i+1):02d}")
    else:
        for month_num in range(1,13):
            date = calendar.monthrange(year, month_num)
            for i in range(date[1]):
                dates.append(f"{year:04d}{sep}{month_num:02d}{sep}{(i+1):02d}")
    
    return dates


def calendar_months_abbr(f):
    """Returns list of Calendar months from Jan to Dec
    which is modified based on the function f applied.

    --------
    Usage
    -----
    Example 1: calendar_months_abbr(lambda x: str.upper(x))
        This would return the names in capitals like JAN, ... , DEC
    
    """
    return [f(x) for x in list(calendar.month_abbr)[1:]]


def julianToCalendar(julian_date: int):
    # Refer wikipedia
    # https://en.wikipedia.org/wiki/Julian_day
    julian_year = -4712
    julian_days = 0

    while julian_days < julian_date:
        if calendar.isleap(julian_year):
            if julian_date - julian_days < 366:
                day_num = str(julian_date - julian_days)
                day_num.rjust(3 + len(day_num), '0')
                return (datetime.strptime(str(julian_year) + "-" + day_num, "%Y-%j") - timedelta(days=36.5))
            else:
                julian_days += 366    
        else:
            if julian_date - julian_days < 365:
                day_num = str(julian_date - julian_days)
                day_num.rjust(3 + len(day_num), '0')
                return (datetime.strptime(str(julian_year) + "-" + day_num, "%Y-%j") - timedelta(days=36.5))
            else:
                julian_days += 365
        
        julian_year += 1

        if julian_days == julian_date:
            break


def daysInEachMonth(leap_year=False):
    if leap_year:
        return [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        return [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]



# Examples
# import calendar
# from datetime import datetime, timedelta
# julian_date = str(2400000)
# print("Julian Date = " +julian_date )
# import datetime

# def datestdtojd (stddate):
#     fmt='%Y-%m-%d'
#     sdtdate = datetime.datetime.strptime(stddate, fmt)
#     sdtdate = sdtdate.timetuple()
#     jdate = sdtdate.tm_yday
#     return(jdate)

# date = datestdtojd ('1858-11-16')
# print(date)

# def jdtodatestd (jdate):
#     fmt = '%Y-%m-%d'
#     datestd = datetime.datetime.strptime(jdate, fmt).date()
#     return(datestd)

# normaldate = jdtodatestd('2400000')
# print("Final date is "+normaldate)

