import pygame.sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, spawn_location, win, collision_sprites, damage_sprites, all_sprites):
        super().__init__()
        self.has_won = False
        self.spawn_location = spawn_location
        self.win = win
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
        self.HORIZ_ACCEL = .25   # wie schnell der Spieler beschleunigt
        self.HORIZ_FRIC = .175  # wie schnell der Spieler bremst

        self.last_key = None
        self.space_released = True

        self.dash_time = 0
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.DASH_SPEED = 10
        self.can_dash = True

        self.GRAVITY = 0.125
        self.JUMP_FORCE = -2.5


    def update(self, deltaTime):

        keys = pygame.key.get_pressed()

        if deltaTime > 50:  # pause when tabbed out
            return
        # horizontal movement
        if keys[pygame.K_a] and keys[pygame.K_d]:
            if self.last_key == pygame.K_a:
                self.acceleration.x = self.HORIZ_ACCEL * deltaTime
            else:
                self.acceleration.x = -self.HORIZ_ACCEL * deltaTime
        elif keys[pygame.K_a]:
            if self.velocity.x > 0:  # moving right, need to decelerate first
                self.acceleration.x = -self.HORIZ_ACCEL * deltaTime
            else:  # moving left or stationary, can accelerate
                self.acceleration.x = -self.HORIZ_ACCEL * deltaTime
            self.last_key = pygame.K_a
        elif keys[pygame.K_d]:
            if self.velocity.x < 0:  # moving left, need to decelerate first
                self.acceleration.x = self.HORIZ_ACCEL * deltaTime
            else:  # moving right or stationary, can accelerate
                self.acceleration.x = self.HORIZ_ACCEL * deltaTime
            self.last_key = pygame.K_d
        elif not keys[pygame.K_a] and not keys[pygame.K_d]:
            self.acceleration.x = 0

        self.acceleration.x -= self.velocity.x * self.HORIZ_FRIC * deltaTime
        self.velocity += self.acceleration

        # vertical movement + jump
        self.velocity.y += self.GRAVITY * deltaTime  # gravity
        if keys[pygame.K_SPACE] and self.on_ground and self.space_released:
            self.velocity.y = self.JUMP_FORCE
            self.space_released = False
        elif not keys[pygame.K_SPACE] and self.on_ground:
            self.space_released = True

        # dash
        if keys[pygame.K_LSHIFT] and self.can_dash:
            self.dash_time = 0.2 * (1/deltaTime)  # dash duration in seconds
            self.dash_direction = pygame.math.Vector2(0, 0)
            if keys[pygame.K_a]:
                self.dash_direction.x = -.25
            elif keys[pygame.K_d]:
                self.dash_direction.x = .25
            if keys[pygame.K_w]:
                self.dash_direction.y = -.25
            elif keys[pygame.K_s]:
                self.dash_direction.y = .25
            if not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_w] and not keys[pygame.K_s]:
                self.dash_direction.y = -.25
            self.can_dash = False

        if self.dash_time > 0:
            self.velocity = self.dash_direction * self.DASH_SPEED
            self.dash_time -= 0.02
        elif self.on_ground and not keys[pygame.K_LSHIFT]:
            self.can_dash = True


        # update y position and check for vertical collisions
        self.position.y += self.velocity.y * deltaTime
        self.rect.bottomleft = self.position
        collision = pygame.sprite.spritecollide(self, self.collision_sprites, False)
        if collision:
            if self.velocity.y > 0:  # moving downwards
                self.position.y = collision[0].rect.top
                self.velocity.y = 0
                self.on_ground = True
            elif self.velocity.y < 0:  # moving upwards
                self.position.y = collision[0].rect.top + self.rect.height * 2
                self.velocity.x += self.velocity.y * self.acceleration.x
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
        self.position.x += self.velocity.x * deltaTime
        self.rect.bottomleft = self.position
        collision = pygame.sprite.spritecollide(self, self.collision_sprites, False)
        if collision:
            if self.velocity.x > 0:  # moving right
                self.position.x = collision[0].rect.left - self.rect.width
            elif self.velocity.x < 0:  # moving left
                self.position.x = collision[0].rect.right

            self.velocity.x = 0
            self.rect.bottomleft = self.position

        # check for damage
        damage = pygame.sprite.spritecollide(self, self.damage_sprites, False)
        if damage:
            self.position = pygame.math.Vector2(self.spawn_location)
            self.velocity = pygame.math.Vector2(0, 0)
            self.rect.bottomleft = self.position
            self.on_ground = False
            self.can_dash = True
            self.dash_time = 0

        # check for win
        if (self.rect.x < self.win[0] + self.win[2] and self.rect.x + self.rect.width > self.win[0] and
                self.rect.y < self.win[1] + self.win[3] and self.rect.y + self.rect.height > self.win[1]):
            self.has_won = True
            print("player won!")
