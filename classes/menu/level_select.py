import json
import os
import sys
import pygame.freetype

import pygame
class LevelSelect:
    def __init__(self, window):
        self.window = window
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Read from files in folder saves
        self.options = ["Create New Save"]
        save_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'saves')
        for filename in os.listdir(save_dir):
            if filename.endswith('.json'):
                with open(os.path.join(save_dir, filename), 'r') as f:
                    save_data = json.load(f)
                    self.options.append(save_data['name'])

        self.current_option = 0

        self.input_font = pygame.freetype.Font(None, 24)
        self.input_string = ""
        self.input_active = False

    def create_new_save(self):
        save_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'saves')
        save_number = len(self.options)-1  # Use the number of options as the save number
        save_data = {
            "name": self.input_string,
            "level": 0,
            "deaths": 0,
            "playtime": 0
        }
        with open(os.path.join(save_dir, f"{save_number}.json"), 'w') as f:
            json.dump(save_data, f)
        self.options.append(save_data['name'])

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    self.input_active = False
                    if self.input_string:
                        self.create_new_save()
                        self.input_string = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.input_string = self.input_string[:-1]
                else:
                    if len(self.input_string) < 20:
                        self.input_string += event.unicode

            else:
                if event.key == pygame.K_UP:
                    self.current_option = (self.current_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.current_option = (self.current_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.current_option == 0:
                        self.input_active = True
                    else:
                        return self.current_option - 1
                elif event.key == pygame.K_ESCAPE:
                    return "back"

    def draw(self):
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.current_option else (100, 100, 100)
            if i == 0:  # "Create New Save" option
                text_surface = self.font.render(option, True, color)
            else:  # Saved game options
                save_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'saves')
                with open(os.path.join(save_dir, f"{i - 1}.json"), 'r') as f:
                    save_data = json.load(f)
                deaths = save_data['deaths']
                playtime_sec = save_data['playtime']
                playtime_ms = int((playtime_sec - int(playtime_sec)) * 1000)
                playtime_min, playtime_sec = divmod(playtime_sec, 60)
                playtime_hrs, playtime_min = divmod(playtime_min, 60)
                playtime_str = f"{int(playtime_hrs)}:{int(playtime_min):02d}:{int(playtime_sec):02d}.{int(playtime_ms):03d}"

                option_text = f"{option} - Deaths: {deaths} - Playtime: {playtime_str}"
                text_surface = self.font.render(option_text, True, color)
            self.window.blit(text_surface, (100, 100 + i * 40))
        if self.input_active:
            input_surface, _ = self.input_font.render(self.input_string, (255, 255, 255) )
            input_container = pygame.Rect((90, 90 + len(self.options) * 40, 450, 40))
            pygame.draw.rect(self.window, (50, 50, 50), input_container)
            # position the input text via the bottom left corner of the input container
            self.window.blit(input_surface, (100, input_container.bottomleft[1] - input_surface.get_height() -10))

    def run(self):
        run = True
        while run:
            deltaTime = self.clock.tick(240) / 1000 * 60  # framerate independence

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                result = self.handle_event(event)
                if result is not None:
                    return result
            self.window.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()

        pygame.quit()
        exit()
