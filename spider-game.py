import pygame
import math
import random
import copy
import queue
##########################################################################
# Tutorial
"""
When game starts, press space to generate a new tree. If you see one that you
like, press enter to begin the game. Click on tree branches to draw spider webs
You only have a limited amount of webbing.
"""
##########################################################################
# Helper Functions
##########################################################################


def getLineLength(x0, y0, x1, y1):
    # Get length of a line segment with endpoints
    return math.sqrt((x1 - x0)**2 + (y1 - y0)**2)


def drawWebLine(canvas, startCoord, endCoord):
    pygame.draw.line(canvas, (150, 150, 150), startCoord, endCoord, 3)

# Line intersection code taken from
# http://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect


def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


# Return true if line segments AB and CD intersect
def doesIntersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


##########################################################################
# Classes
##########################################################################

# Rope Classes


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
        self.nodeList.insert(selfInsert, temp)
        self.springList.append(Spring(self.nodeList[prevNode], temp))
        # Calculate the location to insert new node on other rope
        otherDiff = other.ropeLength()
        otherRatio = getLineLength(
            other.startNode.x, other.startNode.y, points[0], points[1])
        otherInsert = int((otherRatio * len(other.nodeList)) / otherDiff)
        other.nodeList.insert(otherInsert, temp)
        other.springList.append(Spring(other.nodeList[otherInsert - 1], temp))

# Tree Classes


class BranchPolygon(object):

    def __init__(self, branch):
        self.branch = branch
        if branch.orig is None:
            self.baseWidth = branch.depth * 2
        else:
            self.baseWidth = branch.orig.polygon.endWidth
        if branch.depth == 1:
            self.endWidth = 0
        else:
            self.endWidth = branch.depth * 1
            if self.endWidth < 2:
                self.endWidth = 3
        self.pointList = self.calcPoints()

    def calcPoints(self):
        self.baseLeft = [self.branch.start[0] -
                         self.baseWidth // 2,  self.branch.start[1]]
        self.baseRight = [self.branch.start[0] +
                          self.baseWidth // 2,  self.branch.start[1]]
        self.endLeft = [self.branch.end[0] -
                        self.endWidth // 2,  self.branch.end[1]]
        self.endRight = [self.branch.end[0] +
                         self.endWidth // 2,  self.branch.end[1]]
        return [self.baseLeft, self.endLeft, self.endRight, self.baseRight]

    def scale(self, scale):
        self.baseWidth *= scale
        self.endWidth *= scale
        self.pointList = self.calcPoints()

    def changePos(self, xChange, yChange):
        for point in self.pointList:
            point[0] += xChange
            point[1] += yChange

    def pointInPolygon(self, point):
        x, y = point[0], point[1]
        if y > self.baseLeft[1] or y < self.endLeft[1]:
            return False
        line3 = ((x, y), (x + 200, y))
        line1 = (self.baseLeft, self.endLeft)
        line2 = (self.baseRight, self.endRight)
        sum = 1 if doesIntersect(line1[0], line1[1], line3[0], line3[1]) else 0
        sum += 1 if doesIntersect(line2[0],
                                  line2[1], line3[0], line3[1]) else 0
        if sum == 1:
            return True
        return False


class Branch(object):

    def __init__(self, start, end, orig, length, angle, depth):
        self.start = start
        self.end = end
        self.orig = orig
        self.length = length
        self.angle = angle
        self.depth = depth
        self.polygon = BranchPolygon(self)

    def __repr__(self):
        return "(" + str(self.start) + "," + str(self.end) + "," \
            + str(self.length) + "," + str(self.angle) \
            + "," + str(self.depth) + ")"

    def draw(self, gameDisplay, color):
        pygame.draw.aalines(gameDisplay, color, True, self.polygon.pointList)
        pygame.draw.polygon(gameDisplay, color, self.polygon.pointList)

    def inBranch(self, point):
        return self.polygon.pointInPolygon(point)


class treeDrawing(object):

    @staticmethod
    def makeRecursiveTree(startPoint, numBranches):
        branchList = []

        def treeHelper(depth, startPoint, minLength, maxLength,
                       angle=90 + random.randint(-5, 5), orig=None):
            if depth == 0:
                return None
            else:
                length = random.randint(minLength, maxLength)
                endPoint = treeDrawing.calculateEndpoint(
                    startPoint, length, angle)
                newBranch = Branch([int(startPoint[0]), int(startPoint[1])],
                                   [endPoint[0], endPoint[1]], orig,
                                   length, angle, depth)
                branchList.append(newBranch)
                if depth <= numBranches - 2:
                    rand = random.randint(0, 15)
                    if rand == 0:
                        return None
                treeHelper(depth - 1, copy.copy(endPoint),
                           minLength - 10 if minLength > 20 else 20,
                           maxLength - 10 if maxLength > 40 else 40,
                           angle + random.randint(10, 25), newBranch)
                treeHelper(depth - 1, copy.copy(endPoint),
                           minLength - 10 if minLength > 10 else 20,
                           maxLength - 10 if maxLength > 20 else 40,
                           angle - random.randint(10, 25), newBranch)
        treeHelper(numBranches, startPoint, 30, 60)
        return branchList

    def pointOnBranch(self, point):
        for

    @staticmethod
    def calculateEndpoint(startPoint, length, angle):
        deltaX = length * math.cos(math.radians(angle))
        deltaY = length * math.sin(math.radians(angle))
        return [int(startPoint[0] + deltaX), int(startPoint[1] - deltaY)]

    def __init__(self, startPoint, numBranches):
        self.branches = treeDrawing.makeRecursiveTree(startPoint, numBranches)
        self.maxDepth = numBranches
        branchFound = False
        self.availableBranches = []
        while not branchFound:
            curBranch = self.branches[
                random.randint(0, len(self.branches) - 1)]
            if curBranch.depth == self.maxDepth - 1:
                branchFound = True
        self.availableBranches.append(curBranch)
        self.availableBranches.append(self.branches[0])
        self.scale = 1
        self.rect = self.findRect()

    def scaleTree(self, factor):
        self.scale *= factor
        for branch in self.branches:
            branch.length *= self.scale
            endpoint = treeDrawing.calculateEndpoint(
                branch.start, branch.length, branch.angle)
            for altBranch in self.branches:
                if altBranch.start == branch.end:
                    altBranch.start = copy.deepcopy(endpoint)
            branch.end = endpoint
            branch.polygon.scale(factor)
        self.rect = self.findRect()

    def changePos(self, xChange, yChange):
        for branch in self.branches:
            branch.start[1] += yChange
            branch.start[0] += xChange
            branch.end[1] += yChange
            branch.end[0] += xChange
            branch.polygon.changePos(xChange, yChange)
        self.rect = self.findRect()

    def drawTree(self, gameDisplay):
        black = (0, 0, 0)
        pink = (244, 66, 110)
        for branch in self.branches:
            if branch in self.availableBranches:
                continue
            branch.draw(gameDisplay, black)
        for branch in self.availableBranches:
            branch.draw(gameDisplay, pink)

    def __repr__(self):
        return str(self.branches)

    def findRect(self):
        minX = self.branches[0].start[0]
        maxX = self.branches[0].start[0]
        minY = self.branches[0].start[1]
        maxY = self.branches[0].start[1]
        for branch in self.branches:
            x = branch.end[0]
            y = branch.end[1]
            if x < minX:
                minX = x
            elif x > maxX:
                maxX = x
            if y < minY:
                minY = y
            elif y > maxY:
                maxY = y
        return ((minX, minY), (maxX - minX, maxY - minY))

# Other Classes


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
        if self.yVel is not None:
            self.y -= self.yVel
            if self.yVel < -5:
                self.yVel += random.randint(-1, 8)
            elif self.yVel > 5:
                self.yVel += random.randint(-8, 1)
            else:
                self.yVel += random.randint(-1, 1)
            self.depth = random.randint(0, 5)

    def drawBug(self, gameDisplay):
        pygame.draw.circle(gameDisplay, (201, 101, 68),
                           (self.x, self.y), self.radius)

    def checkWebCollision(self, gameDisplay):
        if (self.x > 0 and self.x < gameDisplay.get_width() and
                self.y > 0 and self.y < gameDisplay.get_height()):
            if gameDisplay.get_at((self.x, self.y)) == (255, 255, 255, 255):
                self.yVel = None
                self.xVel = 0
                Bug.bugsCaught += 1

    def __hash__(self):
        return hash((self.x, self.y, self.xVel, self.yVel))


class Hill(object):

    def __init__(self, midpoint, width, height, color=(0, 0, 0)):
        self.width = width
        self.height = height
        self.midpoint = midpoint
        self.color = color
        self.calculatePoints()

    def calculatePoints(self):
        self.startX = self.midpoint[0] - self.width // 2
        self.startY = self.midpoint[1]

    def scale(self, midpoint, scale):
        self.midpoint = midpoint
        self.width *= scale
        self.height *= scale
        self.calculatePoints()

    def changePos(self, midpoint):
        self.midpoint = midpoint
        self.calculatePoints()

    def drawHill(self, gameDisplay):
        pygame.draw.ellipse(gameDisplay, self.color, ((
            self.startX, self.startY), (self.width, self.height)))


class Spider(object):

    @staticmethod
    def findAdjacent(point, closedList, availableBranches, gameDisplay):
        pointList = []
        for xdir in [-1, 0, 1]:
            for ydir in [-1, 0, 1]:
                newPoint = (point[0] + xdir, point[1] + ydir)
                onBranch = False
                for branch in availableBranches:
                    if branch.inBranch(newPoint):
                        onBranch = True
                if onBranch and newPoint not in closedList:
                    pointList.append(newPoint)
        return pointList

    @staticmethod
    def fScore(checkPoint, target):
        return abs(target[0] - checkPoint[0]) + abs(checkPoint[1] - target[1])

    def __init__(self, startPoint):
        self.r = 5
        self.startX = startPoint[0]
        self.startY = startPoint[1]
        self.x = startPoint[0]
        self.y = startPoint[1]
        self.curMovements = []

    def draw(self, gameDisplay):
        pygame.draw.circle(gameDisplay, (244, 164, 66),
                           (self.startX, self.startY), self.r)

    def move(self, target, availableBranches, gameDisplay):
        # Uses A* Pathfinding Algorithm
        closedList = [(self.x, self.y)]

        moveList = []
        pathFound = False
        while not pathFound:
            start = closedList[len(closedList) - 1]
            openList = Spider.findAdjacent(
                start, closedList, availableBranches, gameDisplay)
            if len(openList) == 0:
                moveList = []
                break
            lowestFScore = Spider.fScore(openList[0], target)
            bestPoint = openList[0]
            for point in openList:
                f = Spider.fScore(point, target)
                if f < lowestFScore:
                    bestPoint = point
                    lowestFScore = f
            closedList.append(bestPoint)
            moveList.append((start[0] - bestPoint[0], start[1] - bestPoint[1]))
            if (abs(bestPoint[0] - target[0]) <= 1 and
                    abs(bestPoint[1] - target[1]) <= 1):
                pathFound = True
        self.curMovements = moveList



#######################################################################
# Main Game Function
#######################################################################


class SpiderGame(object):
    # Game Modes
    TREE_SELECTION = 0
    GAME_SCREEN = 1
    DRAW_WEB = 2

    def __init__(self, width=1000, height=600):
        pygame.init()
        self.font = pygame.font.Font(None, 40)
        self.width = width
        self.height = height
        self.fps = 150
        self.mode = SpiderGame.TREE_SELECTION
        self.ropeList = []
        self.bugList = []
        self.ropeSurface = None
        self.wind = 0
        self.windMax = 300
        self.windMin = 50
        self.webLevel = 30
        self.tree = treeDrawing(
            (width // 2, height - 100), random.randint(6, 8))
        self.gameDisplay = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Spider Game")
        self.spider = Spider(self.tree.branches[0].start)
        self.ground = Hill(self.tree.branches[0].start, width, height)
        self.treeX = 0
        self.treeY = 0
        self.runGame()

    def runGame(self):
        self.gameExit = False
        clock = pygame.time.Clock()
        self.drawingLine = False
        while not self.gameExit:
            self.gameDisplay.fill((136, 190, 216))
            # DRAW ELEMENTS
            self.updateRopes()
            self.drawTree()
            self.drawBugs()
            self.drawScore()
            self.drawGround()
            self.drawSpider()
            # CHECK ALL EVENTS
            self.checkEvents()
            # UPDATE OBJECT STATES
            self.updateBugs()
            self.setWind()
            self.drawLine()
            self.updateSpider()
            pygame.display.update()
            clock.tick(self.fps)

    def drawTree(self):
        self.tree.drawTree(self.gameDisplay)

    def drawBugs(self):
        for bug in self.bugList:
            bug.drawBug(self.gameDisplay)

    def drawGround(self):
        self.ground.drawHill(self.gameDisplay)

    def drawSpider(self):
        self.spider.draw(self.gameDisplay)

    def updateSpider(self):
        if len(self.spider.curMovements) > 0:
            self.tree.changePos(self.spider.curMovements[0][0],
                                self.spider.curMovements[0][1])
            self.spider.curMovements.pop(0)
            self.ground.changePos(self.tree.branches[0].start)

    def updateBugs(self):
        for bug in self.bugList:
            bug.update()
            bug.checkWebCollision(self.gameDisplay)
            if bug.yVel is None:
                self.webLevel += 1
            if bug.x > self.width or bug.yVel is None:
                self.bugList.remove(bug)
        rand = random.randint(0, 40)
        if rand == 10:
            self.bugList.append(Bug(-5, random.randint(0, self.height), 1))

    def drawScore(self):
        score = self.font.render(
            "Bugs Caught: " + str(Bug.bugsCaught), True, (255, 0, 0))
        speed = self.font.render(
            "Wind Speed: " + str(self.wind), True, (255, 0, 0))
        web = self.font.render("Web Remaining: " +
                               str(self.webLevel), True, (255, 0, 0))
        self.gameDisplay.blit(score, (10, 10))
        self.gameDisplay.blit(speed, (10, 40))
        self.gameDisplay.blit(web, (10, 70))

    def updateRopes(self):
        if self.ropeSurface is not None:
            self.ropeSurface.fill((0, 0, 0))
            for rope in self.ropeList:
                rope.updateRope()
                rope.drawRope(self.ropeSurface)
            self.gameDisplay.blit(self.ropeSurface, (self.tree.findRect()[0]))

    def setWind(self):
        self.wind = random.randint(self.windMin, self.windMax)
        Rope.applyWind(self.wind, self.ropeList)

    def treeSelectionEvents(self, keys):
        if keys[pygame.K_SPACE]:
            self.tree = treeDrawing(
                (self.width // 2, self.height - 100), random.randint(6, 8))
        elif keys[pygame.K_RETURN]:
            self.spider = Spider(self.tree.branches[0].start)
            self.tree.scaleTree(3.5)
            self.ground.scale(self.tree.branches[0].start, 3.5)
            self.spider.move((self.tree.availableBranches[0].start[0],
                              self.tree.availableBranches[0].start[1]),
                             self.tree.availableBranches,
                             self.gameDisplay)
            self.ropeSurface = pygame.Surface(self.tree.findRect()[1])
            self.ropeSurface.set_colorkey((0, 0, 0))
            self.mode = SpiderGame.GAME_SCREEN

    def pointInAvailableBranches(self, point):
        for branch in self.tree.availableBranches:
            if branch.inBranch(point):
                return True
        return False

    def drawWebEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pointInAvailableBranches(pygame.mouse.get_pos()):
                if not self.drawingLine:
                    self.drawingLine = True
                    self.startTemp = pygame.mouse.get_pos()
            if self.gameDisplay.get_at(pygame.mouse.get_pos()) == \
                    (0, 0, 0, 255):
                if self.drawingLine:
                    self.drawingLine = False
                    endTemp = pygame.mouse.get_pos()
                    startX = self.startTemp[0] - self.tree.rect[0][0]
                    startY = self.startTemp[1] - self.tree.rect[0][1]
                    endX = endTemp[0] - self.tree.rect[0][0]
                    endY = endTemp[1] - self.tree.rect[0][1]
                    numNodes = int(getLineLength(self.startTemp[0],
                                                 self.startTemp[1],
                                                 endTemp[0],
                                                 endTemp[1]) * 0.07)
                    if numNodes > 0 and numNodes <= self.webLevel:
                        newRope = Rope(numNodes, startX, startY,
                                       endX, endY)
                        self.ropeList.append(newRope)
                        self.webLevel -= numNodes
                        for other in self.ropeList:
                            newRope.solveIntersection(other)
                    for branch in self.tree.branches:
                        if branch.inBranch(endTemp):
                            self.tree.availableBranches.append(branch)
        if keys[pygame.K_ESCAPE]:
            self.mode = SpiderGame.GAME_SCREEN

    def gameScreenEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pointInAvailableBranches(pygame.mouse.get_pos()):
                self.spider.move(pygame.mouse.get_pos(),
                                 self.tree.availableBranches,
                                 self.gameDisplay)
        if keys[pygame.K_w]:
            self.mode = SpiderGame.DRAW_WEB

    def checkEvents(self):
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                self.gameExit = True
            elif self.mode == SpiderGame.TREE_SELECTION:
                self.treeSelectionEvents(keys)
            elif self.mode == SpiderGame.GAME_SCREEN:
                self.gameScreenEvents(event, keys)
            elif self.mode == SpiderGame.DRAW_WEB:
                self.drawWebEvents(event, keys)

    def drawLine(self):
        if self.drawingLine:
            drawWebLine(self.gameDisplay, self.startTemp,
                        pygame.mouse.get_pos())

#######################################################################
# Main
#######################################################################
game = SpiderGame()
