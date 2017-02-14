import Queue
import threading
import urllib2

# called by each thread
# def get_url(q, url):
#     q.put(urllib2.urlopen(url).read())
#
# theurls = ["http://google.com", "http://yahoo.com"]
#
# q = Queue.Queue()
#
# for u in theurls:
#     t = threading.Thread(target=get_url, args=(q, u))
#     t.daemon = True
#     t.start()
#
# s = q.get()
# print s
#

# import time
#
#
# def take_input(prompt='Input: '):
#     while True:
#         user_input = raw_input(prompt)
#
#
# def print_text(message='Hello World'):
#     while True:
#         time.sleep(2)
#         print(message)
#
# if __name__ == '__main__':
#
#     q = Queue.Queue()
#
#     printer = threading.Thread(target=take_input)
#     printer.daemon = True
#     inputer = threading.Thread(target=print_text)
#     inputer.daemon = True
#
#     printer.start()
#     inputer.start()

import pygame
from pygame.locals import *


def display(str):
    #text = font.render(str, True, (255, 255, 255), (159, 182, 205))
    text = myfont.render(str, 1, (255, 255, 255))
    #textRect = text.get_rect()
    #textRect.centerx = screen.get_rect().centerx
    #textRect.centery = screen.get_rect().centery
    #screen.blit(text, textRect)
    screen.blit(text, (100, 100))
    pygame.display.update()

# Initialize pygame
pygame.init()

# Create display with resolution
screen = pygame.display.set_mode((800, 450))

# Label of screen
pygame.display.set_caption('Python numbers')

# Fill screen with black background
screen.fill((0, 0, 0))


# initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
myfont = pygame.font.SysFont("monospace", 18)

# render text
#label = myfont.render("Some text!", 1, (255,255,0))
#screen.blit(label, (100, 100))


done = False

# Display input as typed

line = ''
while not done:
    display(str(pygame.key.name(keys)))

    pygame.event.pump()
    keys = pygame.key.get_pressed()


    if keys[K_ESCAPE]:
        done = True

