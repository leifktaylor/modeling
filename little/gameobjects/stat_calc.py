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
