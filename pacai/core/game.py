import abc
import random

import pacai.core.action
import pacai.core.agent
import pacai.core.isolation
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
            isolation_level: pacai.core.isolation.Level = pacai.core.isolation.Level.NONE,
            seed: int | None = None,
            ) -> None:
        """
        Construct a game.

        Game's only carry nonvolatile information about themselves in member data,
        i.e., they do not carry information about an in-progress game.
        """

        if (seed is None):
            seed = random.randint(0, 2**64)

        self._seed: int = seed

        # TEST - We don't want to construct agents here. Construct them in the Isolator.
        self._agents: list[pacai.core.agent.Agent] = agents
        if (len(self._agents) == 0):
            raise ValueError("No agents provided.")

        self._isolation_level: pacai.core.isolation.Level = isolation_level

    def _setup(self) -> None:
        """ Prepare for a game. """

        # TEST - Is this necessary?
        pass

    @abc.abstractmethod
    def process_move(self, move: MoveHistoryRecord) -> None:
        """ Process the given move and update the game's state. """

        pass

    @abc.abstractmethod
    def get_initial_state(self, rng: random.Random) -> None:
        """ Create the initial state for this game. """

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

        # Create a new random number generator just for this game.
        rng = random.Random(seed)

        # Initialize the agent isolator.
        isolator = self._isolation_level.get_isolator()
        isolator.game_init(self._agents)

        # Assign initial tickets to all the agents.
        tickets = []
        for i in range(len(self._agents)):
            tickets.append(pacai.core.agent.Ticket(i + self._agents[i].move_delay, 0, 0))

        # Keep track of what happens during this game.
        result_id = rng.randint(0, 2**64)
        result = GameResult(result_id, self._seed, self._agents)

        # Create the initial game state.
        state = self.get_initial_state(rng)

        # Notify agents about the start of the game.
        isolator.game_start(state)

        turn_count = 0
        while (True):
            agent_index = self._get_next_agent_index(tickets)
            agent = self._agents[agent_index]

            # Get the next action from the agent.
            next_action = isolator.get_next_action(agent_index, state)

            # Execute the next action.

            # Update the move history.

            # Update the game state.

            # Check for game ending conditions.

            # Issue the agent a new ticket.

            # Increment the turn count.
            turn_count += 1

        # TEST

        # Notify agents about the end of this game.
        isolator.game_complete(state)

        return result

    def _get_next_agent_index(self, tickets: list[pacai.core.agent.Ticket]):
        """
        Get the agent that moves next.
        Do this by looking at the agents' tickets and choosing the one with the lowest ticket.
        """

        next_index = 0
        for i in range(1, len(self._agents)):
            if (tickets[i] < tickets[next_index]):
                next_index = i

        return next_index
