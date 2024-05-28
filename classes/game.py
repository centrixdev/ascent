import time

import pygame
import sys
import json

from pytmx.util_pygame import load_pygame
from classes.level import Level


class Game:
    def __init__(self, window, save):
        self.current_level_playtime = 0
        self.save_filename = ""
        self.save_name = ""
        self.current_level_deaths = 0
        self.levels = None
        self.start_time = time.time()

        self.window = window
        self.clock = pygame.time.Clock()

        self.tmx_maps = {
            0: load_pygame("levels/worlds/kitchen/level0.tmx"),

        }
        self.current_level_number = 0

        # TODO: main menu save auswahl
        self.load_save(save)

        self.current_level = Level(self.tmx_maps[self.current_level_number or 0], self.window,
                                   self.current_level_number or 0, self.current_level_deaths, self.save_progress)

    def load_save(self, save_filename):
        self.save_filename = save_filename
        with open(f'saves/{save_filename}.json', 'r') as f:
            data = json.load(f)
            self.save_name = data["name"]
            self.current_level_number = data["level"]
            self.current_level_deaths = data["deaths"]
            self.current_level_playtime = data["playtime"]

    def save_progress(self):
        playtime = (time.time() - self.start_time) + self.current_level_playtime
        self.current_level_playtime = playtime
        deaths = self.current_level.player.deaths
        level_number = self.current_level_number
        with open(f'saves/{self.save_filename}.json', 'w') as json_file:
            json.dump({
                "name": self.save_name,
                "level": level_number,
                "deaths": deaths,
                "playtime": playtime
            }, json_file)
        self.start_time = time.time()

    def run(self):
        while 1:

            deltaTime = self.clock.tick(240) / 1000 * 60  # framerate independence
            # elapsed_time = (time.time() - self.start_time) * 1000
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.current_level.toggle_pause()

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pause_options = self.current_level.run(deltaTime)
            if pause_options == "quit":
                return "quit"
            elif pause_options == "main_menu":
                return "main_menu"
            if self.current_level.is_won:
                self.current_level_number += 1
                self.current_level = Level(self.tmx_maps[self.current_level_number], self.window,
                                           self.current_level_number, self.current_level.deaths, self.save_progress)

            pygame.display.flip()

        exit()
