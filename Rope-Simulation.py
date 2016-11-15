import pygame

#ehhhh

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

    def applyForce(self, force):
        self.yForce += force

    def moveMass(self):
        self.yVel += (self.yForce / self.mass) * 0.2
        self.y += int(self.yVel * 0.2)


class Spring(object):

    def __init__(self, mass1, mass2):
        self.m1 = mass1
        self.m2 = mass2
        self.lastForceY = 54

    def solveSpring(self):
        forceY = 0
        vector = self.m2.y - self.m1.y
        if abs(vector) > 40:
            forceY += -(vector/abs(vector)) * (abs(vector) - 40) * 40
            # forceY = ((self.m1.y - self.m2.y)*5)/self.m1.mass
            forceY += (self.m1.yVel - self.m2.yVel) * 10
            print(vector)
        self.m1.applyForce(-forceY)
        self.m2.applyForce(forceY)


node1 = Node(400, 0)
node2 = Node(400, 20)
node3 = Node(400, 10)
node4 = Node(400, 0)
node5 = Node(400, 0)
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
    node2.yForce = 0
    node3.yForce = 0
    node4.yForce = 0
    node5.yForce = 0
    node2.applyForce(9.81 * node2.mass)
    node3.applyForce(9.81 * node2.mass)
    node4.applyForce(9.81 * node2.mass)
    node5.applyForce(9.81 * node2.mass)
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

    spring1.solveSpring()
    pygame.display.update()
    clock.tick(150)

pygame.quit

quit
