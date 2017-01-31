from gameobject import get_object_by_id
import random


def basic_attack(source, target):
    """
    source and target must be gameobject id's
    """
    source = get_object_by_id(source)
    target = get_object_by_id(target)
    right_hand = source.inventory.equip_slots['right_hand']
    left_hand = source.inventory.equip_slots['left_hand']

    source_pdmg = 0
    source_mdmg = 0
    for hand in [right_hand, left_hand]:
        if hand:
            if hand.stats.MDMG:
                source_mdmg += hand.stats.MDMG
            if hand.stats.PDMG:
                source_pdmg += hand.stats.PDMG

    target_pdef = target.stats.PDEF
    target_mdef = target.stats.MDEF

    pdiff = source_pdmg - target_pdef
    mdiff = source_mdmg - target_mdef
    if pdiff < 0:
        pdiff = 0
    if mdiff < 0:
        mdiff = 0

    source_attack_rating = (source.stats.STR * pdiff) + (source.stats.MND * mdiff)

    # Attacks must do minimum damage of 1
    if source_attack_rating <= 0:
        source_attack_rating = 1

    print('DEBUG: Total Damage: {0}'.format(source_attack_rating))
    do_damage(target.id, source_attack_rating)


def do_damage(target, amount):
    target = get_object_by_id(target)
    target.stats.HP -= amount
    if target.stats.HP <= 0:
        target.destroyed = True

