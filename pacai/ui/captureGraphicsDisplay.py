# TODO(eriq): There is a lot of overlap with graphicsDisplay.py.

import io
import math
import os

from pacai.core.directions import Directions
from pacai.ui import graphicsUtils

DEFAULT_GRID_SIZE = 30.0
INFO_PANE_HEIGHT = 35
BACKGROUND_COLOR = graphicsUtils.formatColor(0, 0, 0)
WALL_COLOR = graphicsUtils.formatColor(0.0 / 255.0, 51.0 / 255.0, 255.0 / 255.0)
INFO_PANE_COLOR = graphicsUtils.formatColor(0.4, 0.4, 0)
SCORE_COLOR = graphicsUtils.formatColor(.9, .9, .9)
PACMAN_OUTLINE_WIDTH = 2
PACMAN_CAPTURE_OUTLINE_WIDTH = 4

GHOST_COLORS = [
    graphicsUtils.formatColor(0.9, 0, 0),  # Red
    graphicsUtils.formatColor(0, 0.3, 0.9),  # Blue
    graphicsUtils.formatColor(0.98, 0.41, 0.07),  # Orange
    graphicsUtils.formatColor(0.1, 0.75, 0.7),  # Green
    graphicsUtils.formatColor(1.0, 0.6, 0.0),  # Yellow
    graphicsUtils.formatColor(0.4, 0.13, 0.91),  # Purple
]

TEAM_COLORS = GHOST_COLORS[:2]

GHOST_SHAPE = [
    (0, 0.3),
    (0.25, 0.75),
    (0.5, 0.3),
    (0.75, 0.75),
    (0.75, -0.5),
    (0.5, -0.75),
    (-0.5, -0.75),
    (-0.75, -0.5),
    (-0.75, 0.75),
    (-0.5, 0.3),
    (-0.25, 0.75)
]
GHOST_SIZE = 0.65
SCARED_COLOR = graphicsUtils.formatColor(1, 1, 1)

GHOST_VEC_COLORS = list(map(graphicsUtils.colorToVector, GHOST_COLORS))

PACMAN_COLOR = graphicsUtils.formatColor(255.0 / 255.0, 255.0 / 255.0, 61.0 / 255)
PACMAN_SCALE = 0.5

# Food
FOOD_COLOR = graphicsUtils.formatColor(1, 1, 1)
FOOD_SIZE = 0.1

# Laser
LASER_COLOR = graphicsUtils.formatColor(1, 0, 0)
LASER_SIZE = 0.02

# Capsule graphics
CAPSULE_COLOR = graphicsUtils.formatColor(1, 1, 1)
CAPSULE_SIZE = 0.25

# Drawing walls
WALL_RADIUS = 0.15

class InfoPane:
    def __init__(self, layout, gridSize, redTeam, blueTeam):
        self.gridSize = gridSize
        self.width = (layout.width) * gridSize
        self.base = (layout.height + 1) * gridSize
        self.height = INFO_PANE_HEIGHT
        self.fontSize = 24
        self.textColor = PACMAN_COLOR
        self.redTeam = redTeam
        self.blueTeam = blueTeam
        self.drawPane()

    def toScreen(self, pos, y = None):
        """
        Translates a point relative from the bottom left of the info pane.
        """

        if (y is None):
            x, y = pos
        else:
            x = pos

        x = self.gridSize + x  # Margin
        y = self.base + y
        return x, y

    def drawPane(self):
        self.scoreText = graphicsUtils.text(self.toScreen(0, 0), self.textColor,
                self._infoString(0, 1200), "Consolas", self.fontSize, "bold")
        self.redText = graphicsUtils.text(self.toScreen(230, 0), TEAM_COLORS[0],
                self._redScoreString(), "Consolas", self.fontSize, "bold")
        self.redText = graphicsUtils.text(self.toScreen(690, 0), TEAM_COLORS[1],
                self._blueScoreString(), "Consolas", self.fontSize, "bold")

    def _redScoreString(self):
        return "RED: % 10s " % (self.redTeam[:12])

    def _blueScoreString(self):
        return "BLUE: % 10s " % (self.blueTeam[:12])

    def updateRedText(self, score):
        graphicsUtils.changeText(self.redText, self._redScoreString())

    def updateBlueText(self, score):
        graphicsUtils.changeText(self.blueText, self._blueScoreString())

    def initializeGhostDistances(self, distances):
        self.ghostDistanceText = []

        size = 20
        if self.width < 240:
            size = 12
        if self.width < 160:
            size = 10

        for i, d in enumerate(distances):
            t = graphicsUtils.text(self.toScreen(self.width / 2 + self.width / 8 * i, 0),
                    GHOST_COLORS[i + 1], d, "Times", size, "bold")
            self.ghostDistanceText.append(t)

    def _infoString(self, score, timeleft):
        return "SCORE: % 4d, TIME: % 4d" % (score, timeleft)

    def updateScore(self, score, timeleft):
        graphicsUtils.changeText(self.scoreText, self._infoString(score, timeleft))

    def setTeam(self, isBlue):
        text = "RED TEAM"
        if isBlue:
            text = "BLUE TEAM"

        self.teamText = graphicsUtils.text(self.toScreen(300, 0), self.textColor, text, "Times",
                self.fontSize, "bold")

    def updateGhostDistances(self, distances):
        if len(distances) == 0:
            return

        if 'ghostDistanceText' not in dir(self):
            self.initializeGhostDistances(distances)
        else:
            for i, d in enumerate(distances):
                graphicsUtils.changeText(self.ghostDistanceText[i], d)

    def drawGhost(self):
        pass

    def drawPacman(self):
        pass

    def drawWarning(self):
        pass

    def clearIcon(self):
        pass

    def updateMessage(self, message):
        pass

    def clearMessage(self):
        pass


class PacmanGraphics:
    def __init__(self, redTeam, blueTeam, zoom=1.0, frameTime=0.0, capture=False,
            gif = None, gif_skip_frames = 0, gif_fps = 10):
        self.expandedCells = []
        self.have_window = 0
        self.currentGhostImages = {}
        self.pacmanImage = None
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.capture = capture
        self.frameTime = frameTime
        self.redTeam = redTeam
        self.blueTeam = blueTeam

        self.gif_path = gif
        self.gif_skip_frames = gif_skip_frames
        self.gif_fps = gif_fps
        self.frame = 0
        self.frame_images = []

    def initialize(self, state, isBlue = False):
        self.isBlue = isBlue
        self.startGraphics(state)

        # self.drawDistributions(state)
        self.distributionImages = None  # Initialized lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

        # Get the first frame.
        self.save_frame(force_save = True)

    def save_frame(self, force_save = False):
        """
        Save the current frame as an image.
        If we are not going to save the game as a gif, no image will be saved.
        """

        if (not self.gif_path):
            return

        if (self.gif_skip_frames != 0 and self.frame % self.gif_skip_frames != 0):
            return

        self.frame_images.append(graphicsUtils.getPostscript())

    def write_gif(self):
        if (not self.gif_path):
            return

        # Delay the dependency unless someone actually needs it.
        import imageio

        images = [imageio.imread(io.BytesIO(image.encode())) for image in self.frame_images]
        imageio.mimwrite(self.gif_path, images, fps = self.gif_fps, subrectangles = True)

    def startGraphics(self, state):
        self.layout = state.getInitialLayout()
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.make_window(self.width, self.height)
        self.infoPane = InfoPane(layout, self.gridSize, self.redTeam, self.blueTeam)
        self.currentState = layout

    def drawDistributions(self, state):
        walls = state.getWalls()
        dist = []
        for x in range(walls.getWidth()):
            distx = []
            dist.append(distx)
            for y in range(walls.getHeight()):
                (screen_x, screen_y) = self.to_screen((x, y))
                block = graphicsUtils.square(
                    (screen_x, screen_y), 0.5 * self.gridSize,
                    color = BACKGROUND_COLOR, filled = 1, behind=2)
                distx.append(block)

        self.distributionImages = dist

    def drawStaticObjects(self, state):
        layout = self.layout
        self.drawWalls(layout.walls)
        self.food = self.drawFood(layout.food)
        self.capsules = self.drawCapsules(layout.capsules)
        graphicsUtils.refresh()

    def drawAgentObjects(self, state):
        self.agentImages = []  # (agentState, image)
        for index, agent in enumerate(state.getAgentStates()):
            if agent.isPacman():
                image = self.drawPacman(agent, index)
                self.agentImages.append((agent, image))
            else:
                image = self.drawGhost(agent, index)
                self.agentImages.append((agent, image))
        graphicsUtils.refresh()

    def swapImages(self, agentIndex, newState):
        """
            Changes an image from a ghost to a pacman or vis versa (for capture)
        """
        prevState, prevImage = self.agentImages[agentIndex]
        for item in prevImage:
            graphicsUtils.remove_from_screen(item)

        if newState.isPacman():
            image = self.drawPacman(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        else:
            image = self.drawGhost(newState, agentIndex)
            self.agentImages[agentIndex] = (newState, image)
        graphicsUtils.refresh()

    def update(self, newState):
        self.frame += 1

        agentIndex = newState.getLastAgentMoved()
        agentState = newState.getAgentState(agentIndex)

        if (self.agentImages[agentIndex][0].isPacman() != agentState.isPacman()):
            self.swapImages(agentIndex, agentState)

        prevState, prevImage = self.agentImages[agentIndex]
        if (agentState.isPacman()):
            self.animatePacman(agentState, prevState, prevImage)
        else:
            self.moveGhost(agentState, agentIndex, prevState, prevImage)
        self.agentImages[agentIndex] = (agentState, prevImage)

        if (newState.getLastFoodEaten() is not None):
            self.removeFood(newState.getLastFoodEaten(), self.food)

        if (newState.getLastCapsuleEaten() is not None):
            self.removeCapsule(newState.getLastCapsuleEaten(), self.capsules)

        self.infoPane.updateScore(newState.getScore(), newState.getTimeleft())
        if ('ghostDistances' in dir(newState)):
            self.infoPane.updateGhostDistances(newState.ghostDistances)

        self.save_frame()

    def make_window(self, width, height):
        grid_width = (width - 1) * self.gridSize
        grid_height = (height - 1) * self.gridSize
        screen_width = 2 * self.gridSize + grid_width
        screen_height = 2 * self.gridSize + grid_height + INFO_PANE_HEIGHT

        graphicsUtils.begin_graphics(screen_width, screen_height, BACKGROUND_COLOR, "Pacman")

    def drawPacman(self, pacman, index):
        position = self.getPosition(pacman)
        screen_point = self.to_screen(position)
        endpoints = self.getEndpoints(self.getDirection(pacman))

        width = PACMAN_OUTLINE_WIDTH
        outlineColor = PACMAN_COLOR
        fillColor = PACMAN_COLOR

        if self.capture:
            outlineColor = TEAM_COLORS[index % 2]
            fillColor = GHOST_COLORS[index]
            width = PACMAN_CAPTURE_OUTLINE_WIDTH

        return [graphicsUtils.circle(screen_point, PACMAN_SCALE * self.gridSize,
                fillColor = fillColor, outlineColor = outlineColor,
                endpoints = endpoints, width = width)]

    def getEndpoints(self, direction, position=(0, 0)):
        x, y = position
        pos = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi * pos)

        delta = width / 2
        if (direction == 'West'):
            endpoints = (180 + delta, 180 - delta)
        elif (direction == 'North'):
            endpoints = (90 + delta, 90 - delta)
        elif (direction == 'South'):
            endpoints = (270 + delta, 270 - delta)
        else:
            endpoints = (0 + delta, 0 - delta)
        return endpoints

    def movePacman(self, position, direction, image):
        screenPosition = self.to_screen(position)
        endpoints = self.getEndpoints(direction, position)
        r = PACMAN_SCALE * self.gridSize
        graphicsUtils.moveCircle(image[0], screenPosition, r, endpoints)
        graphicsUtils.refresh()

    def animatePacman(self, pacman, prevPacman, image):
        if self.frameTime < 0:
            print('Press any key to step forward, "q" to play')
            keys = graphicsUtils.wait_for_keys()
            if 'q' in keys:
                self.frameTime = 0.1

        if self.frameTime > 0.01 or self.frameTime < 0:
            fx, fy = self.getPosition(prevPacman)
            px, py = self.getPosition(pacman)
            frames = 4.0
            for i in range(1, int(frames) + 1):
                pos = (
                    px * i / frames + fx * (frames - i) / frames,
                    py * i / frames + fy * (frames - i) / frames
                )

                self.movePacman(pos, self.getDirection(pacman), image)
                graphicsUtils.refresh()
                graphicsUtils.sleep(abs(self.frameTime) / frames)
        else:
            self.movePacman(self.getPosition(pacman), self.getDirection(pacman), image)
        graphicsUtils.refresh()

    def getGhostColor(self, ghost, ghostIndex):
        if ghost.scaredTimer > 0:
            return SCARED_COLOR
        else:
            return GHOST_COLORS[ghostIndex]

    def drawGhost(self, ghost, agentIndex):
        pos = self.getPosition(ghost)
        dir = self.getDirection(ghost)
        (screen_x, screen_y) = (self.to_screen(pos))
        coords = []
        for (x, y) in GHOST_SHAPE:
            coords.append((
                x * self.gridSize * GHOST_SIZE + screen_x,
                y * self.gridSize * GHOST_SIZE + screen_y
            ))

        colour = self.getGhostColor(ghost, agentIndex)
        body = graphicsUtils.polygon(coords, colour, filled = 1)
        WHITE = graphicsUtils.formatColor(1.0, 1.0, 1.0)
        BLACK = graphicsUtils.formatColor(0.0, 0.0, 0.0)

        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2

        ghostSize = self.gridSize * GHOST_SIZE

        coords = (screen_x + ghostSize * (-0.3 + dx / 1.5), screen_y - ghostSize * (0.3 - dy / 1.5))
        leftEye = graphicsUtils.circle(coords, ghostSize * 0.2, WHITE, WHITE)

        coords = (screen_x + ghostSize * (0.3 + dx / 1.5), screen_y - ghostSize * (0.3 - dy / 1.5))
        rightEye = graphicsUtils.circle(coords, ghostSize * 0.2, WHITE, WHITE)

        coords = (screen_x + ghostSize * (-0.3 + dx), screen_y - ghostSize * (0.3 - dy))
        leftPupil = graphicsUtils.circle(coords, ghostSize * 0.08, BLACK, BLACK)

        coords = (screen_x + ghostSize * (0.3 + dx), screen_y - ghostSize * (0.3 - dy))
        rightPupil = graphicsUtils.circle((coords), ghostSize * 0.08, BLACK, BLACK)

        ghostImageParts = []
        ghostImageParts.append(body)
        ghostImageParts.append(leftEye)
        ghostImageParts.append(rightEye)
        ghostImageParts.append(leftPupil)
        ghostImageParts.append(rightPupil)

        return ghostImageParts

    def moveEyes(self, pos, dir, eyes):
        (screen_x, screen_y) = (self.to_screen(pos))
        dx = 0
        dy = 0
        if dir == 'North':
            dy = -0.2
        if dir == 'South':
            dy = 0.2
        if dir == 'East':
            dx = 0.2
        if dir == 'West':
            dx = -0.2

        ghostSize = self.gridSize * GHOST_SIZE

        coords = (screen_x + ghostSize * (-0.3 + dx / 1.5), screen_y - ghostSize * (0.3 - dy / 1.5))
        graphicsUtils.moveCircle(eyes[0], coords, ghostSize * 0.2)

        coords = (screen_x + ghostSize * (0.3 + dx / 1.5), screen_y - ghostSize * (0.3 - dy / 1.5))
        graphicsUtils.moveCircle(eyes[1], coords, ghostSize * 0.2)

        coords = (screen_x + ghostSize * (-0.3 + dx), screen_y - ghostSize * (0.3 - dy))
        graphicsUtils.moveCircle(eyes[2], coords, ghostSize * 0.08)

        coords = (screen_x + ghostSize * (0.3 + dx), screen_y - ghostSize * (0.3 - dy))
        graphicsUtils.moveCircle(eyes[3], coords, ghostSize * 0.08)

    def moveGhost(self, ghost, ghostIndex, prevGhost, ghostImageParts):
        old_x, old_y = self.to_screen(self.getPosition(prevGhost))
        new_x, new_y = self.to_screen(self.getPosition(ghost))
        delta = new_x - old_x, new_y - old_y

        for ghostImagePart in ghostImageParts:
            graphicsUtils.move_by(ghostImagePart, delta)
        graphicsUtils.refresh()

        if ghost.scaredTimer > 0:
            color = SCARED_COLOR
        else:
            color = GHOST_COLORS[ghostIndex]
        graphicsUtils.edit(ghostImageParts[0], ('fill', color), ('outline', color))
        self.moveEyes(self.getPosition(ghost), self.getDirection(ghost), ghostImageParts[-4:])
        graphicsUtils.refresh()

    def getPosition(self, agentState):
        if (agentState.configuration is None):
            return (-1000, -1000)
        return agentState.getPosition()

    def getDirection(self, agentState):
        if (agentState.configuration is None):
            return Directions.STOP
        return agentState.configuration.getDirection()

    def finish(self):
        # Get the last frame.
        self.save_frame(force_save = True)

        graphicsUtils.end_graphics()

        self.write_gif()

    def to_screen(self, point):
        (x, y) = point
        x = (x + 1) * self.gridSize
        y = (self.height - y) * self.gridSize
        return (x, y)

    # Fixes some TK issue with off - center circles
    def to_screen2(self, point):
        (x, y) = point
        x = (x + 1) * self.gridSize
        y = (self.height - y) * self.gridSize
        return (x, y)

    def drawWalls(self, wallMatrix):
        wallColor = WALL_COLOR
        for xNum, x in enumerate(wallMatrix):
            if self.capture and (xNum * 2) < wallMatrix.getWidth():
                wallColor = TEAM_COLORS[0]

            if self.capture and (xNum * 2) >= wallMatrix.getWidth():
                wallColor = TEAM_COLORS[1]

            for yNum, cell in enumerate(x):
                # Skip of there is no wall here.
                if (not cell):
                    continue

                pos = (xNum, yNum)
                screen = self.to_screen(pos)
                screen2 = self.to_screen2(pos)

                # draw each quadrant of the square based on adjacent walls
                wIsWall = self.isWall(xNum - 1, yNum, wallMatrix)
                eIsWall = self.isWall(xNum + 1, yNum, wallMatrix)
                nIsWall = self.isWall(xNum, yNum + 1, wallMatrix)
                sIsWall = self.isWall(xNum, yNum - 1, wallMatrix)
                nwIsWall = self.isWall(xNum - 1, yNum + 1, wallMatrix)
                swIsWall = self.isWall(xNum - 1, yNum - 1, wallMatrix)
                neIsWall = self.isWall(xNum + 1, yNum + 1, wallMatrix)
                seIsWall = self.isWall(xNum + 1, yNum - 1, wallMatrix)

                wallSize = self.gridSize * WALL_RADIUS

                # NE quadrant
                if (not nIsWall) and (not eIsWall):
                    # inner circle
                    graphicsUtils.circle(screen2, wallSize, wallColor, wallColor, (0, 91), 'arc')
                if (nIsWall) and (not eIsWall):
                    # vertical line
                    graphicsUtils.line(add(screen, (wallSize, 0)),
                            add(screen, (wallSize, self.gridSize * (-0.5) - 1)), wallColor)
                if (not nIsWall) and (eIsWall):
                    # horizontal line
                    graphicsUtils.line(add(screen, (0, -1 * wallSize)),
                            add(screen, (self.gridSize * 0.5 + 1, -1 * wallSize)), wallColor)
                if (nIsWall) and (eIsWall) and (not neIsWall):
                    # outer circle
                    graphicsUtils.circle(add(screen2, (2 * wallSize, -2 * wallSize)),
                            wallSize - 1, wallColor, wallColor, (180, 271), 'arc')
                    graphicsUtils.line(add(screen, (2 * wallSize - 1, -1 * wallSize)),
                            add(screen, (self.gridSize * 0.5 + 1, -1 * wallSize)), wallColor)
                    graphicsUtils.line(add(screen, (wallSize, -2 * wallSize + 1)),
                            add(screen, (wallSize, self.gridSize * (-0.5))), wallColor)

                # NW quadrant
                if (not nIsWall) and (not wIsWall):
                    # inner circle
                    graphicsUtils.circle(screen2, wallSize, wallColor, wallColor, (90, 181), 'arc')
                if (nIsWall) and (not wIsWall):
                    # vertical line
                    graphicsUtils.line(add(screen, (-1 * wallSize, 0)),
                            add(screen, (-1 * wallSize, self.gridSize * (-0.5) - 1)), wallColor)
                if (not nIsWall) and (wIsWall):
                    # horizontal line
                    graphicsUtils.line(add(screen, (0, -1 * wallSize)),
                            add(screen, (self.gridSize * (-0.5) - 1, -1 * wallSize)), wallColor)
                if (nIsWall) and (wIsWall) and (not nwIsWall):
                    # outer circle
                    graphicsUtils.circle(add(screen2, (-2 * wallSize, -2 * wallSize)),
                            wallSize - 1, wallColor, wallColor, (270, 361), 'arc')
                    graphicsUtils.line(add(screen, (-2 * wallSize + 1, -1 * wallSize)),
                            add(screen, (self.gridSize * (-0.5), -1 * wallSize)), wallColor)
                    graphicsUtils.line(add(screen, (-1 * wallSize, -2 * wallSize + 1)),
                            add(screen, (-1 * wallSize, self.gridSize * (-0.5))), wallColor)

                # SE quadrant
                if (not sIsWall) and (not eIsWall):
                    # inner circle
                    graphicsUtils.circle(screen2, wallSize, wallColor, wallColor, (270, 361), 'arc')
                if (sIsWall) and (not eIsWall):
                    # vertical line
                    graphicsUtils.line(add(screen, (wallSize, 0)),
                            add(screen, (wallSize, self.gridSize * (0.5) + 1)), wallColor)
                if (not sIsWall) and (eIsWall):
                    # horizontal line
                    graphicsUtils.line(add(screen, (0, wallSize)),
                            add(screen, (self.gridSize * 0.5 + 1, wallSize)), wallColor)
                if (sIsWall) and (eIsWall) and (not seIsWall):
                    # outer circle
                    graphicsUtils.circle(add(screen2, (2 * wallSize, 2 * wallSize)),
                            wallSize - 1, wallColor, wallColor, (90, 181), 'arc')
                    graphicsUtils.line(add(screen, (2 * wallSize - 1, wallSize)),
                            add(screen, (self.gridSize * 0.5, wallSize)), wallColor)
                    graphicsUtils.line(add(screen, (wallSize, 2 * wallSize - 1)),
                            add(screen, (wallSize, self.gridSize * (0.5))), wallColor)

                # SW quadrant
                if (not sIsWall) and (not wIsWall):
                    # inner circle
                    graphicsUtils.circle(screen2, wallSize, wallColor, wallColor, (180, 271), 'arc')
                if (sIsWall) and (not wIsWall):
                    # vertical line
                    graphicsUtils.line(add(screen, (-1 * wallSize, 0)),
                            add(screen, (-1 * wallSize, self.gridSize * (0.5) + 1)), wallColor)
                if (not sIsWall) and (wIsWall):
                    # horizontal line
                    graphicsUtils.line(add(screen, (0, wallSize)),
                            add(screen, (self.gridSize * (-0.5) - 1, wallSize)), wallColor)
                if (sIsWall) and (wIsWall) and (not swIsWall):
                    # outer circle
                    graphicsUtils.circle(add(screen2, (-2 * wallSize, 2 * wallSize)),
                            wallSize - 1, wallColor, wallColor, (0, 91), 'arc')
                    graphicsUtils.line(add(screen, (-2 * wallSize + 1, wallSize)),
                            add(screen, (self.gridSize * (-0.5), wallSize)), wallColor)
                    graphicsUtils.line(add(screen, (-1 * wallSize, 2 * wallSize - 1)),
                            add(screen, (-1 * wallSize, self.gridSize * (0.5))), wallColor)

    def isWall(self, x, y, walls):
        if (x < 0 or y < 0):
            return False

        if (x >= walls.getWidth() or y >= walls.getHeight()):
            return False

        return walls[x][y]

    def drawFood(self, foodMatrix):
        foodImages = []
        color = FOOD_COLOR
        for xNum, x in enumerate(foodMatrix):
            if (self.capture and (xNum * 2) <= foodMatrix.getWidth()):
                color = TEAM_COLORS[0]

            if (self.capture and (xNum * 2) > foodMatrix.getWidth()):
                color = TEAM_COLORS[1]

            imageRow = []
            foodImages.append(imageRow)
            for yNum, cell in enumerate(x):
                # There's food here
                if (cell):
                    screen = self.to_screen((xNum, yNum))
                    dot = graphicsUtils.circle(
                        screen, FOOD_SIZE * self.gridSize,
                        outlineColor = color, fillColor = color, width = 1)
                    imageRow.append(dot)
                else:
                    imageRow.append(None)
        return foodImages

    def drawCapsules(self, capsules):
        capsuleImages = {}
        for capsule in capsules:
            (screen_x, screen_y) = self.to_screen(capsule)
            dot = graphicsUtils.circle(
                (screen_x, screen_y), CAPSULE_SIZE * self.gridSize,
                outlineColor = CAPSULE_COLOR, fillColor = CAPSULE_COLOR, width = 1)
            capsuleImages[capsule] = dot
        return capsuleImages

    def removeFood(self, cell, foodImages):
        x, y = cell
        graphicsUtils.remove_from_screen(foodImages[x][y])

    def removeCapsule(self, cell, capsuleImages):
        x, y = cell
        graphicsUtils.remove_from_screen(capsuleImages[(x, y)])

    def drawExpandedCells(self, cells):
        """
        Draws an overlay of expanded grid positions for search agents
        """
        n = float(len(cells))
        baseColor = [1.0, 0.0, 0.0]
        self.clearExpandedCells()
        self.expandedCells = []
        for k, cell in enumerate(cells):
            screenPos = self.to_screen(cell)
            cellColor = graphicsUtils.formatColor(*[(n - k) * c * .5 / n + .25 for c in baseColor])
            block = graphicsUtils.square(screenPos, 0.5 * self.gridSize,
                    color = cellColor, filled = 1, behind = 2)
            self.expandedCells.append(block)
            if self.frameTime < 0:
                graphicsUtils.refresh()

    def clearDebug(self):
        if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
            for cell in self.expandedCells:
                graphicsUtils.remove_from_screen(cell)

    def debugDraw(self, cells, color=[1.0, 0.0, 0.0], clear=False):
        if clear:
            self.clearDebug()
            self.expandedCells = []

        for k, cell in enumerate(cells):
            screenPos = self.to_screen(cell)
            cellColor = graphicsUtils.formatColor(*color)
            block = graphicsUtils.square(screenPos, 0.5 * self.gridSize,
                    color = cellColor, filled = 1, behind = 2)
            self.expandedCells.append(block)
            if self.frameTime < 0:
                graphicsUtils.refresh()

    def clearExpandedCells(self):
        if 'expandedCells' in dir(self) and len(self.expandedCells) > 0:
            for cell in self.expandedCells:
                graphicsUtils.remove_from_screen(cell)

class FirstPersonPacmanGraphics(PacmanGraphics):
    def __init__(self, zoom = 1.0, showGhosts = True, capture = False, frameTime=0):
        PacmanGraphics.__init__(self, zoom, frameTime=frameTime)
        self.showGhosts = showGhosts
        self.capture = capture

    def initialize(self, state, isBlue = False):

        self.isBlue = isBlue
        PacmanGraphics.startGraphics(self, state)

        # Initialize distribution images
        self.layout = state.getInitialLayout()

        # Draw the rest
        self.distributionImages = None  # initialize lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def lookAhead(self, config, state):
        if config.getDirection() == 'Stop':
            return
        else:
            pass
            # Draw relevant ghosts
            allGhosts = state.getGhostStates()
            visibleGhosts = state.getVisibleGhosts()
            for i, ghost in enumerate(allGhosts):
                if ghost in visibleGhosts:
                    self.drawGhost(ghost, i)
                else:
                    self.currentGhostImages[i] = None

    def getGhostColor(self, ghost, ghostIndex):
        return GHOST_COLORS[ghostIndex]

    def getPosition(self, ghostState):
        if not self.showGhosts and not ghostState.isPacman() and ghostState.getPosition()[1] > 1:
            return (-1000, -1000)
        else:
            return PacmanGraphics.getPosition(self, ghostState)

def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


# Saving graphical output
# -----------------------
# Note: to make an animated gif from this postscript output, try the command:
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif
# convert is part of imagemagick (freeware)

SAVE_POSTSCRIPT = False
POSTSCRIPT_OUTPUT_DIR = 'frames'
FRAME_NUMBER = 0

def saveFrame():
    "Saves the current graphical output as a postscript file"
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR

    if not SAVE_POSTSCRIPT:
        return

    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR):
        os.mkdir(POSTSCRIPT_OUTPUT_DIR)

    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    graphicsUtils.writePostscript(name)  # writes the current canvas
