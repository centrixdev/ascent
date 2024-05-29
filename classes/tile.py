import pygame


def check_collision(sprite, group):
    for collision_sprite in group:
        if sprite.rect.colliderect(collision_sprite.rect):
            return collision_sprite
    return None


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups, height, width, right, down, image=None):
        super().__init__(*groups)
        self.image = image
        if down:
            self.rect = pygame.Rect(x, y + height, width, height)
        elif right:
            self.rect = pygame.Rect(x + width, y, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)


# class FallingTile(Tile):
#     def __init__(self, x, y, images, *groups, height, width, right, down):
#
#         super().__init__(x, y, *groups, height=height, width=width, right=right, down=down)
#
#         self.images = images
#         # self.image =
#
#
#
#         self.is_falling = False
#         self.fall_speed = 0
#         self.fall_time = 0
#
#     def animate(self, deltaTime):
#         collision = check_collision(self, self.groups()[0])
#         if collision and FallingTile != type(collision):
#             self.is_falling = False
#             return
#         self.fall_time += deltaTime
#         self.rect.y += self.fall_speed * deltaTime
#         self.fall_speed += 0.1 * deltaTime
#         if self.fall_time > 1000:
#             self.kill()
#
#     def draw_fall(self, surface):
#         # Draw the image at the rect's position
#         for i in range(self.rows):
#             for j in range(self.columns):
#                 self.image.blit(self.images[0], (i * 8, j * 8))

class FallingTile(pygame.sprite.Sprite):
    def __init__(self, rects, images, *groups):

        super().__init__(*groups)
        self.image = pygame.Surface()
        self.images = images
        self.tiles = [

        ]


        self.is_falling = False
        self.fall_speed = 0
        self.fall_time = 0

    def animate(self, deltaTime):
        for rect in self.rects:
            collision = check_collision(rect, self.groups()[0])
            if collision and FallingTile != type(collision):
                self.is_falling = False
                return
        self.fall_time += deltaTime
        for rect in self.rects:
            rect.y += self.fall_speed * deltaTime
        self.fall_speed += 0.1 * deltaTime
        if self.fall_time > 1000:
            self.kill()

