from __future__ import division

import pygame
# from pygame.locals import *
# from pytmx.util_pygame import load_pygame

from gameobjects.gameobject import *
from mp.server import GameServer


class GameController(object):
    """
    Controls all aspect of the game engine, hosts server, interfaces with clients
    """
    def __init__(self):
        """
        :param world: wld template file
        """
        # Instantiate goc and add default starting room
        self.goc = GameObjectController(self)
        self.goc.add_room(START_ROOM)

        self.dt = None

        # {'playername': <lifeformid>, 'playername': <lifeformid>, ... }
        self.gameserver = GameServer(self.goc)

        self.running = False

    def load_game(self, save_file):
        """ Load GOC """
        pass

    def save_game(self, save_file):
        """ Pickle GOC """
        pass

    def update(self, dt):
        self.goc.update(dt)
        self.gameserver.update(dt)

    def run(self):
        """ Run the game loop """
        clock = pygame.time.Clock()
        self.running = True

        try:
            while self.running:
                self.dt = clock.tick(60)

                # Update Gameobjects
                self.goc.update(self.dt)

                # Listen on server for client requests
                # GameServer has access to GOC and can change gameobject's attributes directly
                self.gameserver.listen(self.gameserver.get_clients())

        except KeyboardInterrupt:
            self.running = False
        pass

if __name__ == '__main__':
    a = GameController()
    a.run()
