import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass
