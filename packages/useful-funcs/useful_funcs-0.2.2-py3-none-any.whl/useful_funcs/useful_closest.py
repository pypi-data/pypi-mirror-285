import numpy as np

def closest(points_list: np.ndarray, K: float, left_right: int):
    '''Used to find the closest point from a given list of points to the number provided as K.

    --------

    Parameters
    ----------
    points_list: np.ndarray
        Array which contains the list of all points

    K: float
        the point for which we are trying to find the closest value from the above points_list

    left_right: int 
        Defines how you want to get the closest value.
        Use the following values for left_right

        For left closest: -1
        For closest: 0
        For right closest: 1

    Returns
    -------
    closest_value: float
    '''
    list_points = (np.asarray(points_list)).copy()
    list_points.sort()
    index = (np.abs(list_points - K)).argmin()

    if left_right == -1:
        if K - list_points[index] > 0: 
            return float(list_points[index])
        elif K - list_points[index] < 0:
            return float(list_points[index-1])
        elif K - list_points[index] == 0:
            return float(list_points[index])
    elif left_right == 1:
        if K - list_points[index] > 0: 
            return float(list_points[index+1])
        elif K - list_points[index] < 0:
            return float(list_points[index])
        elif K - list_points[index] == 0:
            return float(list_points[index])
    elif left_right == 0:
        return float(list_points[index])


def closest_index(points_list: np.ndarray, K: float, left_right: int):
    '''Used to find the index of the closest point from a given list of points to the number provided as K.

    --------

    Parameters
    ----------
    points_list: np.ndarray
        Array which contains the list of all points

    K: float
        the point for which we are trying to find the closest value from the above points_list

    left_right: int 
        Defines how you want to get the closest value.
        Use the following values for left_right

        For left closest: -1
        For closest: 0
        For right closest: 1

    Returns
    -------
    closest_value: int
        index of the point which is closest to point K as required
    '''
    list_points = (np.asarray(points_list)).copy()
    list_points.sort()
    index = (np.abs(list_points - K)).argmin()

    if left_right == -1:
        if K - list_points[index] > 0: 
            return int(index)
        elif K - list_points[index] < 0:
            return int(index-1)
        elif K - list_points[index] == 0:
            return int(index)
    elif left_right == 1:
        if K - list_points[index] > 0:
            if index == (len(list_points)-1):
                if K - list_points[index] < 1e-10:
                    return int(index)
                else:
                    raise AssertionError
            else:
                return int(index+1)   
        elif K - list_points[index] < 0:
            return int(index)
        elif K - list_points[index] == 0:
            return int(index)
    elif left_right == 0:
        return int(index)


def isCloseToLine(point: np.ndarray, linePoints, threshold) -> bool:
    '''Takes a point and compares it to a set of points on distance. 
    Returns True if it is within the threshold distance to any of the points, else False.
    
    --------
    Parameters
    ----------
    point: np.ndarray
        An array containing x-coordinate and y-coordinate of 1 point.
    linePoints: np.ndarray
        A 2D array containing x and y coordinates of points of a line.
    threshold: float
        A value of radius within which lies our region of interest
    
    Returns
    -------
    True/False
    '''
    for linePoint in linePoints:
        euclidean_distance = (linePoint[0] - point[0])**2 + (linePoint[1] - point[1])**2
        if  euclidean_distance <= threshold:
            return True
    return False