import pygame
import sys
import json

from classes.ui import UI_manager
from pytmx.util_pygame import load_pygame
from classes.level import Level


class Steuerung:
    def __init__(self, screen_width, screen_height):
        pygame.init()
        pygame.display.set_caption("Ascent")
        self.window = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()

        self.ui_manager = UI_manager((screen_width, screen_height), self.window)

        self.tmx_maps = {
            0: load_pygame("levels/data/tmx/tut-jump.tmx"),
            1: load_pygame("levels/data/tmx/tut-dash.tmx"),
            2: load_pygame("levels/data/tmx/tut-precise.tmx"),
            3: load_pygame("levels/data/tmx/tut-fall.tmx"),
            4: load_pygame("levels/data/tmx/level1.tmx"),
            5: load_pygame("levels/data/tmx/level2.tmx")
        }
        self.current_level_number = 0

        # TODO: main menu save auswahl
        self.load_save("example")

        self.current_level = Level(self.tmx_maps[self.current_level_number or 0], self.window)

        self.screen_width = screen_width
        self.screen_height = screen_height

    def load_save(self, save_name):
        self.save_name = save_name
        with open(f'saves/{save_name}.json', 'r') as f:
            data = json.load(f)
            print(data)
            if data["tutorial_finished"]:
                self.current_level_number = data["level"]+3


    def run(self):
        run = True

        while run:
            deltaTime = self.clock.tick(60) / 1000 * 60  # framerate independence

            for event in pygame.event.get():
                self.ui_manager.process_events(event)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.current_level.toggle_pause()
                        self.ui_manager.toggle_pause()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.current_level.run(deltaTime)
            if self.current_level.is_won:
                self.current_level_number += 1
                with open(f'saves/{self.save_name}.json', 'w') as json_file:
                    if self.current_level_number > 3:
                        json.dump({
                            "tutorial_finished": True,
                            "level": self.current_level_number-3
                        }, json_file)
                    else:
                        json.dump({
                            "tutorial_finished": False,
                            "level": -1
                        }, json_file)


                self.current_level = Level(self.tmx_maps[self.current_level_number], self.window)

            self.ui_manager.update(deltaTime)
            self.ui_manager.draw()

            pygame.display.flip()

        pygame.quit()
        exit()
