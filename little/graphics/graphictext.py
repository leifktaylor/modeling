# EzText example
import eztext
import pygame
from pygame.locals import *


def draw_text(string, surface, size=22, coords=(0, 0), color=(255, 255, 255), background=None, font=None):
    font = pygame.font.Font(font, size)
    text = font.render(string, True, color, background)
    surface.blit(text, coords)
    return text


def draw_lines(line_list, surface, spacing=16, size=22, coords=(0, 0)):
    y = coords[1]
    for line in line_list:
        draw_text(string=line, surface=surface, size=size, coords=(coords[0], y))
        y += spacing


class InputLog(object):
    """
    InputLog is a text box similiar to text boxes in mmos.
    """
    def __init__(self, spacing=16, size=22, max_length=8, coords=(0, 0), scroll_type='up', line_list=None):
        if line_list:
            self.line_list = line_list
        else:
            self.line_list = []
        self.spacing = spacing
        self.max_length = max_length
        self.coords = coords
        self.size = size
        self.scroll_type = scroll_type

    def add_line(self, string):
        if self.scroll_type.lower() == 'up':
            if len(self.line_list) == self.max_length:
                self.line_list = [string] + self.line_list[:-1]
            else:
                self.line_list = [string] + self.line_list
        elif self.scroll_type.lower() == 'down':
            if len(self.line_list) == self.max_length:
                self.line_list = self.line_list[1:] + [string]
            else:
                self.line_list += [string]
        else:
            raise RuntimeError('scroll_type must be "up" or "down"')

    def draw(self, surface):
        y = self.coords[1]
        for line in self.line_list:
            draw_text(line, surface, self.size, (self.coords[0], y))
            if self.scroll_type.lower() == 'up':
                y -= self.spacing
            else:
                y += self.spacing


class InventoryBox(object):
    def __init__(self, inventory, coords=(0, 0), spacing=22, size=34,
                 color=(255, 255, 255), background=(0, 0, 0), font=None):
        self.slots = None
        self.equipped_list = None

        self.rects = []
        self.coords = coords
        self.spacing = spacing
        self.size = size
        self.color = color
        self.background = background
        self.font = font

        self.update_inventory(inventory)

    def update_inventory(self, inventory):
        # List of any non-empty (is not None) slots in inventory
        self.slots = [item for item in inventory.slots if item]
        # List of equipped item id's
        self.equipped_list = [item.id for item in self.slots if inventory.is_equipped(instance=item)]

        # Create rectangles for mouse collision
        x = self.coords[0]
        y = self.coords[1]

        self.rects = []
        for item in self.slots:
            rect = pygame.Rect(0, 0, 100, 22)
            rect.topleft = (x, y)
            self.rects.append(rect)
            y += self.spacing

    def collision_check(self, surface):
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                # get a list of all sprites that are under the mouse cursor
                clicked_objects = [s for s in self.rects if s.collidepoint(pos)]
                if clicked_objects:
                    self.color = (100, 100, 240)

                draw_text(str(clicked_objects), surface, coords=(100, 300), color=(0, 0, 0))
        pos = pygame.mouse.get_pos()
        draw_text(str(pos), surface, coords=(50, 200), color=(0, 0, 0))
        draw_text(str(self.rects), surface, coords=(80, 400), color=(0, 0, 0))


    def draw(self, surface):
        x = self.coords[0]
        y = self.coords[1]
        for item in self.slots:
            # If item is equipped
            if item.id in self.equipped_list:
                color = (255, 255, 0)
            # If item is not equipped
            else:
                color = self.color

            # Draw text to screen, and rectangles

            text = draw_text(string=item.name, surface=surface, size=self.size, color=color,
                             background=self.background, font=self.font, coords=(x, y))
            y += self.spacing
            self.collision_check(surface)




#
# def main():
#     # initialize pygame
#     pygame.init()
#     # create the screen
#     screen = pygame.display.set_mode((1100, 619))
#     # fill the screen w/ white
#     screen.fill((0, 0, 0))
#     # here is the magic: making the text input
#     # create an input with a max length of 45,
#     # and a red color and a prompt saying 'type here: '
#     text_box = eztext.Input(maxlength=90, color=(255, 255, 255), x=0, y=590, font=pygame.font.Font(None, 22), prompt=': ')
#
#     # Create InputLog
#     inputlog = InputLog(coords=(0, 570))
#
#     # create the pygame clock
#     clock = pygame.time.Clock()
#
#     # MP stuff
#     a = client.GameClient()
#
#     # main loop
#     while 1:
#         # make sure the program is running at 30 fps
#         clock.tick(60)
#
#         # events for text_box
#         events = pygame.event.get()
#
#         # process other events
#         for event in events:
#             # close it x button is pressed
#             if event.type == QUIT:
#                 return
#
#         # clear the screen (this is important in between frames)
#         screen.fill((0, 0, 0))
#
#         # update text_box
#         msgvalue = text_box.update(events)
#         if msgvalue:
#             # inputlog.add_line(msgvalue)
#             r = a.send(msgvalue)
#             inputlog.add_line(r)
#
#         # blit text_box on the sceen
#         text_box.draw(screen)
#         # draw InputLog to screen
#         inputlog.draw(screen)
#
#         draw_lines(['this is an example', 'of printing a list of lines', 'to the screen'], screen)
#
#         # refresh the display
#         pygame.display.flip()
#
# if __name__ == '__main__': main()
