from gameobjects.gameobject import *
from gameobjects.actions import *
from socket import error as socket_error
import pygame
import graphics.eztext as eztext
from pygame.locals import *
from mp.client import GameClient
from graphics.graphictext import draw_lines, InputLog


pygame.display.set_caption('LITTLE')

# Order of operations for client/server

"""
                                # Listen for client
                                loop forever:
                                    for each client:
                                        server.listen()


# Get user input and tick heartbeat timer
client.timer += 1
client.action = client_get_input()  # Get user input if any, ignore input if local cooldown

# Request changes update from server
if client.action or heartbeat == timer:
    client.request_update(username, password, current_room, action(yes/no))
    client.timer.reset()

                                # Update room with changes if any, server waits for action if valid
                                server.if changes:
                                    server.send_update(data, client)
                                server.else:
                                    server.send_update(None, client)
                                server.if not action:
                                    server.next_client()  # If there was no action, listen for next client

    client.if changes:
        client.room.update(changes)  # Update room data
        client.update_room_graphics(changes)  # Update room graphics

    ----- if there is an action by the client, continue reading -----

                                server.wait_for_update_from_client() # Wait for a while, and then move on if timeout


    client.if action:
        valid = client.do_action()   # Update local room data for action, and show graphical effects
                                     # Will return 0 if action went through, or errorcode if it didn't

        client.if action == valid:
            client.send_update(room_data, server)
        else:
            client.send_update(None, server)

                                if update not None:
                                    server.update_room()

        client.update_room_graphics()  # Update room graphics (objects on tiles, etc)
"""


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
                            font=pygame.font.Font(None, 24), prompt=': ')

    # Create InputLog
    inputlog = InputLog(coords=(0, 570), size=24, max_length=10)

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
