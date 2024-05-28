import pygame.sprite

vec = pygame.math.Vector2


class Player(pygame.sprite.Sprite):
    def __init__(self, spawn_location, level):
        super().__init__()
        # player animations

        self.level = level
        self.deaths = level.deaths
        self.start = False
        self.counter = 0
        self.collision_sprite = None
        self.jump = False
        self.platform = None

        idle_image = pygame.image.load('graphics/player/idle.png').convert_alpha()
        run_init_image = pygame.image.load('graphics/player/run_init.png').convert_alpha()
        run_image = pygame.image.load('graphics/player/run.png').convert_alpha()
        death_image = pygame.image.load('graphics/player/death.png').convert_alpha()
        start_image = pygame.image.load('graphics/player/starting_animation.png').convert_alpha()

        dash_up_image = pygame.image.load('graphics/player/dash/up.png').convert_alpha()
        dash_down_image = pygame.image.load('graphics/player/dash/down.png').convert_alpha()
        dash_horiz_image = pygame.image.load('graphics/player/dash/horiz.png').convert_alpha()
        dash_diag_up_image = pygame.image.load('graphics/player/dash/diag_up.png').convert_alpha()
        dash_diag_down_image = pygame.image.load('graphics/player/dash/diag_down.png').convert_alpha()





        self.frame_counter = 0  # used to slow down the animation
        self.animation_state = 'idle'

        self.idle_frames = [idle_image.subsurface(pygame.Rect(0, 0, 32, 32))]

        self.run_init_frames = self.get_frames(run_init_image)
        self.run_frames = self.get_frames(run_image)

        self.death_frames = self.get_frames(death_image)
        self.start_frames = self.get_frames(start_image)

        self.dash_up_frames = self.get_frames(dash_up_image)
        self.dash_down_frames = self.get_frames(dash_down_image)
        self.dash_horiz_frames = self.get_frames(dash_horiz_image)
        self.dash_diag_up_frames = self.get_frames(dash_diag_up_image)
        self.dash_diag_down_frames = self.get_frames(dash_diag_down_image)

        self.is_dead = False

        self.spawn_location = spawn_location
        self.image = self.idle_frames[0]
        self.frame_index = 0

        # rects
        self.rect = self.image.get_frect(topleft=spawn_location)
        self.hitbox = pygame.Rect(0, 0, 14, 10)
        self.old_hitbox = self.hitbox.copy()
        self.update_hitbox()

        # collision
        self.on_surface = {'floor': False, 'right': False, 'left': False}
        self.collision_sprites = level.collision_sprites

        # kinematics
        self.position = vec(spawn_location)
        self.velocity = vec(0, 0)
        self.acceleration = vec(0, 0)

        # kinematic constants
        self.HORIZ_ACCEL = .35  # wie schnell der Spieler beschleunigt
        self.HORIZ_FRIC = .3  # wie schnell der Spieler bremst

        self.last_key = None
        self.space_released = True

        self.dash_time = 0
        self.dash_direction = vec(0, 0)
        self.DASH_ACCEL = 15
        self.DASH_SPEED_HORIZ = .25
        self.DASH_SPEED = .17
        self.dash_left = 1

        self.GRAVITY = 0.125
        self.JUMP_FORCE = -2.5

    def get_frames(self, image):
        return [image.subsurface(pygame.Rect(i * 32, 0, 32, 32)) for i in range(image.get_width() // 32)]

    def update_hitbox(self):
        self.old_hitbox = self.hitbox.copy()
        # Adjust the position of the collision rectangle relative to the sprite rectangle
        self.hitbox.bottomleft = self.rect.bottomleft + vec(9, 0)

    def input(self, deltaTime):
        keys = pygame.key.get_pressed()
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

        if keys[pygame.K_SPACE] and self.on_surface['floor']:
            self.velocity.y = self.JUMP_FORCE
            self.space_released = False
        elif not keys[pygame.K_SPACE] and self.on_surface['floor']:
            self.space_released = True

        # dash
        if keys[pygame.K_LSHIFT] and self.dash_left > 0:
            self.dash_time = 0.2 * (1 / deltaTime)  # dash duration in seconds
            self.dash_direction = vec(0, 0)
            if keys[pygame.K_w] and keys[pygame.K_a]:
                self.dash_direction = vec(-self.DASH_SPEED, -self.DASH_SPEED)
            elif keys[pygame.K_w] and keys[pygame.K_d]:
                self.dash_direction = vec(self.DASH_SPEED, -self.DASH_SPEED)
            elif keys[pygame.K_s] and keys[pygame.K_a]:
                self.dash_direction = vec(-self.DASH_SPEED, self.DASH_SPEED)
            elif keys[pygame.K_s] and keys[pygame.K_d]:
                self.dash_direction = vec(self.DASH_SPEED, self.DASH_SPEED)
            elif keys[pygame.K_a]:
                self.dash_direction.x = -self.DASH_SPEED_HORIZ
            elif keys[pygame.K_d]:
                self.dash_direction.x = self.DASH_SPEED_HORIZ
            elif keys[pygame.K_w]:
                self.dash_direction.y = -self.DASH_SPEED
            elif keys[pygame.K_s]:
                if self.on_surface['floor']:
                    return
                self.dash_direction.y = self.DASH_SPEED

            elif not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_w] and not keys[pygame.K_s]:
                self.dash_direction.y = -self.DASH_SPEED
            self.dash_left -= 1

        if self.dash_time > 0:
            self.level.camera.shake(.5, .05)
            self.velocity = self.dash_direction * self.DASH_ACCEL
            self.dash_time -= 0.02
        elif self.on_surface['floor'] and self.dash_left == 0 and not keys[pygame.K_LSHIFT]:
            self.dash_left += 1

    def check_contact(self):
        floor_rect = pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 2))
        right_rect = pygame.Rect(self.hitbox.topright + vec(0, self.hitbox.height / 4),
                                 (2, self.hitbox.height / 2))
        left_rect = pygame.Rect(self.hitbox.topleft + vec(-2, self.hitbox.height / 4),
                                (2, self.hitbox.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        # collisions
        self.on_surface['floor'] = True if floor_rect.collidelist(
            collide_rects) >= 0 and self.velocity.y >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left'] = True if left_rect.collidelist(collide_rects) >= 0 else False

        self.platform = None
        sprites = self.collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis):
        # check if player is on far left
        if self.hitbox.left < 0:
            self.hitbox.left = 0
            if self.velocity.x < 0:
                self.velocity.x = 0

        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox):
                self.collision_sprite = sprite
                if axis == 'horizontal':
                    # left
                    if self.hitbox.left <= sprite.rect.right and int(self.old_hitbox.left) >= int(
                            sprite.rect.right):
                        self.hitbox.x = sprite.rect.right
                        if self.velocity.x < 0:
                            self.velocity.x = 0

                    # right
                    if self.hitbox.right >= sprite.rect.left and int(self.old_hitbox.right) <= int(
                            sprite.rect.left):
                        self.hitbox.x = sprite.rect.left - self.hitbox.width
                        if self.velocity.x > 0:
                            self.velocity.x = 0  # Stop horizontal movement

                else:  # vertical
                    # top
                    if self.hitbox.top <= sprite.rect.bottom and int(self.old_hitbox.top) >= int(
                            sprite.rect.bottom):
                        self.hitbox.top = sprite.rect.bottom
                        if self.velocity.y < 0:
                            self.velocity.y = 0

                        if hasattr(sprite, 'moving'):
                            self.hitbox.top += 6

                    # bottom
                    if self.hitbox.bottom >= sprite.rect.top and int(self.old_hitbox.bottom) <= int(
                            sprite.rect.top):
                        if self.level.falling_sprites.has(sprite):
                            sprite.is_falling = True

                        self.position.y = sprite.rect.top
                        self.velocity.y = 0  # Set vertical velocity to zero

    def move(self, deltaTime):
        if not self.on_surface['floor']:
            self.velocity.y += self.GRAVITY * deltaTime  # gravity
        if self.is_dead:
            self.velocity = vec(0, 0)
        self.collision('horizontal')
        self.position.x += self.velocity.x * deltaTime

        self.collision('vertical')
        self.position.y += self.velocity.y * deltaTime

        self.rect.bottomleft = self.position

    def animate(self, deltaTime):
        flip_image = self.velocity.x < 0  # flip image if moving left

        if not self.start:
            if self.animation_state != 'start' and not self.animation_state == 'start_finished':
                self.frame_counter = 0
                self.frame_index = 0

            self.animation_state = 'start'
            self.frame_counter += deltaTime
            if self.frame_index == 0 or self.frame_index == 6 or self.frame_index == 12:
                if self.frame_counter >= 100:
                    self.frame_index += 1
                    self.frame_counter = 0
            elif self.frame_counter >= 5:  # change frame every 0.1 seconds
                self.frame_index += 1
                self.frame_counter = 0
            if self.frame_index >= len(self.start_frames):  # start animation has finished
                self.animation_state = 'start_finished'
                self.image = self.idle_frames[0]
            else:
                self.image = pygame.transform.flip(self.start_frames[self.frame_index], flip_image, False)




        elif self.is_dead:  # player is dead
            if self.animation_state != 'death':
                self.frame_counter = 0
                self.frame_index = 0
                self.animation_state = 'death'
                # not animating logic
                self.deaths += 1
            self.frame_counter += deltaTime
            self.velocity = vec(0, 0)
            self.acceleration = vec(0, 0)
            if self.frame_counter >= 5:  # change frame every 0.1 seconds
                self.frame_index = (self.frame_index + 1) % len(self.death_frames)
                self.frame_counter = 0
            self.image = pygame.transform.flip(self.death_frames[self.frame_index], flip_image, False)
            # when death animation is finished, reset player
            if self.frame_index == len(self.death_frames) - 1:
                self.position = vec(self.spawn_location)
                self.is_dead = False


        elif self.dash_time > 0 or self.animation_state == 'dash' or self.animation_state == 'dash_finish':
            if self.animation_state != 'dash' and self.animation_state != 'dash_finish':
                self.frame_counter = 0
                self.frame_index = 0
                self.animation_state = 'dash'
            self.frame_counter += deltaTime
            change_rate = 0
            if self.frame_index <= 3:
                change_rate = 2
            elif self.frame_index <= 6 or self.frame_index >= 11:
                change_rate = 5
            else:
                if self.on_surface['floor'] or self.animation_state == 'dash_finish' or self.dash_direction.y >= 0:
                    self.animation_state = 'dash_finish'
                    change_rate = 2
                else:
                    change_rate = 999

            if self.frame_counter >= change_rate:
                self.frame_index += 1
                self.frame_counter = 0
            if self.frame_index >= len(self.dash_up_frames):
                self.frame_index = 0
                self.animation_state = 'idle'

            # determine which direction the player is dashing
            flip_image = self.dash_direction.x < 0
            if self.dash_direction.x == 0:  # vertical dash
                if self.dash_direction.y > 0:  # down
                    self.image = pygame.transform.flip(self.dash_down_frames[self.frame_index], False, False)
                else:  # up
                    self.image = pygame.transform.flip(self.dash_up_frames[self.frame_index], False, False)
            elif self.dash_direction.y == 0:  # horizontal dash
                self.image = pygame.transform.flip(self.dash_horiz_frames[self.frame_index], flip_image, False)
            else: # diagonal dash
                if self.dash_direction.y > 0: # down
                    self.image = pygame.transform.flip(self.dash_diag_down_frames[self.frame_index], flip_image, False)
                else: # up
                    self.image = pygame.transform.flip(self.dash_diag_up_frames[self.frame_index], flip_image, False)
        elif round(self.velocity.x) != 0:  # player is moving
            if self.animation_state == 'idle':  # player starts running
                self.animation_state = 'run_init'
                self.frame_index = 0
                self.frame_counter = 0
            if self.animation_state == 'run_init':  # player is in run_init state
                self.frame_counter += deltaTime
                if self.frame_counter >= 3:  # change frame every 0.1 seconds
                    self.frame_index += 1
                    self.frame_counter = 0
                if self.frame_index >= len(self.run_init_frames):  # run_init animation has finished
                    self.animation_state = 'run'
                    self.frame_index = 0
                self.image = pygame.transform.flip(self.run_init_frames[self.frame_index], flip_image, False)
            else:  # player is in run state
                self.frame_counter += deltaTime
                if self.frame_counter >= 5:  # change frame every 0.1 seconds
                    self.frame_index = (self.frame_index + 1) % len(self.run_frames)
                    self.frame_counter = 0
                self.image = pygame.transform.flip(self.run_frames[self.frame_index], flip_image, False)
        else:  # player is idle
            self.animation_state = 'idle'
            self.image = self.idle_frames[0]
            self.frame_counter = 0  # reset counter when idle

    def update(self, deltaTime):

        self.update_hitbox()

        # limit deltaTime to prevent bugs (tabbing out)
        if deltaTime > 50:
            return

        if self.start:
            self.input(deltaTime)

        self.move(deltaTime)

        self.check_contact()
        self.collision(deltaTime)

        self.animate(deltaTime)
