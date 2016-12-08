import pygame
import math
import random
import copy
import os
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
# http://stackoverflow.com/questions/3838329
# how-can-i-check-if-two-segments-intersect


def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


# Return true if line segments AB and CD intersect
def doesIntersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def getCenter(width, surface):
    return width // 2 - surface.get_width() // 2


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
        pygame.draw.circle(gameDisplay, (0, 0, 0), [self.x, self.y], 2)


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
        pygame.draw.lines(gameDisplay, color, True, self.polygon.pointList, 2)
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
        for branch in self.availableBranches:
            if branch.inBranch(point):
                return branch

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
        red = (204, 160, 36)
        for branch in self.branches:
            if branch not in self.availableBranches:
                branch.draw(gameDisplay, black)
        for branch in self.availableBranches:
            newColor = (red[0], red[1] - 19 * branch.depth, red[2])
            branch.draw(gameDisplay, newColor)

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

    def path(self, startPoint, endPoint):
        startBranch = self.pointOnBranch(startPoint)
        endBranch = self.pointOnBranch(endPoint)
        path = [endPoint]
        sameBranch = (startBranch == endBranch)
        while not sameBranch:
            if endBranch.orig is None:
                break
            if endBranch == startBranch.orig:
                path.append(startBranch.start)
                break
            path.append(endBranch.start)
            endBranch = endBranch.orig
            sameBranch = (startBranch == endBranch)
        path.reverse()
        return path


# Other Classes


class Bug(object):
    bugsCaught = 0

    def __init__(self, x, y, direc):
        self.x = x
        self.y = y
        self.xVel = random.randint(1, 3) * direc
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
    def findAdjacent(point, closedList, availableBranches):
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
        color = (79, 5, 12)
        pygame.draw.circle(gameDisplay, color,
                           (self.startX, self.startY), self.r)
        pygame.draw.line(gameDisplay, color,
                         (self.startX - self.r - 3, self.startY),
                         (self.startX + self.r + 3, self.startY))
        pygame.draw.line(gameDisplay, color,
                         (self.startX, self.startY - self.r - 3),
                         (self.startX, self.startY + self.r + 3))
        pygame.draw.line(gameDisplay, color,
                         (self.startX - self.r - math.sqrt(3),
                          self.startY - self.r - math.sqrt(3)),
                         (self.startX, self.startY))
        pygame.draw.line(gameDisplay, color,
                         (self.startX + self.r + math.sqrt(3),
                          self.startY + self.r + math.sqrt(3)),
                         (self.startX, self.startY))
        pygame.draw.line(gameDisplay, color,
                         (self.startX - self.r - math.sqrt(3),
                          self.startY + self.r + math.sqrt(3)),
                         (self.startX, self.startY))
        pygame.draw.line(gameDisplay, color,
                         (self.startX + self.r + math.sqrt(3),
                          self.startY - self.r - math.sqrt(3)),
                         (self.startX, self.startY))

    def move(self, target, availableBranches):
        # Uses A* Pathfinding Algorithm
        closedList = [(self.x, self.y)]
        moveList = []
        pathFound = False
        while not pathFound:
            start = closedList[len(closedList) - 1]
            openList = Spider.findAdjacent(
                start, closedList, availableBranches)
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
            self.x -= start[0] - bestPoint[0]
            self.y -= start[1] - bestPoint[1]
            if (abs(bestPoint[0] - target[0]) <= 1 and
                    abs(bestPoint[1] - target[1]) <= 1):
                pathFound = True
        self.curMovements.extend(moveList)


class Button(object):

    def __init__(self, start, width, height, text,
                 size, bgColor, textColor, font):
        self.start = start
        self.width = width
        self.height = height
        self.text = text
        self.fontSize = size
        self.bgColor = bgColor
        self.textColor = textColor
        self.font = pygame.font.Font(font, size)

    def drawButton(self, gameDisplay):
        pygame.draw.rect(gameDisplay, self.bgColor,
                         (self.start, (self.width, self.height)))
        text = self.font.render(self.text, True, self.textColor)
        height = self.start[1] + self.height // 2 - text.get_height() // 2
        width = self.start[0] + self.width // 2 - text.get_width() // 2
        gameDisplay.blit(text, (width, height))

    def didClick(self, click):
        return click[0] >= self.start[0] \
            and click[0] <= self.start[0] + self.width \
            and click[1] >= self.start[1] \
            and click[1] <= self.start[1] + self.height


class Sky(object):

    def __init__(self):
        self.r = 109
        self.g = 169
        self.b = 191
        self.dir = 0.05

    def color(self):
        return (int(self.r), int(self.g), int(self.b))

    def update(self):
        if self.g >= 255 or self.b >= 255:
            self.dir *= -1
        elif self.g <= 75 or self.b <= 75:
            self.dir *= -1
        self.g += self.dir
        self.b += self.dir


class Weather(object):
    weatherStates = {
        "CALM": (20, 70),
        "LIGHT BREEZE": (50, 300),
        "STRONG BREEZE": (70, 450),
        "HIGH WIND": (100, 800)
    }

    def __init__(self):
        self.weatherName = "LIGHT BREEZE"
        self.weatherState = Weather.weatherStates["LIGHT BREEZE"]
        self.minWind = self.weatherState[0]
        self.maxWind = self.weatherState[1]

    def switchStates(self):
        newState = random.choice(list(Weather.weatherStates.keys()))
        self.weatherName = newState
        self.weatherState = Weather.weatherStates[newState]
        self.minWind = self.weatherState[0]
        self.maxWind = self.weatherState[1]


class Cloud(object):

    def __init__(self, x, y):
        self.cloudLines = []
        self.x, self.y = x, y
        for i in range(random.randint(3, 8)):
            self.cloudLines.append([
                [self.x + random.randint(0, 20), self.y + 5 * i],
                [random.randint(150, 200), 5]])

    def moveCloud(self, wind):
        if wind == "CALM":
            delta = 0.5
        elif wind == "LIGHT BREEZE":
            delta = 0.8
        elif wind == "STRONG BREEZE":
            delta = 0.9
        elif wind == "HIGH WIND":
            delta = 1.1
        self.x += delta
        for cloud in self.cloudLines:
            cloud[0][0] += delta

    def drawCloud(self, gameDisplay):
        for cloud in self.cloudLines:
            pygame.draw.rect(gameDisplay, (240, 240, 240), cloud)

    def __hash__(self):
        return hash(self.cloudLines)


#######################################################################
# Main Game Function
#######################################################################


class SpiderGame(object):
    # Game Modes
    START = -1
    MAIN_HELP = 4
    TREE_SELECTION_HELP = -2
    TREE_SELECTION = 0
    GAME_SCREEN = 1
    DRAW_WEB = 2
    MAX_WEB = 30
    END_GAME_SCREEN = 5

    def __init__(self, width=1000, height=600):
        pygame.init()
        fontPath = os.path.abspath("Desktop/CMU First Year/112/" +
                                   "15-112-Term-Project/fonts/Pixeled.ttf")
        self.fontPath = fontPath
        self.font = pygame.font.Font(fontPath, 20)
        self.weather = Weather()
        self.width = width
        self.height = height
        self.fps = 150
        self.mode = SpiderGame.START
        self.ropeList = []
        self.bugList = []
        self.ropeSurface = None
        self.wind = 0
        self.webLevel = 30
        self.tree = treeDrawing(
            (width // 2, height - 100), random.randint(6, 7))
        self.gameDisplay = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Spider Game")
        self.webLabel = Button((self.width - 220, 10), 200, 50, "DRAWING WEB",
                               15, (220, 220, 220), (1, 1, 1), self.fontPath)
        self.spider = Spider(self.tree.branches[0].start)
        self.ground = Hill(self.tree.branches[0].start, width, height)
        self.treeX = 0
        self.treeY = 0
        self.sky = Sky()
        self.didContinue = False
        # Create whole screen color
        self.screen = pygame.Surface((width, height))
        self.screen.set_alpha(230)
        self.clouds = []
        self.startInit()
        self.runGame()

    def runGame(self):
        self.gameExit = False
        clock = pygame.time.Clock()
        self.drawingLine = False
        while not self.gameExit:
            self.gameDisplay.fill(self.sky.color())
            # DRAW ELEMENTS
            self.drawBugs()
            if self.mode == SpiderGame.GAME_SCREEN\
                    or self.mode == SpiderGame.DRAW_WEB\
                    or self.mode == SpiderGame.END_GAME_SCREEN:
                self.drawClouds()
            if self.mode == SpiderGame.GAME_SCREEN\
                    or self.mode == SpiderGame.DRAW_WEB:
                self.updateRopes()
            self.drawTree()
            if self.mode == SpiderGame.GAME_SCREEN\
                    or self.mode == SpiderGame.DRAW_WEB:
                self.drawScore()
                self.drawSpider()
            if self.mode == SpiderGame.START \
                or self.mode == SpiderGame.TREE_SELECTION_HELP \
                or self.mode == SpiderGame.MAIN_HELP\
                    or self.mode == self.END_GAME_SCREEN:
                self.drawScreen()
            if self.mode == SpiderGame.DRAW_WEB:
                self.drawWebLabel()
            self.drawGround()
            self.curBranch = self.tree.pointOnBranch((self.spider.startX,
                                                      self.spider.startY))
            # CHECK ALL EVENTS
            self.checkEvents()
            # UPDATE OBJECT STATES
            if self.mode == SpiderGame.GAME_SCREEN:
                self.updateBugs()
                self.setWind()
                self.updateSpider()
                self.updateClouds()
            rand = random.randint(0, 450)
            if rand == 20:
                self.weather.switchStates()
            self.sky.update()
            if self.mode == SpiderGame.DRAW_WEB:
                self.drawLine()
            pygame.display.update()
            clock.tick(self.fps)

    def updateClouds(self):
        for cloud in self.clouds:
            cloud.moveCloud(self.weather.weatherName)
            if cloud.x > self.width:
                self.clouds.remove(cloud)
        rand = random.randint(0, 250)
        if rand == 0:
            self.clouds.append(Cloud(-300 + random.randint(-50, 0),
                                     random.randint(0, 320)))

    def startInit(self):
        start = self.width // 2 - 100
        titleFont = pygame.font.Font(self.fontPath, 35)
        authorFont = pygame.font.Font(self.fontPath, 30)
        startTitle = titleFont.render(
            "SPIDER WEB SIMULATOR", True, (255, 255, 255))
        author = authorFont.render("BY ILANA FRANKLIN", True, (255, 255, 255))
        titleCenter = self.width // 2 - startTitle.get_width() // 2
        authorCenter = self.width // 2 - author.get_width() // 2
        self.startButton = Button(
            (start, 375), 200, 70, "BEGIN", 20, (132, 17, 21),
            (255, 255, 255), self.fontPath)
        self.buttonFrame = pygame.Surface((self.width, self.height))
        self.startButton.drawButton(self.buttonFrame)
        self.buttonFrame.blit(startTitle, (titleCenter, 150))
        self.buttonFrame.blit(author, (authorCenter, 250))
        self.buttonFrame.set_colorkey((0, 0, 0, 255))

    def drawClouds(self):
        for cloud in self.clouds:
            cloud.drawCloud(self.gameDisplay)

    def treeSelectionHelpInit(self):
        titleFont = pygame.font.Font(self.fontPath, 20)
        font = pygame.font.Font(self.fontPath, 15)
        helpTitle = titleFont.render("TREE SELECTION", True, (255, 255, 255))
        line1 = font.render("PRESS  SPACE UNTIL YOU SEE A TREE YOU LIKE.",
                            True, (255, 255, 255))
        line2 = font.render("HIT ENTER TO START THE GAME.",
                            True, (255, 255, 255))
        self.helpButton = Button((self.width // 2 - 100, 385), 200, 70,
                                 "GOT IT!", 20, (132, 17, 21),
                                 (255, 255, 255), self.fontPath)
        self.buttonFrame.fill((0, 0, 0))
        self.helpButton.drawButton(self.buttonFrame)
        self.buttonFrame.blit(
            helpTitle, (getCenter(self.width, helpTitle), 100))
        self.buttonFrame.blit(line1, (getCenter(self.width, line1), 200))
        self.buttonFrame.blit(line2, (getCenter(self.width, line2), 300))

    def mainHelpInit(self):
        titleFont = pygame.font.Font(self.fontPath, 20)
        font = pygame.font.Font(self.fontPath, 10)
        helpTitle = titleFont.render("SPIDER WEB GAME", True, (255, 255, 255))
        line1 = font.render("CLICK TO MOVE TO ANY COLORED BRANCH." +
                            "PRESS W TO ENTER WEB DRAWING MODE.",
                            True, (255, 255, 255))
        line2 = font.render(
            "IN WEB DRAWING MODE, CLICK FROM THE BRANCH" +
            "YOU ARE CURRENTLY ON TO MAKE A WEB TO ANY OTHER BRANCH.",
            True, (255, 255, 255))
        line3 = font.render(
            "WATCH YOUR WEB LEVEl! BUILD MORE" +
            "WEBS TO CATCH MORE BUGS AND GET MORE WEB.",
            True, (255, 255, 255))
        line4 = font.render("TRY TO COLOR YOUR WHOLE TREE.",
                            True, (255, 255, 255))
        self.helpButton = Button((self.width // 2 - 100, 400), 200, 60,
                                 "GOT IT!", 18, (132, 17, 21), (255, 255, 255),
                                 self.fontPath)
        self.buttonFrame.fill((0, 0, 0))
        self.helpButton.drawButton(self.buttonFrame)
        self.buttonFrame.blit(
            helpTitle, (getCenter(self.width, helpTitle), 100))
        self.buttonFrame.blit(line1, (getCenter(self.width, line1), 200))
        self.buttonFrame.blit(line2, (getCenter(self.width, line2), 250))
        self.buttonFrame.blit(line3, (getCenter(self.width, line3), 300))
        self.buttonFrame.blit(line4, (getCenter(self.width, line4), 350))

    def endGameInit(self):
        titleFont = pygame.font.Font(self.fontPath, 30)
        font = pygame.font.Font(self.fontPath, 20)
        helpTitle = titleFont.render("CONGRATULATIONS!", True, (255, 255, 255))
        line1 = font.render("YOU CONNECTED THE WHOLE TREE!",
                            True, (255, 255, 255))
        self.stayButton = Button((self.width // 2 - 250, 300), 200, 70,
                                 "KEEP GOING", 16, (132, 17, 21),
                                 (255, 255, 255), self.fontPath)
        self.playButton = Button((self.width // 2 + 50, 300), 200, 70,
                                 "PLAY AGAIN", 16, (132, 17, 21),
                                 (255, 255, 255), self.fontPath)
        self.buttonFrame.fill((0, 0, 0))
        self.stayButton.drawButton(self.buttonFrame)
        self.playButton.drawButton(self.buttonFrame)
        self.buttonFrame.blit(
            helpTitle, (getCenter(self.width, helpTitle), 100))
        self.buttonFrame.blit(line1, (getCenter(self.width, line1), 200))

    def drawScreen(self):
        self.gameDisplay.blit(self.screen, (0, 0))
        self.gameDisplay.blit(self.buttonFrame, (0, 0))

    def drawWebLabel(self):
        self.webLabel.drawButton(self.gameDisplay)

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
            self.moving = True
            self.tree.changePos(self.spider.curMovements[0][0],
                                self.spider.curMovements[0][1])
            self.spider.curMovements.pop(0)
            self.ground.changePos(self.tree.branches[0].start)
        else:
            self.moving = False

    def updateBugs(self):
        for bug in self.bugList:
            bug.update()
            bug.checkWebCollision(self.gameDisplay)
            if bug.yVel is None and self.webLevel != SpiderGame.MAX_WEB:
                self.webLevel += 1
            if bug.x > self.width or bug.yVel is None:
                self.bugList.remove(bug)
        rand = random.randint(0, 100)
        if rand == 10:
            self.bugList.append(Bug(-5, random.randint(0, self.height), 1))

    def drawScore(self):
        font = pygame.font.Font(self.fontPath, 10)
        score = font.render(
            "BUGS CAUGHT: " + str(Bug.bugsCaught), True, (255, 255, 255))
        speed = font.render("WIND SPEED: " + str(self.weather.weatherName),
                            True, (255, 255, 255))
        web = font.render("WEB REMAINING: " + "|" *
                          (self.webLevel // 2), True, (255, 255, 255))
        self.scoreFrame = pygame.Surface(
            (max(score.get_width(), speed.get_width(),
                 web.get_width()) + 10, 65))
        self.scoreFrame.set_alpha(230)
        self.scoreFrame.blit(score, (5, 5))
        self.scoreFrame.blit(speed, (5, 25))
        self.scoreFrame.blit(web, (5, 45))
        self.gameDisplay.blit(self.scoreFrame, (0, 0))

    def updateRopes(self):
        if self.ropeSurface is not None:
            self.ropeSurface.fill((0, 0, 0))
            for rope in self.ropeList:
                rope.updateRope()
                rope.drawRope(self.ropeSurface)
            self.gameDisplay.blit(self.ropeSurface, (self.tree.findRect()[0]))

    def setWind(self):
        self.wind = random.randint(self.weather.minWind, self.weather.maxWind)
        Rope.applyWind(self.wind, self.ropeList)

    def treeSelectionEvents(self, keys):
        if keys[pygame.K_SPACE]:
            self.tree = treeDrawing(
                (self.width // 2, self.height - 100), random.randint(6, 7))
        elif keys[pygame.K_RETURN]:
            self.spider = Spider(self.tree.branches[0].start)
            self.tree.scaleTree(3.5)
            self.ground.scale(self.tree.branches[0].start, 3.5)
            self.spider.move((self.tree.availableBranches[0].start[0],
                              self.tree.availableBranches[0].start[1]),
                             self.tree.availableBranches)
            self.ropeSurface = pygame.Surface(self.tree.findRect()[1])
            self.ropeSurface.set_colorkey((0, 0, 0))
            self.mode = SpiderGame.MAIN_HELP
            self.mainHelpInit()

    def pointInAvailableBranches(self, point):
        for branch in self.tree.availableBranches:
            if branch.inBranch(point):
                return True
        return False

    def drawWebEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.curBranch.inBranch(pygame.mouse.get_pos()):
                if not self.drawingLine:
                    self.drawingLine = True
                    self.startTemp = pygame.mouse.get_pos()
            elif self.gameDisplay.get_at(pygame.mouse.get_pos()) == \
                    (0, 0, 0, 255) \
                    or self.pointInAvailableBranches(pygame.mouse.get_pos()):
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
                                break
                        if (set(self.tree.branches) ==
                            set(self.tree.availableBranches)
                                and not self.didContinue):
                            self.mode == SpiderGame.END_GAME_SCREEN
                            self.endGameInit()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_w]:
            self.mode = SpiderGame.GAME_SCREEN

    def gameScreenEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            movePoint = pygame.mouse.get_pos()
            if self.pointInAvailableBranches(movePoint) and not self.moving \
                    and self.tree.pointOnBranch(movePoint).depth > 1:
                path = self.tree.path((self.spider.startX, self.spider.startY),
                                      movePoint)
                for point in path:
                    self.spider.move(point, self.tree.availableBranches)
                self.spider.x = self.spider.startX
                self.spider.y = self.spider.startY
        if keys[pygame.K_w]:
            self.mode = SpiderGame.DRAW_WEB

    def endGameEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.stayButton.didClick(pygame.mouse.get_pos()):
                self.mode = SpiderGame.GAME_SCREEN
                self.didContinue = True
            elif self.playButton.didClick(pygame.mouse.get_pos()):
                Bug.bugsCaught = 0
                SpiderGame()

    def startSelectionEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.startButton.didClick(pygame.mouse.get_pos()):
                self.mode = SpiderGame.TREE_SELECTION_HELP
                self.treeSelectionHelpInit()
        if keys[pygame.K_RETURN]:
            self.mode = SpiderGame.TREE_SELECTION_HELP
            self.treeSelectionHelpInit()

    def treeHelpSelectionEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.helpButton.didClick(pygame.mouse.get_pos()):
                self.mode = SpiderGame.TREE_SELECTION
        if keys[pygame.K_RETURN]:
            self.mode = SpiderGame.TREE_SELECTION

    def mainHelpEvents(self, event, keys):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.helpButton.didClick(pygame.mouse.get_pos()):
                self.mode = SpiderGame.GAME_SCREEN
        if keys[pygame.K_RETURN]:
            self.mode = SpiderGame.GAME_SCREEN

    def checkEvents(self):
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                self.gameExit = True
            elif self.mode == self.END_GAME_SCREEN:
                self.endGameEvents(event, keys)
            elif self.mode == SpiderGame.MAIN_HELP:
                self.mainHelpEvents(event, keys)
            elif self.mode == SpiderGame.TREE_SELECTION_HELP:
                self.treeHelpSelectionEvents(event, keys)
            elif self.mode == SpiderGame.START:
                self.startSelectionEvents(event, keys)
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
