# TEST
import abc
import enum
import logging
import multiprocessing
import random

import pacai.core.action
import pacai.core.agent
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.core.isolation.isolator
import pacai.util.time

# TEST
MESSAGE_TYPE_INIT: str = 'init'

class ProcessIsolator(pacai.core.isolation.isolator.AgentIsolator):
    """
    An isolator that runs agents in their own process.
    This is a fairly quick and simple way to ensure agents cannot access the same memory space as the game engine.
    Agents will still have access to the same disk and permissions as the game engine.
    """

    def __init__(self) -> None:
        self._agent_processes: dict[int, multiprocessing.Process] = {}
        """
        A process for each agent.
        """

    def init_agents(self, agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
        self._agents = {}
        for (agent_index, agent_info) in agent_infos.items():
            self._agents[agent_index] = pacai.core.agent.load(agent_info)

    def game_start(self, rng: random.Random, initial_state: pacai.core.gamestate.GameState) -> None:
        for (agent_index, agent) in self._agents.items():
            suggested_seed = rng.randint(0, 2**64)
            agent.game_start(agent_index, suggested_seed, initial_state)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        for agent in self._agents.values():
            agent.game_complete(final_state)

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.ActionRecord:
        if (state.agent_index == -1):
            raise ValueError("Game state does not have an active agent.")

        agent = self._agents[state.agent_index]
        crashed = False

        start_time = pacai.util.time.now()

        try:
            action = agent.get_action(state, user_inputs)
        except Exception as ex:
            logging.warning("Agent '%s' (%d) crashed.", agent.name, state.agent_index, exc_info = ex)

            crashed = True
            action = pacai.core.action.STOP

        end_time = pacai.util.time.now()

        return pacai.core.action.ActionRecord(
                agent_index = state.agent_index,
                action = action,
                duration = end_time.sub(start_time),
                crashed = crashed)


    def close(self) -> None:
        self._agents.clear()
