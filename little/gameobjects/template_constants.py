"""
Variables to be parsed for in .itm, .lfm, .sts, and .spl templates.
"""

item_classes = {'apparel': 'ItemApparel', 'ingredient': 'ItemIngredient', 'misc': 'ItemMisc',
                'potion': 'ItemPotion', 'weapon': 'ItemWeapon', 'prop': 'ItemProp'}

possible_stats = ['name', 'item_type', 'description', 'equippable_slot', 'OnHit', 'Passive',
                  'HP', 'MP', 'STR', 'MND', 'SPD', 'STA', 'PDEF', 'MDEF', 'MDMG', 'PDMG', 'weight',
                  'OnUse', 'uses', 'OnHitLength', 'PassiveLength', 'OnHitChance', 'slots']

all_equip_slots = ['head', 'mask', 'neck', 'chest', 'wrist1', 'wrist2', 'ring1', 'ring2', 'idol',
                   'belt', 'legs', 'boots', 'right_hand', 'left_hand', 'ranged', 'ammo']

all_stats = ['HP', 'MP', 'MND', 'STA', 'SPD', 'STR', 'MDEF', 'PDEF']

spell_template_params = ['name', 'description', 'cast_message', 'hit_message', 'MP_cost', 'HP_cost',
                         'power', 'HP_scale', 'MP_scale', 'MND_scale', 'STR_scale', 'STA_scale', 'SPD_scale',
                         'AOE', 'self_only', 'HP_steal', 'MP_steal', 'item_steal', 'gold_steal',
                         'stun_chance', 'stun_duration', 'sleep_chance', 'sleep_duration',
                         'charm_chance', 'charm_duration']
