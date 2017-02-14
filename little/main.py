from gameobjects.gameobject import *
from gameobjects.actions import *
from socket import error as socket_error
import pygame
import graphics.eztext as eztext
from pygame.locals import *
from mp.client import GameClient
from graphics.graphictext import draw_lines, InputLog


pygame.display.set_caption('LITTLE')


def main():
    # initialize pygame
    pygame.init()
    # create the screen
    screen = pygame.display.set_mode((1100, 619))
    # fill the screen w/ white
    screen.fill((0, 0, 0))
    # here is the magic: making the text input
    # create an input with a max length of 45,
    # and a red color and a prompt saying 'type here: '
    text_box = eztext.Input(maxlength=90, color=(255, 255, 255), x=0, y=590,
                            font=pygame.font.Font(None, 22), prompt=': ')

    # Create InputLog
    inputlog = InputLog(coords=(0, 570))

    # create the pygame clock
    clock = pygame.time.Clock()
    # main loop!

    # MP stuff
    a = GameClient()

    while 1:
        # make sure the program is running at 30 fps
        clock.tick(60)

        # events for text_box
        events = pygame.event.get()

        # process other events
        for event in events:
            # close it x button is pressed
            if event.type == QUIT:
                return

        # clear the screen (this is important in between frames)
        screen.fill((0, 0, 0))

        # update text_box
        msgvalue = text_box.update(events)
        if msgvalue:
            # inputlog.add_line(msgvalue)
            try:
                r = a.send(msgvalue)
                inputlog.add_line(r)
            except socket_error:
                inputlog.add_line('Cannot connect to server')

        # blit text_box on the sceen
        text_box.draw(screen)

        # blit InputLog to screen
        inputlog.draw(screen)

        draw_lines(['this is an example', 'of printing a list of lines', 'to the screen'], screen)

        # refresh the display
        pygame.display.flip()

if __name__ == '__main__':
    main()
