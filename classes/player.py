import pygame.sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, spawn_location, collision_sprites, damage_sprites, all_sprites):
        super().__init__()

        self.on_ground = False
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)  # Adjust the size here
        pygame.draw.circle(self.image, (255, 0, 0), (4, 4), 4)  # Adjust the circle radius here
        self.rect = self.image.get_rect(center=spawn_location)

        # groups
        self.collision_sprites = collision_sprites
        self.damage_sprites = damage_sprites
        self.all_sprites = all_sprites

        # kinematics
        self.position = pygame.math.Vector2(spawn_location)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)

        # kinematic constants
        self.HORIZ_ACCEL = .085  # wie schnell der Spieler beschleunigt
        self.HORIZ_FRIC = .5  # wie schnell der Spieler bremst

        self.last_key = None
        self.space_released = True

    def update(self):
        keys = pygame.key.get_pressed()

        # horizontal movement
        if keys[pygame.K_a] and keys[pygame.K_d]:
            if self.last_key == pygame.K_a:
                self.acceleration.x = self.HORIZ_ACCEL
            else:
                self.acceleration.x = -self.HORIZ_ACCEL
        elif keys[pygame.K_a]:
            self.acceleration.x = -self.HORIZ_ACCEL
            self.last_key = pygame.K_a
        elif keys[pygame.K_d]:
            self.acceleration.x = self.HORIZ_ACCEL
            self.last_key = pygame.K_d
        elif not keys[pygame.K_a] and not keys[pygame.K_d]:
            self.acceleration.x = 0

        self.acceleration.x -= self.velocity.x * self.HORIZ_FRIC
        self.velocity += self.acceleration

        # vertical movement + jump
        self.velocity.y += 0.008  # gravity
        if keys[pygame.K_SPACE] and self.on_ground and self.space_released:
            self.velocity.y = -.65  # jump force
            self.space_released = False
        elif not keys[pygame.K_SPACE] and self.on_ground:
            self.space_released = True



        # update y position and check for vertical collisions
        self.position.y += self.velocity.y
        self.rect.bottomleft = self.position
        collision = pygame.sprite.spritecollide(self, self.collision_sprites, False)
        if collision:
            if self.velocity.y > 0:  # moving downwards
                self.position.y = collision[0].rect.top
                self.velocity.y = 0
                self.on_ground = True
            elif self.velocity.y < 0:  # moving upwards
                self.position.y = collision[0].rect.top + self.rect.height*2
                self.velocity.y = 0
            self.rect.bottomleft = self.position
        else:
            # check if the player is on the ground by adding a small offset to their position
            self.rect.y += 1
            if pygame.sprite.spritecollide(self, self.collision_sprites, False):
                self.on_ground = True
            else:
                self.on_ground = False
            self.rect.y -= 1

        # update x position and check for horizontal collisions
        self.position.x += self.velocity.x
        self.rect.bottomleft = self.position
        collision = pygame.sprite.spritecollide(self, self.collision_sprites, False)
        if collision:
            if self.velocity.x > 0:  # moving right
                self.position.x = collision[0].rect.left - self.rect.width
            elif self.velocity.x < 0:  # moving left
                self.position.x = collision[0].rect.right

            self.velocity.x = 0
            self.rect.bottomleft = self.position
