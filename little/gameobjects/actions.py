from gameobject import get_object_by_id
from gameobject import get_room_from_lifeform
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
    # if weapon(s) equipped, use their MDMG and PDMG stats
    if right_hand or left_hand:
        for hand in [right_hand, left_hand]:
            if hand:
                if hand.stats.MDMG:
                    source_mdmg += hand.stats.MDMG
                if hand.stats.PDMG:
                    source_pdmg += hand.stats.PDMG
    else:
        # if no weapon equipped just use STR stat
        source_pdmg = source.stats.STR

    target_pdef = target.stats.PDEF
    target_mdef = target.stats.MDEF

    pdiff = source_pdmg - target_pdef if source_pdmg - target_pdef >= 0 else 0
    mdiff = source_mdmg - target_mdef if source_mdmg - target_mdef >= 0 else 0

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
        room = get_room_from_lifeform(target.id)
        room.remove_gameobject_by_id(target.id)
    # TODO: drops

