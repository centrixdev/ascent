import sys

import pygame
class Start:
    def __init__(self, window, show_splash):
        self.window = window
        self.clock = pygame.time.Clock()
        self.in_splash = show_splash
        self.font = pygame.font.Font(None, 36)
        self.options = ["Start", "Options", "Exit"]
        self.current_option = 0


    def draw(self):
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.current_option else (100, 100, 100)
            text_surface = self.font.render(option, True, color)
            self.window.blit(text_surface, (100, 100 + i * 40))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.current_option = (self.current_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.current_option = (self.current_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.current_option == 0:
                    return "start"
                elif self.current_option == 1:
                    return "options"
                elif self.current_option == 2:
                    return "quit"
    def run(self):
        run = True
        while run:
            deltaTime = self.clock.tick(240) / 1000 * 60  # framerate independence
            if self.in_splash:
                self.window.fill((0, 0, 0))
                text = self.font.render("Press Enter to start", True, (255, 255, 255))
                text_rect = text.get_rect(center=(640, 360))
                self.window.blit(text, text_rect)

                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.in_splash = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"
                    result = self.handle_event(event)
                    if result is not None:
                        return result
                self.window.fill((0, 0, 0))
                self.draw()
                pygame.display.flip()

        pygame.quit()
        exit()
