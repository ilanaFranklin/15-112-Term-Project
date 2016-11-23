import pygame
from Rope_Class import *
import math
import random
################################################################################
# Click to draw webs
################################################################################
pygame.init()

gameDisplay = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Draw Rope")
gameExit = False
clock = pygame.time.Clock()
drawingLine = False
startTemp = None
endTemp = None


def drawWebLine(canvas, startCoord, endCoord):
    pygame.draw.aaline(canvas, (0, 0, 0), startCoord, endCoord, 2)


def lineLength(startCoord, endCoord):
    return math.sqrt(abs(endCoord[0] - startCoord[0]) + abs(endCoord[1] - startCoord[1]))


def applyWind(force, ropes):
    for rope in ropes:
        rope.applyXForce(force)

ropeList = []
wind = 50
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
                numNodes = int(lineLength(startTemp, endTemp) * 0.5)
                ropeList.append(Rope(numNodes, startTemp[0], startTemp[1],
                                     endTemp[0], endTemp[1]))
    if drawingLine:
        drawWebLine(gameDisplay, startTemp, pygame.mouse.get_pos())
    # applyWind(wind, ropeList)
    # wind = random.randint(1, 100)
    for rope in ropeList:
        rope.updateRope()
        rope.drawRope(gameDisplay)
    pygame.display.update()
    clock.tick(150)

pygame.quit
quit
