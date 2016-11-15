import pygame
import math

# ehhhh

pygame.init()

gameDisplay = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Rope Simulation")

gameExit = False
clock = pygame.time.Clock()


class Node(object):

    def __init__(self, startX, startY):
        self.x = startX
        self.y = startY
        self.mass = 5
        self.xVel = 0
        self.yVel = 0
        self.xForce = 0
        self.yForce = 0

    def applyYForce(self, force):
        self.yForce += force

    def applyXForce(self, force):
        self.xForce += force

    def moveMass(self):
        self.yVel += (self.yForce / self.mass) * 0.2
        self.y += int(self.yVel * 0.2)
        self.xVel += (self.xForce / self.mass) * 0.2
        self.x += int(self.xVel * 0.2)


class Spring(object):

    def __init__(self, mass1, mass2):
        self.m1 = mass1
        self.m2 = mass2

    def solveSpring(self):
        forceY = 0
        yLength = self.m2.y - self.m1.y
        xLength = self.m2.x - self.m1.x
        vector = math.sqrt(yLength**2 + xLength**2)
        if abs(vector) > 10:
            forceY += -(yLength / abs(vector)) * (abs(vector) - 50) * 50
            # forceY = ((self.m1.y - self.m2.y)*5)/self.m1.mass
            forceY += (self.m1.yVel - self.m2.yVel) * 3
        self.m1.applyYForce(-forceY)
        self.m2.applyYForce(forceY)
        forceX = 0
        if abs(vector) > 10:
            forceX += -(xLength / abs(vector)) * (abs(vector) - 50) * 50
            forceX += (self.m1.xVel - self.m2.xVel) * 3
            print(forceX)
        self.m1.applyXForce(-forceX)
        self.m2.applyXForce(forceX)


node1 = Node(400, 0)
node2 = Node(450, 20)
node3 = Node(500, 10)
node4 = Node(550, 0)
node5 = Node(600, 0)
spring1 = Spring(node1, node2)
spring2 = Spring(node2, node3)
spring3 = Spring(node3, node4)
spring4 = Spring(node4, node5)
while not gameExit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            node5.y = pygame.mouse.get_pos()[1]
            node5.x = pygame.mouse.get_pos()[0]
    node2.yForce = 0
    node3.yForce = 0
    node4.yForce = 0
    node5.yForce = 0
    node2.xForce = 0
    node3.xForce = 0
    node4.xForce = 0
    node5.xForce = 0
    node2.applyYForce(9.81 * node2.mass)
    node3.applyYForce(9.81 * node2.mass)
    node4.applyYForce(9.81 * node2.mass)
    node5.applyYForce(9.81 * node2.mass)
    spring1.solveSpring()
    spring2.solveSpring()
    spring3.solveSpring()
    spring4.solveSpring()
    node2.moveMass()
    node3.moveMass()
    node4.moveMass()
    node5.moveMass()
    gameDisplay.fill((255, 255, 255))
    pygame.draw.circle(gameDisplay, (0, 255, 0), [
                       node1.x, node1.y], 10)
    pygame.draw.circle(gameDisplay, (255, 255, 0), [
                       node2.x, node2.y], 10)
    pygame.draw.circle(gameDisplay, (255, 255, 0), [
                       node3.x, node3.y], 10)
    pygame.draw.circle(gameDisplay, (255, 255, 0), [
                       node4.x, node4.y], 10)
    pygame.draw.circle(gameDisplay, (255, 255, 0), [
                       node5.x, node5.y], 10)
    pygame.display.update()
    clock.tick(60)

pygame.quit

quit
