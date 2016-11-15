import pygame
import math

# ehhhh

pygame.init()

gameDisplay = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Rope Simulation")

gameExit = False
clock = pygame.time.Clock()


class Node(object):

    def __init__(self, startX, startY):
        self.x = startX
        self.y = startY
        self.mass = 50
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
            self.x, self.y], 5)


class Spring(object):

    def __init__(self, mass1, mass2):
        self.m1 = mass1
        self.m2 = mass2
        self.length = 2
        self.k = 150
        self.friction = 60

    def drawSpring(self, gameDisplay):
        pygame.draw.line(gameDisplay, (0, 0, 0), (self.m1.x,
                                                  self.m1.y), (self.m2.x, self.m2.y), 8)

    def solveSpring(self):
        forceY = 0
        forceX = 0
        yLength = self.m2.y - self.m1.y
        xLength = self.m2.x - self.m1.x
        vector = math.sqrt(yLength**2 + xLength**2)
        if abs(vector) > 0:
            forceY += -(yLength / abs(vector)) * \
                (abs(vector) - self.length) * self.k
            forceY += (self.m1.yVel - self.m2.yVel) * self.friction
            forceX += -(xLength / abs(vector)) * \
                (abs(vector) - self.length) * self.k
            forceX += (self.m1.xVel - self.m2.xVel) * self.friction
        self.m1.applyYForce(-forceY)
        self.m2.applyYForce(forceY)
        self.m1.applyXForce(-forceX)
        self.m2.applyXForce(forceX)
basicNode = Node(200, 0)
nodeList  = []
for i in range(15):
    nodeList.append(Node(500 + i, 0))
endNode = Node(600, 110)
springList = []
springList.append(Spring(basicNode, nodeList[0]))
for i in range(14):
    springList.append(Spring(nodeList[i], nodeList[i+1]))
springList.append(Spring(nodeList[len(nodeList) - 1], endNode))

while not gameExit:
    gameDisplay.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
    for node in nodeList:
        node.xForce = 0
        node.yForce = 0
        node.applyYForce(9.81 * node.mass)
    for spring in springList:
        spring.solveSpring()
    for node in nodeList:
        node.moveMass()
        # node.drawNode(gameDisplay)
    for spring in springList:
        spring.drawSpring(gameDisplay)
    pygame.display.update()
    clock.tick(100)

pygame.quit

quit
