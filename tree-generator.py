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
                [[int(startPoint[0]), int(startPoint[1])], [int(endPoint[0]), int(endPoint[1])], depth])
            if depth <= numBranches - 2:
                rand = random.randint(0, 15)
                if rand == 0:
                    return None
            treeHelper(depth - 1, endPoint, minLength - 10 if minLength > 20 else 20,
                       maxLength - 10 if maxLength > 40 else 40, angle + random.randint(10, 25))
            treeHelper(depth - 1, endPoint, minLength - 10 if minLength > 10 else 20,
                       maxLength - 10 if maxLength > 20 else 40, angle - random.randint(10, 25))
    treeHelper(numBranches, startPoint, 50, 100)
    return branchList


def scaleTree(tree, scale):
    for i in range(len(tree)):
        # if i == 0:
        #         print(tree[i][1][0])
        #         tree[i][1][0] *= scale
        #         tree[i][1][1] *= scale
        #         tree[i][2] *= scale
        # else:
        for coord in tree[i]:
            if isinstance(coord, int):
                print(coord)
                coord = scale
            else:
                coord[0] *= scale
                coord[1] += scale

def drawTree(gameDisplay, branchList):
    for branch in branchList:
        pygame.draw.line(gameDisplay, (0, 0, 0), branch[
                         0], branch[1], branch[2])


branches = makeRecursiveTree((500, 550), 8)
while not gameExit:
    gameDisplay.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == pygame.KEYDOWN:
            branches = makeRecursiveTree((500, 550), random.randint(6, 8))
            print(branches)
        if event.type == pygame.MOUSEBUTTONDOWN:
            scaleTree(branches, 2)
            print(branches)
    drawTree(gameDisplay, branches)
    pygame.display.update()
