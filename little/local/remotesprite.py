import pygame


class RemoteSpriteController(object):
    def __init__(self, game):
        """
        :param game: Game object instance
        :param id: id of current logged in player gameobject
        :param group: pyscroll sprite group
        """
        # Access to game object is required to add sprites to group
        self.game = game

        # Dictionary like {<id>: <RemoteSprite>, <id>: <RemoteSprite>, ... }
        self._remotesprites = {}
        # Create sprite group (pygame)

        self.initialized = False
        self.id = None
        self.group = None

    def initialize(self):
        self.id = self.game.hero.id
        self.group = self.game.group

    def add_remotesprite(self, id, sprite, coords):
        remotesprite = RemoteSprite(id=id, sprite=sprite, coords=coords)
        self._remotesprites[id] = remotesprite
        return remotesprite

    def remove_remotesprite(self, id):
        del self._remotesprites[id]

    @property
    def visible(self):
        """ Return all dict {<id>: sprite, ... } of remotesprites which are not stealthed / invisible """
        pass

    @property
    def remotesprites(self):
        return self._remotesprites

    def update_coords(self, coords_dict):
        """ Takes a dictionary of coords like {<id>: (<sprite>, <coords>), <id>: <coords>, ... } """
        for id, spritecoords in coords_dict.items():
            # If this remote sprite is rendered already
            if id in self.remotesprites.keys():
                self.remotesprites[id].coords = spritecoords[1]
            # If this sprite is not yet known to client, create it
            else:
                if id != self.id:
                    remote_sprite = self.add_remotesprite(id=id, sprite=spritecoords[0], coords=spritecoords[1])
                    self.group.add(remote_sprite)
        # If we have a remote sprite locally that no longer exists on remote, remove it
        for id in self.remotesprites.keys():
            if id not in coords_dict.keys():
                remote_sprite = self.remotesprites[id]
                self.group.remove(remote_sprite)
                self.remove_remotesprite(id)

    def update(self):
        pass

    def clear_sprites(self):
        """ Delete all remotesprite objects """
        self._remotesprites = {}
        self.group = pygame.sprite.Group()


class RemoteSprite(pygame.sprite.Sprite):
    """
    This object is the counterpart of a gameobject on the server side.  It holds a limited amount
    of information about its sister game object.  This allows the server to expose a limited amount
    of information to the client, and the client to render a representation of all the gameobjects
    in the game world.
    """
    def __init__(self, id, sprite, coords):
        """
        :param id: id of sister gameobject on server side
        :param sprite: image
        :param coords: pixel coordinates to render on screen (from remote gameobject)
        :param stats: stats of Gameobject counterpart
        """
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        print(sprite)
        self.image = pygame.image.load(sprite).convert_alpha()
        self.rect = self.image.get_rect()
        self._coords = coords

    def update(self, dt=None):
        self.rect.topleft = self._coords

    @property
    def x(self):
        return self._coords[0]

    @x.setter
    def x(self, value):
        self._coords[0] = value

    @property
    def y(self):
        return self._coords[1]

    @y.setter
    def y(self, value):
        self._coords[1] = value

    @property
    def coords(self):
        return list(self._coords)

    @coords.setter
    def coords(self, value):
        self._coords = list(value)