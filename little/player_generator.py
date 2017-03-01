from gameobjects.gameobject import GameObjectController


def make_player(filepath):
    gc = GameObjectController()
    lifeform_instance, id = gc.add_gameobject(filepath)
    name = lifeform_instance.name
    gc.save_gameobject(lifeform_instance, 'mp/users/{0}.sav'.format(name))

if __name__ == '__main__':
    path = 'gameobjects/lifeform/'
    templates = ['zaxim']
    for template in templates:
        make_player('{0}/{1}.lfm'.format(path, template))