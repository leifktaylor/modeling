from cli import CliParser
from pygame.locals import *
import pygame
# size of walkable tile
TILE_SIZE = 8


class PlayerController(object):
    def __init__(self, game):
        self.game = game
        self.hero = self.game.hero
        self.sprite = self.hero.remotesprite
        self.cli_parser = CliParser(game=self.game)

    def handle_input(self, dt):
        """ Handle pygame input events"""

        def move_timer_reset():
            self.hero.move_timer = self.hero.move_time

        # event = poll()
        events = pygame.event.get()

        # while event:
        for event in events:
            # update text_box

            if event.type == QUIT:
                self.game.running = False
                break

            # This is where key press events go
            elif event.type == KEYDOWN:
                msgvalue = self.game.text_box.update(events)
                if msgvalue:
                    self.cli_parser.parse(msgvalue)

                if event.key == K_ESCAPE:
                    self.game.running = False
                    break

                elif event.key == K_EQUALS:
                    self.game.map_layer.zoom += .1

                elif event.key == K_MINUS:
                    value = self.game.map_layer.zoom - .1
                    if value > 0:
                        self.game.map_layer.zoom = value

            # this will be handled if the window is resized
            elif event.type == VIDEORESIZE:
                init_screen(event.w, event.h)
                self.game.map_layer.set_size((event.w, event.h))

            elif event.type == KEYUP:
                if event.key == K_LSHIFT or event.key == K_RSHIFT:
                    self.game.text_box.shifted = False
                    # event = poll()

        # using get_pressed is slightly less accurate than testing for events
        # but is much easier to use.
        moved = False
        if self.hero.move_timer <= 0:
            if not self.hero.moving:
                pressed = pygame.key.get_pressed()
                target_coords = [None, None]
                if pressed[K_UP]:
                    # This is a diagonal fix, pre-checking for collision on one of the axis
                    if not self.hero.collision_check([self.hero.x, self.hero.y - TILE_SIZE]):
                        moved = True
                        target_coords[1] = self.hero.y - TILE_SIZE
                elif pressed[K_DOWN]:
                    if not self.hero.collision_check([self.hero.x, self.hero.y + TILE_SIZE]):
                        target_coords[1] = self.hero.y + TILE_SIZE
                        moved = True

                if pressed[K_LEFT]:
                    target_coords[0] = self.hero.x - TILE_SIZE
                    moved = True
                elif pressed[K_RIGHT]:
                    target_coords[0] = self.hero.x + TILE_SIZE
                    moved = True

                if moved:
                    target_coords = [self.hero.position[i] if item is None else
                                     item for i, item in enumerate(target_coords)]
                    move_timer_reset()
                    self.hero.move_lifeform(target_coords)
        else:
            return
