import math


def negpos(number):
    """Gives direction of vector"""
    if number < 0:
        return -1
    elif number > 0:
        return 1
    else:
        return 0


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def point_distance(coords1, coords2):
    """ Distance between two points, should be tuples or lists, Returns a float """
    x, y = coords1
    xx, yy = coords2
    distances = (xx - x)**2 + (yy - y)**2
    return math.sqrt(distances)