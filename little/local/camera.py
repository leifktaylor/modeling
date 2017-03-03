import pygame


class Camera(object):
    """Invisible object that slowly follows player, screen locks onto this object"""
    def __init__(self, remotesprite):
        self.remotesprite = remotesprite
        x, y = self.remotesprite.x, self.remotesprite.y
        self.rect = pygame.Rect(x, y, 8, 8)
        self._coords = self.remotesprite.coords
        self.spd = 100.

    def update(self, dt):
        self.x += (self.remotesprite.x - self.x) * (dt / self.spd)
        self.y += (self.remotesprite.y - self.y) * (dt / self.spd)
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