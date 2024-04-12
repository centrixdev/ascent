import pygame
from classes.tile import Tile
from classes.player import Player


class Level:
    def __init__(self, tmx_map, window):
        self.player = None
        self.window = window
        self.display_surface = pygame.display.get_surface()

        self.level_width = tmx_map.width * 8
        self.level_height = tmx_map.height * 8

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()

        self.setup(tmx_map)
        self.world = pygame.Surface((320, 180))

    def setup(self, tmx_map):

        spawn_location = None

        for layer in tmx_map.visible_layers:
            if layer.name == "collision":
                for x, y, image in layer.tiles():
                    Tile(x * 8, y * 8, image, self.collision_sprites, self.all_sprites)
            elif layer.name == "damage":
                for x, y, image in layer.tiles():
                    Tile(x * 8, y * 8, image, self.damage_sprites, self.all_sprites)
            elif layer.name == "Locations":
                for obj in layer:
                    if obj.type == "Player" and obj.name == "Spawn":
                        spawn_location = (obj.x, obj.y)

        if spawn_location is not None:
            self.all_sprites.add(Player(spawn_location, self.collision_sprites, self.damage_sprites, self.all_sprites))

    def run(self):
        # clear the display surface
        self.world.fill((0, 0, 0))

        # Update all sprites
        self.all_sprites.update()

        # Draw all sprites onto self.world
        self.all_sprites.draw(self.world)

        # Scale self.world to the size of the window
        scaled_game_world = pygame.transform.scale(self.world, self.window.get_size())

        # Blit the scaled game world onto the display surface
        self.display_surface.blit(scaled_game_world, (0, 0))
