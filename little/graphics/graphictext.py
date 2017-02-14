# EzText example
import eztext
import pygame
from pygame.locals import *


def draw_text(string, surface, size=22, coords=(0, 0), color=(255, 255, 255), background=None):
    font = pygame.font.Font(None, size)
    text = font.render(string, True, color, background)
    surface.blit(text, coords)


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
