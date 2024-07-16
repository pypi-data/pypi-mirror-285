import calendar
import datetime

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


def calendar_months_abbr(f) -> list[str]:
    """Returns list of Calendar months from Jan to Dec
    which is modified based on the function f applied.

    --------
    Usage
    -----
    Example: 
        >>> calendar_months_abbr(lambda x: str.upper(x))
        This would return the names in capitals like JAN, ... , DEC

    More examples:
        >>> f = lambda x: str(x)[0]
        >>> print(calendar_months_abbr(f))
    ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

        >>> f = lambda x: str.upper(x)
        >>> print(calendar_months_abbr(f))
    ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

        >>> f = lambda x: str.lower(x)
        >>> print(calendar_months_abbr(f))
    ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    """
    return [f(x) for x in list(calendar.month_abbr)[1:]]


def julianToCalendar(julian_date: int):
    """

    Usage
    -----
    Examples:
        >>> julian_date = str(julianToCalendar(2400000))
        >>> print("Julian Date = " +julian_date )
    Julian Date = 1858-11-16 12:00:00

        >>> julian_date = str(julianToCalendar(2500010))
        >>> print("Julian Date = " +julian_date )
    Julian Date = 2132-09-10 12:00:00

    
    Notes
    -----
    https://en.wikipedia.org/wiki/Julian_day
    """
    
    julian_year = -4712
    julian_days = 0

    while julian_days < julian_date:
        if calendar.isleap(julian_year):
            if julian_date - julian_days < 366:
                day_num = str(julian_date - julian_days)
                day_num.rjust(3 + len(day_num), '0')
                return (datetime.datetime.strptime(str(julian_year) + "-" + day_num, "%Y-%j") - datetime.timedelta(days=36.5))
            else:
                julian_days += 366    
        else:
            if julian_date - julian_days < 365:
                day_num = str(julian_date - julian_days)
                day_num.rjust(3 + len(day_num), '0')
                return (datetime.datetime.strptime(str(julian_year) + "-" + day_num, "%Y-%j") - datetime.timedelta(days=36.5))
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




def datestdtojd(stddate: str, fmt: str="%Y-%m-%d") -> int:
    sdtdate = datetime.datetime.strptime(stddate, fmt)
    sdtdate = sdtdate.timetuple()
    jdate = sdtdate.tm_yday
    return(jdate)

date = datestdtojd ('1858-11-16')
print(date)

# def jdtodatestd (jdate):
#     fmt = '%Y-%m-%d'
#     datestd = datetime.datetime.strptime(jdate, fmt).date()
#     return(datestd)

# normaldate = jdtodatestd('2400000')
# print("Final date is "+normaldate)

