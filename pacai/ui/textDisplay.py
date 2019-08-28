import time

DRAW_EVERY = 1
SLEEP_TIME = 0  # This can be overwritten by __init__
QUIET = False  # Supresses output

class NullGraphics(object):
    def initialize(self, state, isBlue = False):
        pass

    def update(self, state):
        pass

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def finish(self):
        pass

class PacmanGraphics(object):
    def __init__(self, speed=None):
        if speed is not None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state, isBlue = False):
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state):
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        if self.agentCounter == 0:
            self.turn += 1

            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                self.pause()

        if state._win or state._lose:
            self.draw(state)

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def finish(self):
        pass
