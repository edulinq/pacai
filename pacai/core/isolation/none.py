import logging
import random

import pacai.core.action
import pacai.core.agent
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.core.isolation.isolator
import pacai.util.time

class NoneIsolator(pacai.core.isolation.isolator.AgentIsolator):
    """
    An isolator that does not do any isolation between the engine and agents.
    All agents will be run in the same thread (and therefore processes space).
    This is the simplest and fastest of all isolators, but offers the least control and protection.
    Agents cannot be timed out (since they run on the same thread).
    Agents can also access any memory, disk, or permissions that the core engine has access to.
    """

    def __init__(self) -> None:
        self._agents: dict[int, pacai.core.agent.Agent] = {}
        """
        The agents that this isolator manages.
        These agents are held and ran in this thread's memory space.
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
