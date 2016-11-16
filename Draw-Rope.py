import pygame
from Rope_Class import *
import math
pygame.init()

gameDisplay = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Draw Rope")
gameExit = False
clock = pygame.time.Clock()
drawingLine = False
startTemp = None
endTemp = None

ropeList = []
while not gameExit:
    gameDisplay.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not drawingLine:
                drawingLine = True
                startTemp = pygame.mouse.get_pos()
            else:
                drawingLine = False
                endTemp = pygame.mouse.get_pos()
                ropeList.append(Rope(12, startTemp[0], startTemp[1],
                                     endTemp[0], endTemp[1]))
    for rope in ropeList:
        rope.updateRope()
        rope.drawRope(gameDisplay)
    pygame.display.update()
    clock.tick(150)

pygame.quit
quit
