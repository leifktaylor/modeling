from gameobjects.gameobject import *
import pprint


a = TemplateParser()
print(' TEST 1 : Lifeform ')
pprint.pprint(a.load_data('gameobjects/lifeform/zaxim.lfm'))
print(' TEST 2 : Item ')
pprint.pprint(a.load_data('gameobjects/weapon/long_sword.itm'))
print(' TEST 3 : Room ')
pprint.pprint(a.load_data('gameobjects/room/template.rm'))
print(' TEST 4 : Faction ')
pprint.pprint(a.load_data('gameobjects/faction/chand_baori.fct'))
print(' TEST 5 : AI ')
pprint.pprint(a.load_data('gameobjects/ai/healer.ai'))
print(' TEST 6 : DIALOGUE ')
pprint.pprint(a.load_data('gameobjects/dialogue/template.dlg'))


print(' ------- GameObjectController Tests ------- ')
print(' TEST 7 : Rooms')
print('Instantiating GOC')
GOC = GameObjectController()
print('Creating Template Room')
GOC.add_room('gameobjects/room/template.rm')
print('Verifying Room in Room list')
print(GOC.rooms)


print(' TEST 8 : Lifeform Creation / Removal')
print(' Creating 30 Lifeforms from template ')
instance_list = []
for i in range(0, 30):
    instance, id = GOC.add_gameobject('gameobjects/lifeform/template.lfm')
    instance_list.append(instance)
for i, lifeform in enumerate(instance_list):
    print(i, lifeform)
    assert i == lifeform.id
pprint.pprint(instance.__dict__)

print(' Removing Every other Lifeform ')
for i in range(0, 30, 2):
    GOC.remove_gameobject(i)
for id, lf in GOC.gameobjects.items():
    try:
        print(lf, lf.id)
    except AttributeError:
        print(None)

print(' Creating 30 More Lifeforms from template, should fill gaps, and id on class should match id in hash table')
for i in range(0, 30):
    instance, id = GOC.add_gameobject('gameobjects/lifeform/template.lfm', 'template_room', [5, 5])

for id, instance in GOC.gameobjects.items():
    try:
        assert id == instance.id
    except AttributeError:
        pass
    print(id, instance)

print(' TEST 9 : Inventory ')
instance, id = GOC.add_gameobject('gameobjects/lifeform/template.lfm')
pprint.pprint(instance.inventory.__dict__)

