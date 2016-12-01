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

    def __repr__(self):
        return "(%d, %d)" % (self.x, self.y)

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
        self.k = 500
        self.friction = 50

    def __repr__(self):
        return "Spring(" + str(self.m1) + ", " + str(self.m2) + ")"

    def drawSpring(self, gameDisplay, color=(0, 0, 0)):
        pygame.draw.line(gameDisplay, color,
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
        if slopeX == 0:
            self.slope = None
            self.intercept = None
        else:
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

    def ropeLength(self):
        return getLineLength(self.startNode.x, self.startNode.y, self.endNode.x, self.endNode.y)

    def pointOnRope(self, x, y):
        return (x >= min(self.startNode.x, self.endNode.x)
            and x <= max(self.startNode.x, self.endNode.x)
            and y >= min(self.startNode.y, self.endNode.y)
            and y <= max(self.startNode.y, self.endNode.y))

    def getIntersection(self, other):
        if self.slope == other.slope:
            return None
        elif self.slope == None:
            x = self.startNode.x
            y = int(other.slope * x  + other.intercept)
        elif other.slope == None:
            x = other.startNode.x
            y = int(self.slope * x + self.intercept)
        else:
            b = other.intercept - self.intercept
            m = self.slope - other.slope
            x = int(b / m)
            y = int(self.slope * x + self.intercept)
        if self.pointOnRope(x, y) and other.pointOnRope(x, y):
            return (x, y)
        return None

    def solveIntersection(self, other):
        points = self.getIntersection(other)
        if points == None: return None # Stop if there is no intersection
        temp = Node(points[0], points[1])
        # Calculate the location to insert new node on self rope
        selfDiff = self.ropeLength()
        selfRatio = getLineLength(self.startNode.x, self.startNode.y, points[0], points[1])
        selfInsert = int((selfRatio * len(self.nodeList))/selfDiff)
        print(selfInsert)
        prevNode = selfInsert - 1
        nextNode = selfInsert + 1
        self.nodeList.insert(selfInsert, temp)
        self.springList.append(Spring(self.nodeList[prevNode], temp))
        print(self.springList)
        print(self.nodeList[prevNode], temp, self.nodeList[nextNode])
        # Calculate the location to insert new node on other rope
        otherDiff = other.ropeLength()
        otherRatio = getLineLength(other.startNode.x, other.startNode.y, points[0], points[1])
        otherInsert = int((otherRatio * len(other.nodeList))/otherDiff)
        print(otherInsert)
        other.nodeList.insert(otherInsert, temp)
        other.springList.append(Spring(other.nodeList[otherInsert - 1], temp))



def getLineLength(x0, y0, x1, y1):
    return math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
