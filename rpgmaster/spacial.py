import math


def vec_direction(x1, y1, x2, y2):
    """
    Returns the direction (in degrees) between two sets of co-ordinates
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return: angle in degrees
    """
    h_change = x2 - x1
    v_change = y2 - y1
    # TODO : HANDLE divide by 0 error
    return math.degrees(math.atan(float(v_change)/float(h_change)))


def vec_distance(x1, y1, x2, y2):
    """
    Returns the magnitude (length) of a vector between two sets of co-ordinates
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return: exact distance (float)
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)