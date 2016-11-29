import pygame
import math


class Node(object):

    def __init__(self, startX, startY):
        self.x = startX
        self.y = startY
        self.mass = 100
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
        self.length = 0.75
        self.k = 300
        self.friction = 50

    def drawSpring(self, gameDisplay, color=(0, 0, 0)):
        pygame.draw.aaline(gameDisplay, color,
                           (self.m1.x, self.m1.y), (self.m2.x, self.m2.y), 3)

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
            # Each node starts at a point on the straight line from (x0, y0)
            self.nodeList.append(
                Node(startX + slopeX * node, startY + slopeY * node))
        # Connect all nodes with springs to create rope
        # Attach the first node
        self.springList = [Spring(self.startNode, self.nodeList[0])]
        for spring in range(numNodes - 1):
            self.springList.append(
                Spring(self.nodeList[spring], self.nodeList[spring + 1]))
        # Attach the last node
        self.springList.append(
            Spring(self.nodeList[len(self.nodeList) - 1], self.endNode))
        # Set slope
        self.slope = slopeY / slopeX
        self.intercept = startY - 1 * self.slope * startX

    def updateRope(self):
        for node in self.nodeList:
            node.xForce = 0
            node.yForce = 0
            node.applyYForce(2 * node.mass)
            node.applyXForce(self.wind)
        for spring in self.springList:
            spring.solveSpring()
        for node in self.nodeList:
            node.moveMass()

    def applyXForce(self, force):
        # Apply a force to every node in the rope
        for node in self.nodeList:
            node.applyXForce(force)

    def drawRope(self, gameDisplay):
        for spring in self.springList:
            spring.drawSpring(gameDisplay)

    def pointOnRope(self, x, y):
        return (x >= min(self.startNode.x, self.endNode.x)
            and x <= max(self.startNode.x, self.endNode.x)
            and y >= min(self.startNode.y, self.endNode.y)
            and y <= max(self.startNode.y, self.endNode.y))

    def getIntersection(self, other):
        if self.slope == other.slope:
            return None
        b = other.intercept - self.intercept
        m = self.slope - other.slope
        x = int(b / m)
        y = int(self.slope * x + self.intercept)
        if self.pointOnRope(x, y) and other.pointOnRope(x, y):
            return (x, y)
        return None

    def solveIntersection(self, other):
        points = self.getIntersection(other)
        if points == None: return None
        temp = Node(points[0], points[1])
        selfXDiff = self.endNode.x - self.startNode.x
        print(selfXDiff)
        print(points[0])
        xRatio = points[0] - self.startNode.x
        selfInsert = int((xRatio * len(self.nodeList))/selfXDiff)
        print(len(self.nodeList))
        print(selfInsert)
        self.nodeList.insert(selfInsert, temp)
        self.springList.append(Spring(self.nodeList[selfInsert - 1], temp))
        otherDiff = other.endNode.x - other.startNode.x
        otherRatio = points[0] - other.startNode.x
        otherInsert = int((otherRatio * len(other.nodeList))/otherDiff)
        other.nodeList.insert(otherInsert, temp)
        other.springList.append(
            Spring(other.nodeList[otherInsert - 1], temp))
