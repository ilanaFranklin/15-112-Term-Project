import pygame
import random
import math

pygame.init()

gameDisplay = pygame.display.set_mode((1000, 600))
gameExit = False


def makeRecursiveTree(startPoint, numBranches):
    branchList = []
    def treeHelper(depth, startPoint, minLength, maxLength, angle=90 + random.randint(-5, 5)):
        if depth == 0:
            return None
        else:
            length = random.randint(minLength, maxLength)
            tempX = length * math.cos(math.radians(angle))
            tempY = length * math.sin(math.radians(angle))
            endPoint = (startPoint[0] + tempX, startPoint[1] - tempY)
            branchList.append(
                [(int(startPoint[0]), int(startPoint[1])), (int(endPoint[0]), int(endPoint[1])), depth])
            if depth <= numBranches - 2:
                rand = random.randint(0, 10)
                if rand == 0:
                    return None
            treeHelper(depth - 1, endPoint, minLength - 10 if minLength > 20 else 20,
                       maxLength - 10 if maxLength > 40 else 40, angle + random.randint(15, 25))
            treeHelper(depth - 1, endPoint, minLength - 10 if minLength > 10 else 20,
                       maxLength - 10 if maxLength > 20 else 40, angle - random.randint(15, 25))
    treeHelper(numBranches, startPoint, 50, 100)
    return branchList


def drawTree(gameDisplay, branchList):
    for branch in branchList:
        pygame.draw.line(gameDisplay, (0, 0, 0), branch[0], branch[1], branch[2])


branches = makeRecursiveTree((500, 550), 8)
while not gameExit:
    gameDisplay.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == pygame.KEYDOWN:
            branches = makeRecursiveTree((500, 550), random.randint(5, 8))
            print(branches)
    drawTree(gameDisplay, branches)
    pygame.display.update()
