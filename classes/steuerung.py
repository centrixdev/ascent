import pygame
import sys
from pytmx.util_pygame import load_pygame
from classes.level import Level


class Steuerung:
    def __init__(self, screen_width, screen_height):
        self.player = None
        pygame.init()
        pygame.display.set_caption("Ascent")
        self.window = pygame.display.set_mode((screen_width, screen_height))

        self.clock = pygame.time.Clock()

        self.tmx_maps = {0: load_pygame("levels/data/tmx/level0.tmx")}
        self.current_level = Level(self.tmx_maps[0], self.window)

        self.screen_width = screen_width
        self.screen_height = screen_height






    def run(self):
        run = True
        while run:
            deltaTime = self.clock.tick(240) / 1000 * 60  # framerate independence
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.current_level.run()

            pygame.display.flip()
        pygame.quit()
        exit()
