import pygame
import math
import random
################################################################################
# Pygame Tech Demo
# Uses Pygame and physics Simulation
################################################################################

pygame.init()

gameDisplay = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Rope Simulation")

gameExit = False
clock = pygame.time.Clock()


class Node(object):

    def __init__(self, startX, startY):
        self.x = startX
        self.y = startY
        self.mass = 300
        self.xVel = 0
        self.yVel = 0
        self.xForce = 0
        self.yForce = 0

    def applyYForce(self, force):
        self.yForce += force

    def applyXForce(self, force):
        self.xForce += force

    def moveMass(self):
        self.yVel += (self.yForce / self.mass) * 0.3
        self.y += int(self.yVel * 0.3)
        self.xVel += (self.xForce / self.mass) * 0.3
        self.x += int(self.xVel * 0.3)

    def drawNode(self, gameDisplay):
        pygame.draw.circle(gameDisplay, (0, 0, 0), [
            self.x, self.y], 2)


class Spring(object):

    def __init__(self, mass1, mass2):
        self.m1 = mass1
        self.m2 = mass2
        self.length = 1
        self.k = 425
        self.friction = 280

    def drawSpring(self, gameDisplay, color=(38, 145, 170)):
        pygame.draw.line(gameDisplay, color,
                         (self.m1.x, self.m1.y), (self.m2.x, self.m2.y), 1)

    def solveSpring(self):
        forceY = 0
        forceX = 0
        yLength = self.m2.y - self.m1.y
        xLength = self.m2.x - self.m1.x
        vector = math.sqrt(yLength**2 + xLength**2)
        if abs(vector) > 0:
            # Set corrective Y spring forces
            forceY += -(yLength / abs(vector)) * \
                (abs(vector) - self.length) * self.k
            # Add in Y spring friction
            forceY += (self.m1.yVel - self.m2.yVel) * self.friction
            # Set corrective X spring forces
            forceX += -(xLength / abs(vector)) * \
                (abs(vector) - self.length) * self.k
            # Add in X spring friction
            forceX += (self.m1.xVel - self.m2.xVel) * self.friction
        self.m1.applyYForce(-forceY)
        self.m2.applyYForce(forceY)
        self.m1.applyXForce(-forceX)
        self.m2.applyXForce(forceX)


class Rope(object):

    def __init__(self, numNodes, x0, y0, x1, y1):
        self.numNodes = numNodes
        # Set the leftmost node as the startNode
        if x1 < x0:
            startX, startY = x1, y1
            endX, endY = x0, y0
        else:
            startX, startY = x0, y0
            endX, endY = x1, y1
        self.startNode = Node(startX, startY)
        self.endNode = Node(endX, endY)
        # Create list of nodes
        slopeY = int((endY - startY) / numNodes)
        slopeX = int((endX - startX) / numNodes)
        self.nodeList = []
        for node in range(numNodes):
            self.nodeList.append(
                Node(startX + slopeX * node, startY + slopeY * node))
        # Connect all nodes with springs to create rope
        self.springList = [Spring(self.startNode, self.nodeList[0])]
        for spring in range(numNodes - 1):
            self.springList.append(
                Spring(self.nodeList[spring], self.nodeList[spring + 1]))
        self.springList.append(
            Spring(self.nodeList[len(self.nodeList) - 1], self.endNode))

    def updateRope(self):
        for node in self.nodeList:
            node.xForce = 0
            node.yForce = 0
            node.applyYForce(7 * node.mass)
        for spring in self.springList:
            spring.solveSpring()
        for node in self.nodeList:
            node.moveMass()

    def drawRope(self, gameDisplay):
        for spring in self.springList:
            spring.drawSpring(gameDisplay)
        # for node in self.nodeList:
        #     node.drawNode(gameDisplay)

ropeList = [
    Rope(15, 0, 200, 1000, 200),
    Rope(15, 50, 100, 1000, 400),
    Rope(15, 0, 400, 1000, 20),
    Rope(10, 0, 150, 1000, 200),
    Rope(15, 60, 50, 800, 50)]
while not gameExit:
    gameDisplay.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
    for rope in ropeList:
        rope.updateRope()
        rope.drawRope(gameDisplay)
    pygame.display.update()
    clock.tick(150)

pygame.quit
quit
