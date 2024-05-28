import os

import pygame

from classes.menu.start import Start
from classes.menu.options import Options
from classes.menu.level_select import LevelSelect
from classes.game import Game

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
pygame.init()
DISPLAY_WIDTH = pygame.display.Info().current_w
DISPLAY_HEIGHT = pygame.display.Info().current_h

is_fullscreen = False

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ascent")


def level_select(window):
    option = LevelSelect(window).run()
    if option == "back":
        show_menu(False)
    elif option == "quit":
        pygame.quit()
        quit_game()
    else:
        options = Game(window, option).run()
        if options == "main_menu":
            show_menu(False)
        elif options == "quit":
            quit_game()


def options(window):
    option = Options(window).run()

    if option == "back":
        show_menu(False)
    elif option == "quit":
        quit_game()
    else:
        if option == "fullscreen_exclusive":
            global is_fullscreen
            if not is_fullscreen:
                window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF, 16)
            else:
                window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            is_fullscreen = not is_fullscreen

        options(window)


def show_menu(show_splash):
    operation = Start(window, show_splash).run()
    if operation == "start":
        level_select(window)
    elif operation == "options":
        options(window)

    elif operation == "quit":
        quit_game()


def quit_game():
    pygame.quit()
    exit()


def main():
    run = True
    while run:
        show_menu(True)
    pygame.quit()
    exit()


if __name__ == "__main__":
    main()
