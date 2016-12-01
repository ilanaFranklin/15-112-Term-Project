import pygame
import math
import random
import copy
##########################################################################
# Tutorial
"""
When game starts, press space to generate a new tree. If you see one that you
like, press enter to begin the game. Click on tree branches to draw spider webs.
You only have a limited amount of webbing.
"""
##########################################################################
# Helper Functions
##########################################################################
# Get length of a line segment with endpoints


def getLineLength(x0, y0, x1, y1):
    return math.sqrt((x1 - x0)**2 + (y1 - y0)**2)


def drawWebLine(canvas, startCoord, endCoord):
    pygame.draw.line(canvas, (150, 150, 150), startCoord, endCoord, 3)
##########################################################################
# Classes
##########################################################################


class Node(object):

    def __init__(self, startX, startY):
        self.x = startX
        self.y = startY
        self.mass = 100
        self.xVel = 0
        self.yVel = 0
        self.xForce = 0
        self.yForce = 0
        self.t = 0.3

    def __repr__(self):
        return "(%d, %d)" % (self.x, self.y)

    def applyYForce(self, force):
        self.yForce += force

    def applyXForce(self, force):
        self.xForce += force

    def moveMass(self):
        self.yVel += (self.yForce / self.mass) * self.t
        self.y += int(self.yVel * self.t)
        self.xVel += (self.xForce / self.mass) * self.t
        self.x += int(self.xVel * self.t)

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

    def __repr__(self):
        return "Spring(" + str(self.m1) + ", " + str(self.m2) + ")"

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

    def drawSpring(self, gameDisplay, color=(255, 255, 255)):
        pygame.draw.line(gameDisplay, color,
                         (self.m1.x, self.m1.y), (self.m2.x, self.m2.y), 3)


class Rope(object):

    @staticmethod
    def applyWind(force, ropeList):
        for rope in ropeList:
            rope.wind = force

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
        self.wind = 0

    def updateRope(self):
        for node in self.nodeList:
            # Reset the forces
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
        return getLineLength(self.startNode.x, self.startNode.y,
                             self.endNode.x, self.endNode.y)

    def pointOnRope(self, x, y):  # Verify that a point is on the rope
        return (x >= min(self.startNode.x, self.endNode.x)
                and x <= max(self.startNode.x, self.endNode.x)
                and y >= min(self.startNode.y, self.endNode.y)
                and y <= max(self.startNode.y, self.endNode.y))

    def getIntersection(self, other):
        if self.slope == other.slope:
            return None
        elif self.slope is None:
            x = self.startNode.x
            y = int(other.slope * x + other.intercept)
        elif other.slope is None:
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
        if points is None:
            return None  # Stop if there is no intersection
        temp = Node(points[0], points[1])
        # Calculate the location to insert new node on self rope
        selfDiff = self.ropeLength()
        selfRatio = getLineLength(
            self.startNode.x, self.startNode.y, points[0], points[1])
        selfInsert = int((selfRatio * len(self.nodeList)) / selfDiff)
        prevNode = selfInsert - 1
        nextNode = selfInsert + 1
        self.nodeList.insert(selfInsert, temp)
        self.springList.append(Spring(self.nodeList[prevNode], temp))
        # Calculate the location to insert new node on other rope
        otherDiff = other.ropeLength()
        otherRatio = getLineLength(
            other.startNode.x, other.startNode.y, points[0], points[1])
        otherInsert = int((otherRatio * len(other.nodeList)) / otherDiff)
        other.nodeList.insert(otherInsert, temp)
        other.springList.append(Spring(other.nodeList[otherInsert - 1], temp))


class treeDrawing(object):

    @staticmethod
    def makeRecursiveTree(startPoint, numBranches):
        branchList = []
        minX = startPoint[0]
        maxX = startPoint[0]
        minY = startPoint[1]
        maxY = startPoint[1]

        def treeHelper(depth, startPoint, minLength, maxLength,
                       angle=90 + random.randint(-5, 5)):
            nonlocal minX
            nonlocal minY
            nonlocal maxX
            nonlocal maxY
            if depth == 0:
                return None
            else:
                length = random.randint(minLength, maxLength)
                endPoint = treeDrawing.calculateEndpoint(
                    startPoint, length, angle)
                if endPoint[0] < minX:
                    minX = endPoint[0]
                elif endPoint[0] > maxX:
                    maxX = endPoint[0]
                if endPoint[1] < minY:
                    minY = endPoint[1]
                elif endPoint[1] > maxY:
                    maxY = endPoint[1]
                branchList.append([[int(startPoint[0]), int(startPoint[1])],
                                   [endPoint[0], endPoint[1]],
                                   length, angle, depth])
                if depth <= numBranches - 2:
                    rand = random.randint(0, 15)
                    if rand == 0:
                        return None
                treeHelper(depth - 1, copy.copy(endPoint),
                           minLength - 10 if minLength > 20 else 20,
                           maxLength - 10 if maxLength > 40 else 40,
                           angle + random.randint(10, 25))
                treeHelper(depth - 1, copy.copy(endPoint),
                           minLength - 10 if minLength > 10 else 20,
                           maxLength - 10 if maxLength > 20 else 40,
                           angle - random.randint(10, 25))
        treeHelper(numBranches, startPoint, 50, 100)
        width = maxX - minX
        height = maxY - minY
        return [branchList, width, height, minX, minY]

    @staticmethod
    def calculateEndpoint(startPoint, length, angle):
        deltaX = length * math.cos(math.radians(angle))
        deltaY = length * math.sin(math.radians(angle))
        return [int(startPoint[0] + deltaX), int(startPoint[1] - deltaY)]

    def __init__(self, startPoint, numBranches):
        temp = treeDrawing.makeRecursiveTree(startPoint, numBranches)
        self.branches = temp[0]
        self.scale = 1
        self.rect = self.findRect()

    def scaleTree(self, factor):
        self.scale *= factor
        for branch in self.branches:
            branch[2] *= self.scale
            endpoint = treeDrawing.calculateEndpoint(
                branch[0], branch[2], branch[3])
            for altBranch in self.branches:
                if altBranch[0] == branch[1]:
                    altBranch[0] = copy.deepcopy(endpoint)
            branch[1] = endpoint
        self.rect = self.findRect()

    def changePos(self, xChange, yChange):
        for branch in self.branches:
            branch[0][1] += yChange
            branch[0][0] += xChange
            branch[1][1] += yChange
            branch[1][0] += xChange
        self.rect = self.findRect()

    def drawTree(self, gameDisplay):
        for branch in self.branches:
            pygame.draw.line(gameDisplay, (0, 0, 0), branch[
                             0], branch[1], int(branch[4] * self.scale * 2))

    def __repr__(self):
        return str(self.branches)

    def findRect(self):
        minX = self.branches[0][0][0]
        maxX = self.branches[0][0][0]
        minY = self.branches[0][0][1]
        maxY = self.branches[0][0][1]
        for branch in self.branches:
            x = branch[1][0]
            y = branch[1][1]
            if x < minX:
                minX = x
            elif x > maxX:
                maxX = x
            if y < minY:
                minY = y
            elif y > maxY:
                maxY = y
        return ((minX, minY), (maxX - minX, maxY - minY))


class Bug(object):
    bugsCaught = 0

    def __init__(self, x, y, direc):
        self.x = x
        self.y = y
        self.xVel = random.randint(2, 5) * direc
        self.yVel = 0
        self.depth = random.randint(0, 5)
        self.radius = 3

    def update(self):
        self.x += self.xVel
        if self.yVel != None:
            self.y -= self.yVel
            if self.yVel < -5:
                self.yVel += random.randint(-1, 8)
            elif self.yVel > 5:
                self.yVel += random.randint(-8, 1)
            else:
                self.yVel += random.randint(-1, 1)
            self.depth = random.randint(0, 5)

    def drawBug(self, gameDisplay):
        pygame.draw.circle(gameDisplay, (244, 185, 66),
                           (self.x, self.y), self.radius)

    def checkWebCollision(self, gameDisplay):
        if self.x > 0 and self.x < gameDisplay.get_width() and self.y > 0 and self.y < gameDisplay.get_height():
            if gameDisplay.get_at((self.x, self.y)) == (255, 255, 255, 255):
                self.yVel = None
                self.xVel = 0
                Bug.bugsCaught += 1

    def __hash__(self):
        return hash((self.x, self.y, self.xVel, self.yVel))


#######################################################################
# Main Game Function
#######################################################################


def runSpiderGame(width=1000, height=600):
    pygame.init()
    pygame.font.init()
    gameDisplay = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Spider Game")
    gameExit = False
    clock = pygame.time.Clock()
    fps = 50  # Frames per second
    TREE_SELECTION = 0
    GAME_SCREEN = 1
    mode = TREE_SELECTION
    tree = treeDrawing((width // 2, height - 100), random.randint(6, 8))
    ropeList = []
    ropeSurface = None
    drawingLine = False
    bugList = []
    webLevel = 30
    for i in range(6):
        bugList.append(Bug(-5, random.randint(0, height), 1))
    font = pygame.font.Font(None, 40)
    wind = 0
    while not gameExit:
        gameDisplay.fill((51, 123, 196))  # Make canvas white
        if ropeSurface != None:
            ropeSurface.fill((0, 0, 0))
            for rope in ropeList:
                rope.updateRope()
                rope.drawRope(ropeSurface)
            gameDisplay.blit(ropeSurface, (tree.findRect()[0]))
        for bug in bugList:
            bug.drawBug(gameDisplay)
        tree.drawTree(gameDisplay)
        score = font.render(
            "Bugs Caught: " + str(Bug.bugsCaught), True, (255, 0, 0))
        speed = font.render("Wind Speed: " + str(wind), True, (255, 0, 0))
        web = font.render("Web Remaining: " + str(webLevel), True, (255, 0, 0))
        gameDisplay.blit(score, (10, 10))
        gameDisplay.blit(speed, (10, 40))
        gameDisplay.blit(web, (10, 70))
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                gameExit = True
            elif mode == TREE_SELECTION:
                if keys[pygame.K_SPACE]:
                    tree = treeDrawing((width // 2, height - 100),
                                       random.randint(6, 8))
                elif keys[pygame.K_RETURN]:
                    tree.scaleTree(3)
                    tree.changePos(50, 300)
                    ropeSurface = pygame.Surface(tree.findRect()[1])
                    ropeSurface.set_colorkey((0, 0, 0))
                    mode = GAME_SCREEN
            elif mode == GAME_SCREEN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if gameDisplay.get_at(pygame.mouse.get_pos()) == (0, 0, 0, 255):
                        if not drawingLine:
                            drawingLine = True
                            startTemp = pygame.mouse.get_pos()
                        else:
                            drawingLine = False
                            endTemp = pygame.mouse.get_pos()
                            startX = startTemp[0] - tree.rect[0][0]
                            startY = startTemp[1] - tree.rect[0][1]
                            endX = endTemp[0] - tree.rect[0][0]
                            endY = endTemp[1] - tree.rect[0][1]
                            numNodes = int(getLineLength(startTemp[0], startTemp[
                                           1], endTemp[0], endTemp[1]) * 0.07)
                            if numNodes > 0 and numNodes <= webLevel:
                                newRope = Rope(numNodes, startX, startY,
                                               endX, endY)
                                ropeList.append(newRope)
                                webLevel -= numNodes
                            for other in ropeList:
                                newRope.solveIntersection(other)
                if keys[pygame.K_RIGHT]:
                    tree.changePos(10, 0)
                if keys[pygame.K_LEFT]:
                    tree.changePos(-10, 0)
                if keys[pygame.K_UP]:
                    tree.changePos(0, -10)
                if keys[pygame.K_DOWN]:
                    tree.changePos(0, 10)
        for bug in bugList:
            bug.update()
            bug.checkWebCollision(gameDisplay)
            if bug.yVel == None:
                webLevel += 0.5
            if bug.x > width or bug.yVel == None:
                bugList.remove(bug)
        rand = random.randint(0, 20)
        if rand == 10:
            bugList.append(Bug(-5, random.randint(0, height), 1))
        wind = random.randint(50, 300)
        Rope.applyWind(wind, ropeList)
        if drawingLine:
            drawWebLine(gameDisplay, startTemp, pygame.mouse.get_pos())
        pygame.display.update()
        clock.tick(fps)


#######################################################################
# Main
#######################################################################
runSpiderGame()
