import logging
import random
import typing

import edq.util.time

import pacai.core.action
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.core.isolation.isolator

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

    def game_start(self,
            rng: random.Random,
            initial_state: pacai.core.gamestate.GameState,
            timeout: float,
            ) -> dict[int, pacai.core.agentaction.AgentActionRecord]:
        results = {}
        for (agent_index, agent) in self._agents.items():
            data = {
                'agent_index': agent_index,
                'suggested_seed': rng.randint(0, 2**64),
                'initial_state': initial_state,
            }

            results[agent_index] = _call_agent_method(agent_index, agent.game_start_full, data)

        return results

    def game_complete(self,
            final_state: pacai.core.gamestate.GameState,
            timeout: float,
            ) -> dict[int, pacai.core.agentaction.AgentActionRecord]:
        results = {}
        for (agent_index, agent) in self._agents.items():
            data = {
                'final_state': final_state,
            }

            results[agent_index] = _call_agent_method(agent_index, agent.game_complete_full, data)

        return results

    def get_action(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            timeout: float,
            ) -> pacai.core.agentaction.AgentActionRecord:
        agent = self._agents[state.agent_index]
        data = {
            'state': state,
            'user_inputs': user_inputs,
        }

        return _call_agent_method(state.agent_index, agent.get_action_full, data)

    def close(self) -> None:
        self._agents.clear()

def _call_agent_method(
        agent_index: int,
        agent_method: typing.Callable[..., pacai.core.agentaction.AgentAction],
        agent_method_kwargs: dict[str, typing.Any],
        ) -> pacai.core.agentaction.AgentActionRecord:
    """ Call a method on the agent and do all the proper bookkeeping. """

    crashed = False
    agent_action: pacai.core.agentaction.AgentAction | None = None

    start_time = edq.util.time.Timestamp.now()

    try:
        agent_action = agent_method(**agent_method_kwargs)
    except Exception as ex:
        crashed = True
        logging.warning("Agent %d crashed.", agent_index, exc_info = ex)

    end_time = edq.util.time.Timestamp.now()

    return pacai.core.agentaction.AgentActionRecord(
            agent_index = agent_index,
            agent_action = agent_action,
            duration = end_time.sub(start_time),
            crashed = crashed)
