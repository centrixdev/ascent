import pygame
import pygame_gui


class UI_manager:
    def __init__(self, screen, window):
        self.is_paused = None
        self.manager = pygame_gui.UIManager((screen[0], screen[1]))
        self.window = window
        self.debug = None
        self.setup()

    def setup(self):
        self.debug = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((10, 10), (-1, -1)),
                                                       text='',
                                                       manager=self.manager)

    def process_events(self, event):
        self.manager.process_events(event)

    def update(self, deltaTime):
        self.debug.set_text("FPS: " + str(round((1/deltaTime)*60)))  # deltaTime = 1 bei 60fps
        self.manager.update(deltaTime)


    def draw(self):
        if self.is_paused:
            return
        self.manager.draw_ui(self.window)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
