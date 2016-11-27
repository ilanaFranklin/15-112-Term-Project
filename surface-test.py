import pygame

pygame.init()

gameDisplay = pygame.display.set_mode((1000, 600))
gameExit = False
surface = pygame.Surface((1000, 1000))
surface.fill((255, 0, 0))
pygame.draw.circle(surface, (0, 0, 0), [100, 100], 50)
surface.set_colorkey((255, 0, 0))

width = 1000
height = 1000

while not gameExit:
    gameDisplay.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == pygame.KEYDOWN:
            print("HERE")
            width -= 20
            height -= 20
            surface = pygame.transform.scale(surface, (width, height))
            print(surface.get_width())
    gameDisplay.blit(surface, (50, 50))
    pygame.display.update()
