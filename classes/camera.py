import random

import pygame


class Camera:
    def __init__(self, player, all_sprites):
        self.start_sequence_duration = 0
        self.start_initiated = False
        self.INTERACTION_ZOOM = 1.125
        self.INTERACTION_CAMERA_SPEED = 2

        self.DEATH_ZOOM = 1.5
        self.DEATH_CAMERA_SPEED = .1

        self.START_ZOOM = 3
        self.START_CAMERA_SPEED = 1

        self.PLAY_CAMERA_SPEED = 0.05
        self.last_camera_pos = (0, 0)
        self.new_camera_pos = (0, 0)
        self.last_zoom_level = 1
        self.zoom_level = 1
        self.camera_speed = self.PLAY_CAMERA_SPEED

        self.shake_timer = 0
        self.shake_intensity = 0

        self.player = player
        self.all_sprites = all_sprites

    def shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_timer = duration
    def focus(self, focus_obj):
        if focus_obj == 'player':
            self.new_camera_pos = (self.player.hitbox.x + self.player.hitbox.width // 2,
                                   self.player.hitbox.y + self.player.hitbox.height // 2)
        elif focus_obj == 'screens':
            vert_screens = (self.player.hitbox.y // 150)
            # vert_screens = 1 if vert_screens == 0 else vert_screens
            vert_cam_pos = -30 + vert_screens * 270

            horiz_screens_r = ((self.player.hitbox[0] + 10) // 320)

            horiz_screens_l = ((self.player.hitbox[0] - 10) // 320)
            horiz_screens_l = 1 if horiz_screens_l == 0 else horiz_screens_l

            if self.player.velocity.x < 0:
                self.focus((horiz_screens_l * 320 + 160, vert_cam_pos))
            elif self.player.velocity.x >= 0:
                self.focus((horiz_screens_r * 320 + 160, vert_cam_pos))


        else:
            self.new_camera_pos = focus_obj

    def zoom(self, level=''):
        if level == 'interaction':
            self.zoom_level = self.INTERACTION_ZOOM
            self.camera_speed = self.INTERACTION_CAMERA_SPEED
        elif level == 'death':
            self.zoom_level = self.DEATH_ZOOM
            self.camera_speed = self.DEATH_CAMERA_SPEED
        elif level == 'start':
            self.zoom_level = self.START_ZOOM
            self.camera_speed = self.START_CAMERA_SPEED
        else:
            self.zoom_level = 1
            self.camera_speed = self.PLAY_CAMERA_SPEED

    def update(self, deltaTime, start_sequence):
        if self.start_sequence_duration == 0:
            self.start_sequence_duration = start_sequence

        if self.shake_timer > 0:
            self.shake_timer -= deltaTime
            self.last_camera_pos = (
                self.last_camera_pos[0] + random.uniform(-self.shake_intensity, self.shake_intensity),
                self.last_camera_pos[1] + random.uniform(-self.shake_intensity, self.shake_intensity)
            )
        else:
            self.shake_intensity = 0

        if self.player:
            if start_sequence > 0:
                if start_sequence > self.start_sequence_duration-1:
                    self.start_initiated = True
                    self.zoom('start')
                    self.focus('player')
            elif self.start_initiated:
                self.start_initiated = False
                self.player.start = True
                self.zoom()
                self.focus('screens')
            elif self.player.is_dead:
                self.zoom('death')
                self.focus('player')
            else:
                if self.player.position == self.player.spawn_location:
                    self.zoom()
                self.focus('screens')
                self.camera_speed = self.PLAY_CAMERA_SPEED
        camera_pos = self.last_camera_pos
        if self.new_camera_pos != self.last_camera_pos:
            camera_pos = (
                self.lerp(self.last_camera_pos[0], self.new_camera_pos[0], deltaTime),
                self.lerp(self.last_camera_pos[1], self.new_camera_pos[1], deltaTime)
            )

        self.all_sprites.center(camera_pos)

        self.last_camera_pos = camera_pos
        self.last_zoom_level += (self.zoom_level - self.last_zoom_level) * .075 * deltaTime

    def lerp(self, a, b, deltaTime):

        return a + (b - a) * self.camera_speed * deltaTime
