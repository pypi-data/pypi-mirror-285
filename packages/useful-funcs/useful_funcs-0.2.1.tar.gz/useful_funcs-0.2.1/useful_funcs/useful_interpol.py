import numpy
from typing import Tuple

'''
Imagine points on map are like this
(x1, y2)         (x2, y2)
(x1, y1)         (x2, y1)

First we do linear interpolation in x-direction
at y1 value and at y2 value.
f(x, y1) = f(x1,y1)[(x2 - x)/(x2 - x1)] + f(x2,y1)[(x - x1)/(x2 - x1)]
f(x, y2) = f(x1,y2)[(x2 - x)/(x2 - x1)] + f(x2,y2)[(x - x1)/(x2 - x1)]


Now we perform another linear interpolation on top of this function
in the y direction
f(x, y) =  f(x, y1)[(y2 - y)/(y2 - y1)] + f(x, y2)[(y - y1)/(y2 - y1)]
Upon expansion of this, we get
f(x, y) 
                                              | f(x1, y1)   f(x1, y2) | | (y2 - y) | 
= 1/(x2 - x1)(y2 - y1) | (x2 - x)  (x - x1) | | f(x2, y1)   f(x2, y2) | | (y - y1) |





An alternate way of obtaining interpolation would be by 
the below method of polynomial fit.
| 1    x1    y1    x1y1 | | a00 |    | f(x1,y1) |
| 1    x1    y2    x1y2 | | a10 | =  | f(x1,y2) |
| 1    x2    y1    x2y1 | | a01 |    | f(x2,y1) |
| 1    x2    y2    x2y2 | | a11 |    | f(x2,y2) |

Solving we get,
| a00 |                        | x2y2   -x2y1   -x1y2   x1y1 | | f(x1,y1) |
| a10 | = 1/(x2 - x1)(y2 - y1) | -y2     y1      y2     -y1  | | f(x1,y2) |
| a01 |                        | -x2     x2      x1     -x1  | | f(x2,y1) |
| a11 |                        |  1      -1      -1      1   | | f(x2,y2) |

f(x, y) ~ a00 + a10x + a01y + a11xy
'''


def interpolated_value(x, y, x1, x2, y1, y2, fx1y1, fx1y2, fx2y1, fx2y2) -> float:
    '''
    Calculates the interpolated value inside a rectangle of 4 boundary values.
     Can be used for unstructured rectangular grids as well.
      This is slower than the fast_interpolator method available in this module.
    ----------
    Parameters
    ----------
    x: x-coordinate of the required point
    y: y-coordinate of the required point
    x1: left x-coordinate of known value point
    x2: right x-coordinate of known value point
    y1: lower y-coordinate of known value point
    y2: upper y-coordinate of known value point
    fx1y1: lower-left value
    fx1y2: upper-left value
    fx2y1: lower-right value
    fx2y2: upper-right value

    Returns
    -------
    interpolated_value: float
        The required bilinearly interpolated value

    Raises
    ------
    AssertionError
    ZeroDivisionError
    '''
    try:
        if x1 != x2 and y1 != y2:
            coeff = (1 / ((x2 - x1)*(y2 - y1)))
            x_matrix = numpy.array([(x2 - x), (x - x1)])
            y_matrix = numpy.array([(y2 - y), (y - y1)])
            f_matrix = numpy.array([[fx1y1, fx1y2],
                                [fx2y1, fx2y2]])
            fy_matrix = f_matrix.dot(y_matrix)
            xfy_matrix = x_matrix.dot(fy_matrix)
            interpol_value = coeff * xfy_matrix
                
            # print('coeff=', coeff, '\nx_matrix=', x_matrix, \
            # '\ny_matrix=', y_matrix,'\nf_matrix=', f_matrix, \
            # '\nxfy=', xfy_matrix,'\ninterpol_value=', interpol_value)

            return interpol_value
        elif y1 == y2 and x1 != x2:
            if fx1y1 == fx1y2 and fx2y1 == fx2y2:
                interpol_value = (fx1y1 * ((x2 - x)/(x2 - x1))) + (fx2y1 * ((x - x1)/(x2 - x1)))
                return interpol_value
            print("Not right")
            raise AssertionError
        elif x1 == x2 and y1 != y2:
            if fx1y1 == fx2y1 and fx1y2 == fx2y2:
                interpol_value = (fx1y1 * ((y - y1)/(y2 - y1))) + (fx1y2 * ((y2 - y)/(y2 - y1)))
                return interpol_value
            print("Not right")
            raise AssertionError
        elif x1 == x2 and y1 == y2:
            if fx1y1 == fx2y1 and fx1y1 == fx1y2 and fx1y1 == fx2y2:
                interpol_value = fx1y1
                return interpol_value
            print("Not right")
            raise AssertionError
        else:
            print("Not right")
            raise AssertionError
    except ZeroDivisionError:
        print(f"Zero Division Error has occured with the following values")
        print(f"x = {x}, y = {y}, \nx1 = {x1}, x2 = {x2}, \ny1 = {y1}, y2 = {y2}")
        print(f"fx1y1 = {fx1y1}, fx1y2 = {fx1y2}, \nfx2y1 = {fx2y1}, fx2y2 = {fx2y2}")
        raise ZeroDivisionError

def interpolate_to_nearest_neighbour(x, y, x1, x2, y1, y2, fx1y1, fx1y2, fx2y1, fx2y2):
    """
    Under construction!
    """
    pass

# # Example implementation of above code
# x, y = 20.2, 14.5
# x1, x2 = 20, 21
# y1, y2 = 14, 15
# fx1y1, fx1y2 = 91, 210
# fx2y1, fx2y2 = 162, 95
# print(interpolated_value(x, y, x1, x2, y1, y2, fx1y1, fx1y2, fx2y1, fx2y2))

def closest_indices_linear_interp(new_x:numpy.ndarray, old_x:numpy.ndarray) -> Tuple[numpy.ndarray, numpy.ndarray,
                                                                            numpy.ndarray, numpy.ndarray]:
    """
    Used for linear interpolation in 1 or more than 1 dimensions.

    --------
    Parameters
    ----------
    new_x: numpy.ndarray
            Array of 1 dimension containing the new locations where the old values 
             need to be interpolated.

    old_x: numpy.ndarray
            Array of 1 dimension containing the old locations where the data is originally defined.

    Returns
    -------
    _left: numpy.ndarray
            Array of 1 dimension containing the multiplication factors by which the left points of old data
             corresponding to the new data should be multiplied and added to the similar array obtained from
              _rght array.

    _rght: numpy.ndarray
            Array of 1 dimension containing the multiplication factors by which the right points of old data
             corresponding to the new data should be multiplied and added to the similar array obtained from
              _left array.
            
    _left_indices: numpy.ndarray
            Array of 1 dimension containing the indices of the points left of old data
             corresponding to the new data which should be multiplied and added to the points at the 
              indices obtained from _right_indices array.

    _right_indices: numpy.ndarray
            Array of 1 dimension containing the indices of the points right of old data
             corresponding to the new data which should be multiplied and added to the points at the 
              indices obtained from _left_indices array.

    """
    if (new_x[0] < old_x[0]) or (new_x[-1] > old_x[-1]):
        raise AssertionError("Incompatible arrays. Elements of a should be within x")

    _left_indices = numpy.empty(new_x.size, dtype=int)
    _right_indices = numpy.empty(new_x.size, dtype=int)
    _left = numpy.empty(new_x.size, dtype=float)
    _rght = numpy.empty(new_x.size, dtype=float)

    _left_index = 0
    _new_ele_index = 0
    while (_new_ele_index < new_x.size):
        _a_ith = new_x[_new_ele_index]
        if (old_x[_left_index] == new_x[_new_ele_index]):
            _left[_new_ele_index] = 1
            _rght[_new_ele_index] = 0
            _left_indices[_new_ele_index] = _left_index
            _right_indices[_new_ele_index] = _left_index
            _new_ele_index += 1
        elif (old_x[_left_index+1] > _a_ith) and (old_x[_left_index] < _a_ith):
            _left[_new_ele_index] = (old_x[_left_index + 1] - new_x[_new_ele_index]) / (old_x[_left_index + 1] - old_x[_left_index])
            _rght[_new_ele_index] = 1 - _left[_new_ele_index]
            _left_indices[_new_ele_index] = _left_index
            _right_indices[_new_ele_index] = _left_index + 1
            _new_ele_index += 1
        else:
            _left_index += 1

    return _left, _rght, _left_indices, _right_indices


def closest_indices_nn_interp(new_x:numpy.ndarray, old_x:numpy.ndarray) -> Tuple[numpy.ndarray, numpy.ndarray,
                                                                            numpy.ndarray, numpy.ndarray]:
    """
    Used for Nearest Neighbour Interpolation

    --------
    Parameters
    ----------
    new_x: numpy.ndarray
            Array of 1 dimension containing the new locations where the old values 
             need to be interpolated.

    old_x: numpy.ndarray
            Array of 1 dimension containing the old locations where the data is originally defined.

    Returns
    -------
    _left: numpy.ndarray
            Array of 1 dimension containing the multiplication factors by which the left points of old data
             corresponding to the new data should be multiplied and added to the similar array obtained from
              _rght array.

    _rght: numpy.ndarray
            Array of 1 dimension containing the multiplication factors by which the right points of old data
             corresponding to the new data should be multiplied and added to the similar array obtained from
              _left array.
            
    _left_indices: numpy.ndarray
            Array of 1 dimension containing the indices of the points left of old data
             corresponding to the new data which should be multiplied and added to the points at the 
              indices obtained from _right_indices array.

    _right_indices: numpy.ndarray
            Array of 1 dimension containing the indices of the points right of old data
             corresponding to the new data which should be multiplied and added to the points at the 
              indices obtained from _left_indices array.

    """
    if (new_x[0] < old_x[0]) or (new_x[-1] > old_x[-1]):
        raise AssertionError("Incompatible arrays. Elements of a should be within x")

    _left_indices = numpy.empty(new_x.size, dtype=int)
    _right_indices = numpy.empty(new_x.size, dtype=int)
    _left = numpy.empty(new_x.size, dtype=float)
    _rght = numpy.empty(new_x.size, dtype=float)

    _left_index = 0
    _new_ele_index = 0
    while (_new_ele_index < new_x.size):
        _a_ith = new_x[_new_ele_index]
        if (old_x[_left_index] == new_x[_new_ele_index]):
            _left[_new_ele_index] = 1
            _rght[_new_ele_index] = 0
            _left_indices[_new_ele_index] = _left_index
            _right_indices[_new_ele_index] = _left_index
            _new_ele_index += 1
        elif ((old_x[_left_index+1] > _a_ith) and (old_x[_left_index+1] - _a_ith) > (_a_ith - old_x[_left_index])):
            _left[_new_ele_index] = 1
            _rght[_new_ele_index] = 0
            _left_indices[_new_ele_index] = _left_index
            _right_indices[_new_ele_index] = _left_index + 1
            _new_ele_index += 1
        elif ((old_x[_left_index+1] > _a_ith) and (old_x[_left_index+1] - _a_ith) < (_a_ith - old_x[_left_index])):
            _left[_new_ele_index] = 0
            _rght[_new_ele_index] = 1
            _left_indices[_new_ele_index] = _left_index
            _right_indices[_new_ele_index] = _left_index + 1
            _new_ele_index += 1
        else:
            _left_index += 1

    return _left, _rght, _left_indices, _right_indices





def fast_interpolator(old_vals:numpy.ndarray,
                 new_lons:numpy.ndarray, old_lons:numpy.ndarray,
                 new_lats:numpy.ndarray, old_lats:numpy.ndarray,
                 new_deps:numpy.ndarray, old_deps:numpy.ndarray,
                 dim:str = "1dnt", kind:str="lin") -> numpy.ndarray:
    """ Interpolates old_vals (Old values on old grid) to _new_vals (New values on new grid)
    and returns the _new_vals.

    --------

    Useful for evenly spaced grids only! DO NOT USE FOR UNSTRUCTURED GRIDS!

    --------
    Parameters
    ----------
    old_vals
    new_lons
    old_lons
    new_lats
    old_lats
    new_deps
    old_deps
    dim


    Please see that the shape of the old_vals is as follows corresponding to the dim option.

    "1dnt" = (lon)

    "1dwt" = (time, lon)

    "2dnt" = (lat, lon)

    "2dwt" = (time, lat, lon)

    "3dnt" = (depth, lat, lon)

    "3dwt" = (time, depth, lat, lon)

    Please select the required type of interpolation by choosing the option kind

    "lin" = Linearly interpolates in various dimensions

    "nn" = Nearest Neighbour Interpolation

    --------
    Returns
    -------
    _new_vals: numpy.ndarray
        Interpolated values.
    """
    if kind == "lin":
        closest_indices = closest_indices_linear_interp
    else:
        closest_indices = closest_indices_nn_interp


    if (dim == "1dnt"):
        assert (len(old_vals.shape) == 1), "Shape of old values is not correct"
        lon_left, lon_rght, lon_left_indices, lon_rght_indices = closest_indices(new_lons, old_lons)

        _new_vals = (old_vals[lon_left_indices] * lon_left[:]) + (old_vals[lon_rght_indices] * lon_rght[:])

        return _new_vals

    elif (dim == "1dwt"):
        assert (len(old_vals.shape) == 2), "Shape of old values is not correct"
        lon_left, lon_rght, lon_left_indices, lon_rght_indices = closest_indices(new_lons, old_lons)

        _new_vals = (old_vals[:, lon_left_indices] * lon_left[numpy.newaxis, :]) + (old_vals[:, lon_rght_indices] * lon_rght[numpy.newaxis, :])

        return _new_vals

    elif (dim == "2dnt") and (new_lats is not None) and (new_lons is not None):
        assert (len(old_vals.shape) == 2), "Shape of old values is not correct"
        lon_left, lon_rght, lon_left_indices, lon_rght_indices = closest_indices(new_lons, old_lons)
        lat_left, lat_rght, lat_left_indices, lat_rght_indices = closest_indices(new_lats, old_lats)

        _new_vals = (old_vals[:, lon_left_indices] * lon_left[numpy.newaxis, :]) + (old_vals[:, lon_rght_indices] * lon_rght[numpy.newaxis, :])
        _new_vals = (_new_vals[lat_left_indices, :] * lat_left[:, numpy.newaxis]) + (_new_vals[lat_rght_indices, :] * lat_rght[:, numpy.newaxis])

        return _new_vals

    elif (dim == "2dwt") and (new_lats is not None) and (new_lons is not None):
        assert (len(old_vals.shape) == 3), "Shape of old values is not correct"
        lon_left, lon_rght, lon_left_indices, lon_rght_indices = closest_indices(new_lons, old_lons)
        lat_left, lat_rght, lat_left_indices, lat_rght_indices = closest_indices(new_lats, old_lats)

        _new_vals = (old_vals[:, :, lon_left_indices] * lon_left[numpy.newaxis, numpy.newaxis, :]) + (old_vals[:, :, lon_rght_indices] * lon_rght[numpy.newaxis, numpy.newaxis, :])
        _new_vals = (_new_vals[:, lat_left_indices, :] * lat_left[numpy.newaxis, :, numpy.newaxis]) + (_new_vals[:, lat_rght_indices, :] * lat_rght[numpy.newaxis, :, numpy.newaxis])

        return _new_vals

    elif (dim == "3dnt") and (new_deps is not None) and (new_lats is not None) and (new_lons is not None):
        assert (len(old_vals.shape) == 3), "Shape of old values is not correct"
        lon_left, lon_rght, lon_left_indices, lon_rght_indices = closest_indices(new_lons, old_lons)
        lat_left, lat_rght, lat_left_indices, lat_rght_indices = closest_indices(new_lats, old_lats)
        dep_left, dep_rght, dep_left_indices, dep_rght_indices = closest_indices(new_deps, old_deps)

        _new_vals = (old_vals[:, :, lon_left_indices] * lon_left[numpy.newaxis, numpy.newaxis, :]) + (old_vals[:, :, lon_rght_indices] * lon_rght[numpy.newaxis, numpy.newaxis, :])
        _new_vals = (_new_vals[:, lat_left_indices, :] * lat_left[numpy.newaxis, :, numpy.newaxis]) + (_new_vals[:, lat_rght_indices, :] * lat_rght[numpy.newaxis, :, numpy.newaxis])
        _new_vals = (_new_vals[dep_left_indices, :, :] * dep_left[:, numpy.newaxis, numpy.newaxis]) + (_new_vals[dep_rght_indices, :, :] * dep_rght[:, numpy.newaxis, numpy.newaxis])

        return _new_vals

    elif (dim == "3dwt") and (new_deps is not None) and (new_lats is not None) and (new_lons is not None):
        assert (len(old_vals.shape) == 4), "Shape of old values is not correct"
        lon_left, lon_rght, lon_left_indices, lon_rght_indices = closest_indices(new_lons, old_lons)
        lat_left, lat_rght, lat_left_indices, lat_rght_indices = closest_indices(new_lats, old_lats)
        dep_left, dep_rght, dep_left_indices, dep_rght_indices = closest_indices(new_deps, old_deps)

        _new_vals = (old_vals[:, :, :, lon_left_indices] * lon_left[numpy.newaxis, numpy.newaxis, numpy.newaxis, :]) + (old_vals[:, :, :, lon_rght_indices] * lon_rght[numpy.newaxis, numpy.newaxis, numpy.newaxis, :])
        _new_vals = (_new_vals[:, :, lat_left_indices, :] * lat_left[numpy.newaxis, numpy.newaxis, :, numpy.newaxis]) + (_new_vals[:, :, lat_rght_indices, :] * lat_rght[numpy.newaxis, numpy.newaxis, :, numpy.newaxis])
        _new_vals = (_new_vals[:, dep_left_indices, :, :] * dep_left[numpy.newaxis, :, numpy.newaxis, numpy.newaxis]) + (_new_vals[:, dep_rght_indices, :, :] * dep_rght[numpy.newaxis, :, numpy.newaxis, numpy.newaxis])

        return _new_vals
    
    # # # UNDER CONSTRUCTION! 
    # # # Need to change new_deps, old_deps in tim_left, tim_rght, etc. initialization
    # elif (dim == "4dit") and (new_deps is not None) and (new_lats is not None) and (new_lons is not None):
    #     assert (len(old_vals.shape) == 4), "Shape of old values is not correct"
    #     lon_left, lon_rght, lon_left_indices, lon_rght_indices = closest_indices(new_lons, old_lons)
    #     lat_left, lat_rght, lat_left_indices, lat_rght_indices = closest_indices(new_lats, old_lats)
    #     dep_left, dep_rght, dep_left_indices, dep_rght_indices = closest_indices(new_deps, old_deps)
    #     tim_left, tim_rght, tim_left_indices, tim_rght_indices = closest_indices(new_deps, old_deps)

    #     _new_vals = (old_vals[:, :, :, lon_left_indices] * lon_left[numpy.newaxis, numpy.newaxis, numpy.newaxis, :]) + (old_vals[:, :, :, lon_rght_indices] * lon_rght[numpy.newaxis, numpy.newaxis, numpy.newaxis, :])
    #     _new_vals = (_new_vals[:, :, lat_left_indices, :] * lat_left[numpy.newaxis, numpy.newaxis, :, numpy.newaxis]) + (_new_vals[:, :, lat_rght_indices, :] * lat_rght[numpy.newaxis, numpy.newaxis, :, numpy.newaxis])
    #     _new_vals = (_new_vals[:, dep_left_indices, :, :] * dep_left[numpy.newaxis, :, numpy.newaxis, numpy.newaxis]) + (_new_vals[:, dep_rght_indices, :, :] * dep_rght[numpy.newaxis, :, numpy.newaxis, numpy.newaxis])
    #     _new_vals = (_new_vals[tim_left_indices, :, :, :] * tim_left[:, numpy.newaxis, numpy.newaxis, numpy.newaxis]) + (_new_vals[tim_rght_indices, :, :, :] * tim_rght[:, numpy.newaxis, numpy.newaxis, numpy.newaxis])
    #     return _new_vals

    else:
        raise AssertionError("Something did not work properly. Check all details again around interpolation")



