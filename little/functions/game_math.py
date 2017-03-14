import math


def negpos(number):
    """Gives direction of vector"""
    if number < 0:
        return -1
    elif number > 0:
        return 1
    else:
        return 0


def map_pos(game, pos):
    """ Converts screen position to map position """
    zoom = game.map_layer.zoom
    offset = game.map_layer.view_rect.topleft
    return (pos[0] / zoom) + offset[0], (pos[1] / zoom) + offset[1]


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


def point_distance(coords1, coords2):
    """ Distance between two points, should be tuples or lists, Returns a float """
    x, y = coords1
    xx, yy = coords2
    distances = (xx - x)**2 + (yy - y)**2
    return math.sqrt(distances)


def calc_stat(stat, tier1=50, tier2=70, denom1=1.5, denom2=2):
    """
    Return adjusted stat (adds softcaps at two tiers, and adjusts them with given a denominator)
    """
    softcap2, softcap1 = 0, 0
    if stat >= tier2:
            softcap2 = stat - 70
    if stat >= tier1:
        softcap1 = stat - 50 - softcap2
    adj_stat = (stat - softcap1 - softcap2) + (softcap1 / denom1) + (softcap2 / denom2)
    return adj_stat
