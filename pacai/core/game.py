import abc
import random

import pacai.core.action
import pacai.core.agent
import pacai.core.time

class MoveHistoryRecord:
    """ A record of a single move made by an agent. """

    def __init__(self, index: int, action: pacai.core.action.Action, duration: pacai.core.time.Duration) -> None:
        self.index: int = index
        """ The index of the agent making this move. """

        self.action: pacai.core.action.Action = action
        """ The action made by the agent. """

        self.duration: pacai.core.time.Duration = duration
        """ How long the agent took to compute the this move. """

class GameResult:
    """ The result of running a game. """

    def __init__(self, id: int, seed: int, agents: list[pacai.core.agent.Agent]) -> None:
        self.id: int = id
        """ The ID of the game. """

        self.seed: int = seed
        """ The seed used for the game. """

        self.agent_names: list[str] = []
        """ The names of the agents in the game by index. """

        for agent in agents:
            self.agent_names.append(agent.name)
        
        self.history: list[MoveHistoryRecord] = []
        """ The history of actions taken by each agent in this game. """

class Game(abc.ABC):
    """
    A game that can be run in pacai.
    Games combine the rules, layouts, and agents to run.
    """

    def __init__(self,
            agents: list[pacai.core.agent.Agent],
            seed: int | None = None,
            ) -> None:
        if seed is None:
            seed = random.randint(0, 2**64)

        self._seed: int = seed
        self._rng: random.Random = random.Random(seed)

        self._id = self._rng.randint(0, 2**64)

        self._agents: list[pacai.core.agent.Agent] = agents
        if (len(self._agents) == 0):
            raise ValueError("No agents provided.")

        # Assign initial tickets to all the agents.
        self._tickets = [pacai.core.agent.Ticket(agent.move_delay, 0, 0) for agent in self._agents]

    def setup(self) -> None:
        # TEST - Is this necessary?
        pass

    @abc.abstractmethod
    def process_move(self, move: MoveHistoryRecord) -> None:
        """ Process the given move and update the game's state. """

        pass

    def run(self) -> GameResult:
        """
        The main "game loop" for all games.
        One round of the loop will:
         1) allow the next agent to move,
         2) allocate a new ticket for the moved agent,
         3) record actions,
         4) check the game's rules,
         and 5) update the display.
        """

        result = GameResult(self._id, self._seed, self._agents)

        turn_count = 0
        while (True):
            agent_index = self._get_next_agent_index()
            agent = self._agents[agent_index]

        # TEST

        return result

    def _get_next_agent_index(self):
        """
        Get the agent that moves next.
        Do this by looking at the agents' tickets and choosing the one with the lowest ticket.
        """

        next_index = 0
        for i in range(1, len(self._agents)):
            if (self._tickets[i] < self._tickets[next_index]):
                next_index = i

        return next_index
