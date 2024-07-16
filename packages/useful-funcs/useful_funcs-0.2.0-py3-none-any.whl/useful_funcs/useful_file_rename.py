import os
import datetime
import time


def renameBasedOnDate(path:str) -> int:
    """Renames all the files in a folder which are earlier named in the
    form yyyy_mm_dd and attaches a count number for each date.
    
    --------
    Parameters
    ----------
    path: str
        Full path of the folder whose files have to be renamed.

    Returns
    -------
    file_count: int
        Number of files which have been renamed.
    """
    date_prev = ""
    file_count = 0
    count = 1
    for file in os.listdir(path):
        if date_prev == file[:10]:
            count += 1
            file_new_name = f"{file[:10].replace('-', '_')}_{count:03d}.{file.split('.')[-1]}"
            os.rename(os.path.join(path, file), os.path.join(path, file_new_name))
            file_count += 1
        else:
            date_prev = file[:10]
            count = 1
            file_new_name = f"{file[:10].replace('-', '_')}_{count:03d}.{file.split('.')[-1]}"
            os.rename(os.path.join(path, file), os.path.join(path, file_new_name))
            file_count += 1
    
    return file_count


def renameBasedOnModified(path:str) -> int:
    """Renames all the files in the folder whose path is provided 
    to the date on which they were last modified. Attaches a unique
    file_number to each file_name at the end to prevent files modified
    on the same date and time from mixing up.

    --------
    Parameters
    ----------
    path: str
        Full path of the folder whose files have to be renamed.

    Returns
    -------
    file_count: int
        Number of files which have been renamed.
    """
    file_count = 0
    for file in os.listdir(path):
        file = str(file)
        ctime = time.ctime(os.path.getmtime(f"{path}/{file}"))
        date1 = str(datetime.datetime.strptime(ctime, "%a %b %d %H:%M:%S %Y")).replace("-","_").replace(":","_").replace(" ", "_")
        file_new_name = f"{date1}_{file_count:03d}.{file.split('.')[-1]}"
        os.rename(os.path.join(path, file), os.path.join(path, file_new_name))
        file_count += 1

    return file_count



