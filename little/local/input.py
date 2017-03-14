from local.cli import CliParser
from pygame.locals import *
import pygame

# from particles import PyIgnition
# from particles.fire import FXFire

from functions.game_math import map_pos

# size of walkable tile
TILE_SIZE = 8
CURSOR_GRAPHIC = 'graphics/sprites/gems/067.png'


class Cursor(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.solid = False
        self.game = game
        self.image = pygame.image.load(CURSOR_GRAPHIC).convert_alpha()
        self.rect = self.image.get_rect()
        self._coords = [0, 0]
        self.game.group.add(self, layer='over0')

    def update(self, dt=None):
        mousepos = pygame.mouse.get_pos()
        self.coords = map_pos(self.game, mousepos)
        self.rect.center = self._coords

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


class PlayerController(object):
    def __init__(self, game):
        self.game = game
        self.hero = self.game.hero
        self.sprite = self.hero.remotesprite
        self.cli_parser = CliParser(game=self.game)
        self.cursor = Cursor(game)

        self.cooldown = 20
        self.cooldowntimer = self.cooldown

        self.dir = 'right'

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

            # Mouse click events
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                pos = self.cursor.coords
                clicked_sprites = [s for s in self.game.group if s.rect.collidepoint(pos) and not isinstance(s, Cursor)]
                if clicked_sprites:
                    sprite = clicked_sprites[0]
                    response = self.game.client.send('get_target', [sprite.id])
                    name, stats = response['response']['name'], response['response']['stats']
                    self.hero.tgh.set_target(id=sprite.id, name=name, stats=stats)
                if not clicked_sprites:
                    self.hero.tgh.drop_target()

            # This is where key press events go
            elif event.type == KEYDOWN:
                msgvalue = self.game.text_box.update(events)
                if msgvalue:
                    self.cli_parser.parse(msgvalue)

                if event.key == K_ESCAPE:
                    self.hero.tgh.drop_target()
                    break

                if event.key == K_SPACE:
                    pass

                if event.key == K_a:
                    if self.hero.attacking:
                        self.hero.attacking = False
                    else:
                        self.hero.attacking = True

                elif event.key == K_EQUALS:
                    self.game.map_layer.zoom += .1

                elif event.key == K_MINUS:
                    value = self.game.map_layer.zoom - .1
                    if value > 0:
                        self.game.map_layer.zoom = value

            # this will be handled if the window is resized
            elif event.type == VIDEORESIZE:
                pass
                # # TODO: Bug here
                # init_screen(event.w, event.h)
                # self.game.map_layer.set_size((event.w, event.h))

            elif event.type == KEYUP:
                if event.key == K_LSHIFT or event.key == K_RSHIFT:
                    self.game.text_box.shifted = False
                    # event = poll()

        # using get_pressed is slightly less accurate than testing for events
        # but is much easier to use.
        moved = False

        pressed = pygame.key.get_pressed()
        self.cooldowntimer -= 1

        if self.cooldowntimer <= 0:
            if pressed[K_TAB]:
                self.cooldowntimer = self.cooldown
                # Cycle through nearby targets with TAB
                id_list = self.hero.nearby_lifeforms.keys()
                for i, id in enumerate(id_list):
                    if self.hero.tgh.target:
                        # If we already have an targets selected
                        if self.hero.tgh.target['id'] == id or self.hero.tgh.target['id'] == self.hero.id:
                            if i + 1 < len(id_list):
                                response = self.game.client.send('get_target', [id_list[i + 1]])
                                name, stats = response['response']['name'], response['response']['stats']
                                self.hero.tgh.set_target(id=id_list[i + 1], name=name, stats=stats)
                                break
                            else:

                                response = self.game.client.send('get_target', [id_list[0]])
                                name, stats = response['response']['name'], response['response']['stats']
                                self.hero.tgh.set_target(id=id_list[0], name=name, stats=stats)
                    else:
                        response = self.game.client.send('get_target', [id_list[i]])
                        name, stats = response['response']['name'], response['response']['stats']
                        self.hero.tgh.set_target(id=id_list[i], name=name, stats=stats)

        if self.hero.move_timer <= 0:
            if not self.hero.moving:
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
                    # Aim direction we're moving
                    rs = self.hero.remotesprite
                    if self.dir is not 'left':
                        rs.image = pygame.transform.flip(rs.image, True, False)
                        self.hero.remotesprite.visualequipment.flip()
                        self.dir = 'left'
                        self.hero.remotesprite.facing = 'left'
                    target_coords[0] = self.hero.x - TILE_SIZE
                    moved = True

                elif pressed[K_RIGHT]:
                    # Aim direction we're moving
                    rs = self.hero.remotesprite
                    if self.dir is not 'right':
                        self.hero.remotesprite.visualequipment.flip()
                        rs.image = pygame.transform.flip(rs.image, True, False)
                        self.dir = 'right'
                        self.hero.remotesprite.facing = 'right'
                    target_coords[0] = self.hero.x + TILE_SIZE
                    moved = True

                if moved:
                    target_coords = [self.hero.position[i] if item is None else
                                     item for i, item in enumerate(target_coords)]
                    move_timer_reset()
                    self.hero.move_lifeform(target_coords)
