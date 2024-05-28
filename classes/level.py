from operator import xor

import pygame
import pyscroll

from classes.interaction import Interaction
from classes.tile import Tile
from classes.tile import FallingTile
from classes.player import Player
from classes.camera import Camera




class Level:
    def __init__(self, tmx_map, window, level_number, deaths, save_progress):

        self.DEV_MODE = True
        # controlling the pause menu

        self.UP_KEY = False
        self.DOWN_KEY = False
        self.current_option = 0
        self.save_progress = save_progress

        self.deaths = deaths

        self.camera = None

        if level_number == 1:
            self.start_sequence = 500
        else:
            self.start_sequence = 50

        self.debug = False

        self.level_number = level_number

        self.is_paused = None
        self.player = None
        self.window = window
        self.display_surface = pygame.display.get_surface()

        self.level_width = tmx_map.width * 8
        self.level_height = tmx_map.height * 8

        # groups
        self.all_sprites = None
        self.collision_sprites = pygame.sprite.Group()
        self.falling_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()

        self.checkpoints = []
        self.interactions = []
        self.current_interaction = None

        self.world = pygame.Surface((320, 180))
        self.is_won = False
        self.win_area = None
        self.setup(tmx_map)
        self.show_starting_frame = False

    def setup(self, tmx_map):

        spawn_location = None

        # Make the scrolling layer
        map_layer = pyscroll.BufferedRenderer(
            data=pyscroll.TiledMapData(tmx_map),
            size=(320, 180),

        )

        # make the pygame SpriteGroup with a scrolling map
        self.all_sprites = pyscroll.PyscrollGroup(map_layer=map_layer)




        for layer in tmx_map.visible_layers:
            if layer.name.startswith('terrain_') or layer.name.endswith('_fall') or (
                    self.DEV_MODE and layer.name.startswith('prototype')):
                for x, y, image in layer.tiles():
                    if layer.name.endswith('_fall'):
                        blocks = self.find_connected_blocks(layer)
                        for block in blocks:
                            x, y, width, height = block
                            tile = FallingTile(x * 8, y * 8, image, self.collision_sprites, self.falling_sprites, height=height - 8, width=width - 8,
                                 right=False,
                                 down=False)
                            break
                    else:
                        Tile(x * 8, y * 8, image, self.collision_sprites, height=8, width=8, right=False,
                             down=False)
            elif layer.name == "damage_down":
                for x, y, image in layer.tiles():
                    Tile(x * 8, y * 8, image, self.damage_sprites, height=4, width=10, right=False,
                         down=True)

            elif layer.name == "damage_left":
                for x, y, image in layer.tiles():
                    Tile(x * 8, y * 8, image, self.damage_sprites, height=8, width=4, right=False,
                         down=False)
            elif layer.name == "damage_right":
                for x, y, image in layer.tiles():
                    Tile(x * 8, y * 8, image, self.damage_sprites, height=8, width=4, right=True,
                         down=False)
            elif layer.name == "Locations":
                for obj in layer:
                    if obj.type == "Player" and obj.name == "Spawn":
                        spawn_location = (obj.x, obj.y)
                    elif obj.type == "Player" and obj.name == "Win":
                        self.win_area = (obj.x, obj.y, obj.width, obj.height)
                    elif obj.type == "Player" and obj.name == "OutOfBounds":
                        outofbounds_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        Tile(outofbounds_rect.x, outofbounds_rect.y, None, self.damage_sprites,
                             height=outofbounds_rect.height, width=outofbounds_rect.width, right=False, down=False)
                    elif obj.type == "Player" and obj.name == "Barrier":
                        barrier_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        Tile(barrier_rect.x, barrier_rect.y, None, self.collision_sprites,
                             height=barrier_rect.height, width=barrier_rect.width,
                             right=False, down=False)
                    elif obj.type == "Checkpoint":
                        self.checkpoints.append((obj.x, obj.y, obj.width, obj.height))
                    elif obj.type == "Interaction":
                        self.interactions.append((obj.x, obj.y, obj.width, obj.height, obj.name))
        if spawn_location is not None and self.win_area is not None:
            self.player = Player(spawn_location, self)
            self.camera = Camera(self.player, self.all_sprites)
            self.all_sprites.add(self.player)

    def is_in_area(self, area):
        return self.player.hitbox.x < area[0] + area[2] and self.player.hitbox.x + self.player.hitbox.width > area[
            0] and self.player.hitbox.y < area[
            1] + area[3] and self.player.hitbox.y + self.player.hitbox.height > area[1]

    def check_area(self):
        # check for damage
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox):
                self.save_progress()
                self.player.is_dead = True

        # check for checkpoint
        for checkpoint in self.checkpoints:
            if self.is_in_area(checkpoint):
                self.save_progress()
                self.player.spawn_location = pygame.math.Vector2(checkpoint[0] + checkpoint[2] // 2,
                                                                 checkpoint[1] + checkpoint[3] // 2)

        # check for interaction
        for interaction in self.interactions:
            if self.is_in_area(interaction) and self.current_interaction is None:
                self.save_progress()
                self.current_interaction = Interaction(interaction, self.level_number, self.pos, self.camera)
            elif self.current_interaction is not None and not self.is_in_area((self.current_interaction.x,
                                                                               self.current_interaction.y,
                                                                               self.current_interaction.width,
                                                                               self.current_interaction.height,
                                                                               self.current_interaction.id)):
                self.current_interaction.is_hiding = True
                if self.current_interaction.popup_scale_factor == 0:
                    self.current_interaction = None

        # check for win
        if self.is_in_area(self.win_area):
            self.save_progress()
            self.is_won = True

    def run(self, deltaTime):

        if self.start_sequence > 0:
            self.start_sequence -= deltaTime
            if self.start_sequence <= 0:
                self.player.velocity = pygame.math.Vector2(0, 0)

        # toggle debug mode with F3, eliminate holding the key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_F3]:
            self.debug = not self.debug
            pygame.time.delay(150)

        if self.is_paused:
            # fill in the screen
            self.display_surface.fill((0, 0, 0))
            if keys[pygame.K_UP]:
                if not self.UP_KEY:
                    self.UP_KEY = True
                    self.current_option = (self.current_option - 1) % 4
            elif not keys[pygame.K_UP]:
                self.UP_KEY = False
            if keys[pygame.K_DOWN]:
                if not self.DOWN_KEY:
                    self.DOWN_KEY = True
                    self.current_option = (self.current_option + 1) % 4
            elif not keys[pygame.K_DOWN]:
                self.DOWN_KEY = False

            if keys[pygame.K_RETURN]:
                if self.current_option == 0:
                    self.toggle_pause()
                elif self.current_option == 1:
                    self.save_progress()
                    self.toggle_pause()
                elif self.current_option == 2:
                    self.save_progress()
                    self.toggle_pause()
                    return "main_menu"
                elif self.current_option == 3:
                    self.save_progress()
                    return "quit"

            font = pygame.font.Font(None, 36)
            text = font.render("Paused", True, (255, 255, 255))
            text_rect = text.get_rect(center=(640, 360))
            self.display_surface.blit(text, text_rect)
            # option to resume, save, go to main menu or quit
            for i, option in enumerate(["Resume", "Save", "Main Menu", "Quit"]):
                color = (255, 255, 255) if i == self.current_option else (100, 100, 100)
                text_surface = font.render(option, True, color)
                self.display_surface.blit(text_surface, (100, 100 + i * 40))

            pygame.display.flip()
            return

        # clear the display surface
        self.world.fill((0, 0, 0))

        self.check_area()
        if self.current_interaction is not None:
            self.current_interaction.update(deltaTime)
        # Update all sprites, except when an interaction is active
        if (self.current_interaction is None or not self.current_interaction.is_active):
            self.all_sprites.update(deltaTime)

        # Update the camera
        self.camera.update(deltaTime, self.start_sequence)

        for sprite in self.falling_sprites:
            if sprite.is_falling:

                sprite.animate(deltaTime)

        # Draw all sprites onto self.world
        self.draw()

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def pos(self, orientation, pos):
        if orientation == 'x':
            return pos % self.world.get_width()
        elif orientation == 'y':
            return pos % self.world.get_height() + 30
        return 0

    def draw(self):
        if self.player.animation_state == 'start_finished' and self.start_sequence > 0 and not self.show_starting_frame:
            Tile(self.player.rect.x, self.player.rect.y, self.player.start_frames[0],
                 self.all_sprites, height=32, width=32, right=False, down=False)
            self.show_starting_frame = True

        for sprite in self.falling_sprites:
            pass
            # sprite.draw_fall(self.world)
        self.all_sprites.draw(self.world)
        if self.current_interaction is not None:
            self.current_interaction.draw(self.world)

        if self.debug:
            pygame.draw.rect(self.world, (255, 0, 0), (
                self.pos('x', self.player.hitbox.x),
                self.pos('y', self.player.hitbox.y),
                self.player.hitbox.width,
                self.player.hitbox.height), 1)
            for damage_sprite in self.damage_sprites:
                pygame.draw.rect(self.world, (0, 255, 0), (
                    self.pos('x', damage_sprite.rect.x),
                    self.pos('y', damage_sprite.rect.y),
                    damage_sprite.rect.width,
                    damage_sprite.rect.height), 1
                                 )

            pygame.draw.rect(self.world, (255, 0, 255), (
                self.pos('x', self.player.rect.x),
                self.pos('y', self.player.rect.y),
                self.player.rect.width,
                self.player.rect.height), 1)

            for checkpoint in self.checkpoints:
                pygame.draw.rect(self.world, (0, 255, 255), (
                    self.pos('x', checkpoint[0]),
                    self.pos('y', checkpoint[1]),
                    checkpoint[2],
                    checkpoint[3]), 1
                                 )
            for interaction in self.interactions:
                pygame.draw.rect(self.world, (255, 255, 0), (
                    self.pos('x', interaction[0]),
                    self.pos('y', interaction[1]),
                    interaction[2],
                    interaction[3],
                ), 1
                                 )
            if self.player.collision_sprite:
                pygame.draw.rect(self.world, (0, 255, 0), (
                    self.pos('x', self.player.collision_sprite.rect.x),
                    self.pos('y', self.player.collision_sprite.rect.y),
                    self.player.collision_sprite.rect.width,
                    self.player.collision_sprite.rect.height), 1
                                 )
            if self.current_interaction is not None:
                pygame.draw.rect(self.world, (255, 0, 0), (
                    self.pos('x', self.current_interaction.x),
                    self.pos('y', self.current_interaction.y),
                    self.current_interaction.width,
                    self.current_interaction.height), 1
                                 )

        # Scale self.world to the size of the window
        scaled_game_world = pygame.transform.scale(self.world,
                                                   (int(self.window.get_width() * self.camera.last_zoom_level),
                                                    int(self.window.get_height() * self.camera.last_zoom_level)))

        # Blit the scaled game world onto the display surface
        blit_pos = ((self.window.get_width() - scaled_game_world.get_width()) // 2,
                    (self.window.get_height() - scaled_game_world.get_height()) // 2)
        self.display_surface.blit(scaled_game_world, blit_pos)

    def find_connected_blocks(self, layer):
        visited = set()
        blocks = []
        for x, y, image in layer.tiles():
            if (x, y) not in visited:
                block = self.find_block(layer, x, y, visited)
                blocks.append(block)
        return blocks

    def find_block(self, layer, x, y, visited):
        # Use a stack to perform depth-first search
        stack = [(x, y)]
        block = [x, y, 1, 1]  # x, y, width, height
        while stack:

            x, y = stack.pop()
            visited.add((x, y))
            # Check the four adjacent tiles
            if x - 1 >= 0 and (x - 1, y) not in visited and layer.data[y][x - 1] == layer.data[y][x]:  # left
                stack.append((x - 1, y))
                block[0] = min(block[0], x - 1)  # update x
                block[2] += 1  # update width
            if x + 1 < layer.width and (x + 1, y) not in visited and layer.data[y][x + 1] == layer.data[y][x]:  # right
                stack.append((x + 1, y))  # update x
                block[2] += 8  # update width
            if y - 1 >= 0 and (x, y - 1) not in visited and layer.data[y - 1][x] == layer.data[y][x]:  # up
                stack.append((x, y - 1))
                block[1] = min(block[1], y - 1)  # update y
                block[3] += 8  # update height
            if y + 1 < layer.height and (x, y + 1) not in visited and layer.data[y + 1][x] == layer.data[y][x]:  # down
                stack.append((x, y + 1))
                block[3] += 8  # update height
            # self.all_sprites.remove(self.all_sprites.get_sprites_at((x * 8, y * 8)))

        return block
