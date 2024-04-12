import pygame, sys
from pytmx.util_pygame import load_pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
tmx_data = load_pygame("levels/data/tmx/level0.tmx")
layer = tmx_data.get_layer_by_name("Graybox")
for x,y,surf in layer.tiles():
    print(x*8)
    print(y*8)
    print(surf)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill("black")
    pygame.display.update()
