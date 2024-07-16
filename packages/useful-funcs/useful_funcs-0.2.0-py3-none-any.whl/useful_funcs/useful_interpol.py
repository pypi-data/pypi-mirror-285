from numpy import array

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
            x_matrix = array([(x2 - x), (x - x1)])
            y_matrix = array([(y2 - y), (y - y1)])
            f_matrix = array([[fx1y1, fx1y2],
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
    pass

# x, y = 20.2, 14.5
# x1, x2 = 20, 21
# y1, y2 = 14, 15
# fx1y1, fx1y2 = 91, 210
# fx2y1, fx2y2 = 162, 95
# print(interpolated_value(x, y, x1, x2, y1, y2, fx1y1, fx1y2, fx2y1, fx2y2))