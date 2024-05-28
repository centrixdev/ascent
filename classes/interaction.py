import json

import pygame.key
import pygame.sprite


class Interaction:
    def __init__(self, interaction, level_number, pos, camera):

        self.pos = pos
        self.camera = camera

        self.x = interaction[0]
        self.y = interaction[1]
        self.width = interaction[2]
        self.height = interaction[3]

        self.is_active = False

        self.popup_active = False

        self.id = interaction[4]
        self.level_number = level_number
        self.content = []

        self.type = ""
        self.load_interaction()

        self.popup_image = pygame.image.load("graphics/interaction/popup.png").convert_alpha()
        self.container_image = pygame.image.load(f"graphics/interaction/{self.type}_container.png").convert_alpha()

        self.current_text_index = 0

        self.pressed_space = False

        # animations
        self.popup_scale_factor = 0  # Add this line
        self.popup_scale_speed = 0.125  # Speed of scaling animation
        self.is_hiding = False

    def update(self, deltaTime):

        keys = pygame.key.get_pressed()
        if self.is_active:
            if keys[pygame.K_SPACE]:
                if not self.pressed_space:
                    self.next_text()
                    self.is_hiding = True
                    self.pressed_space = True
            else:
                self.pressed_space = False
        else:
            if keys[pygame.K_e]:
                self.is_active = True
            elif not self.popup_active:
                self.popup_active = True
        if self.is_hiding:

            # Decrease scale_factor
            self.popup_scale_factor = max(0, self.popup_scale_factor - self.popup_scale_speed * deltaTime)
            if self.popup_scale_factor == 0:
                self.popup_active = False
                self.is_hiding = False
        elif self.popup_active:
            # Increase scale_factor
            self.popup_scale_factor = min(1, self.popup_scale_factor + self.popup_scale_speed * deltaTime)

    def load_interaction(self):
        with open(f'levels/interactions/level{self.level_number}.json', 'r') as f:
            data = json.load(f)
            for interaction in data['interactions']:
                if interaction["id"] == self.id:
                    self.content = interaction["content"]
                    self.type = interaction["type"]
                    break

    def next_text(self):
        if self.current_text_index < len(self.content)-1:
            # Show the text at current_text_index

            self.current_text_index += 1
        else:
            # Hide the text
            self.is_active = False
            self.camera.zoom()
            self.current_text_index = 0
            pass

    def draw(self, surface):
        if self.popup_active:
            # Draw the popup
            scaled_popup_image = pygame.transform.scale(
                self.popup_image,
                (int(self.popup_image.get_width() * self.popup_scale_factor),
                 int(self.popup_image.get_height() * self.popup_scale_factor))
            )

            offset = (scaled_popup_image.get_width() - self.width) // 2
            popup_pos = (self.pos('x', self.x - offset), self.pos('y', self.y - scaled_popup_image.get_height() - 2))
            surface.blit(scaled_popup_image, (popup_pos))



            if self.is_active:
                self.popup_active = False
                self.camera.zoom('interaction')
        if self.is_active:
            surface.blit(self.container_image, (surface.get_width() // 2 - self.container_image.get_width() // 2,
                                                20))
            # Draw the text
            font = pygame.font.Font("graphics/munro.ttf", 10)
            text = font.render(self.content[self.current_text_index], False, (0, 0, 0))
            text_rect = text.get_rect(center=(surface.get_width() // 2, 35))
            surface.blit(text, text_rect)

