import logging
import multiprocessing
import random
import sys

import pacai.core.action
import pacai.core.agent
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.core.isolation.isolator
import pacai.util.time

MESSAGE_TYPE_START: str = 'start'
MESSAGE_TYPE_ACTION: str = 'action'
MESSAGE_TYPE_COMPLETE: str = 'complete'

JOIN_WAIT_SECS: float = 1.0
REAP_WAIT_SECS: float = 0.5

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

        self._agent_message_queues: dict[int, multiprocessing.Queue] = {}
        """
        The queues used to send messages to each agent process.
        """

        self._agent_action_queues: dict[int, multiprocessing.Queue] = {}
        """
        The queues used for each agent to send back actions.
        """

        # Windows has differences with spawning processes.
        if (sys.platform.startswith("win")):
            raise ValueError("Process isolation is not available on Windows.")

    def init_agents(self, agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
        for (agent_index, agent_info) in agent_infos.items():
            message_queue: multiprocessing.Queue = multiprocessing.Queue()
            action_queue: multiprocessing.Queue = multiprocessing.Queue()

            args = (message_queue, action_queue, agent_info)
            process = multiprocessing.Process(target = _agent_handler, args = args)
            process.start()

            self._agent_message_queues[agent_index] = message_queue
            self._agent_action_queues[agent_index] = action_queue
            self._agent_processes[agent_index] = process

    def game_start(self, rng: random.Random, initial_state: pacai.core.gamestate.GameState) -> None:
        for (agent_index, queue) in self._agent_message_queues.items():
            suggested_seed = rng.randint(0, 2**64)
            queue.put((MESSAGE_TYPE_START, (agent_index, suggested_seed, initial_state)), False)

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        for queue in self._agent_message_queues.values():
            queue.put((MESSAGE_TYPE_COMPLETE, final_state), False)

    def get_action(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            ) -> pacai.core.action.ActionRecord:
        message_queue = self._agent_message_queues[state.agent_index]
        action_queue = self._agent_action_queues[state.agent_index]

        # Send the request for an action.
        message_queue.put((MESSAGE_TYPE_ACTION, (state, user_inputs)), False)

        # Receive the action.
        return action_queue.get(True)

    def close(self) -> None:
        # Close all sending (message) queues.
        for queue in self._agent_message_queues.values():
            queue.close()

        # Empty all receiving (action) queues.
        for queue in self._agent_message_queues.values():
            while (not queue.empty()):
                queue.get(False)

        # Join all processes.
        for process in self._agent_processes.values():
            _join_process(process)

        self._agent_message_queues.clear()
        self._agent_action_queues.clear()
        self._agent_processes.clear()

def _join_process(process: multiprocessing.Process) -> None:
    process.join(JOIN_WAIT_SECS)

    # Check to see if the process is still running.
    if (process.is_alive()):
        # Kill the long-running process.
        process.terminate()

        # Try to reap the process once before just giving up on it.
        process.join(REAP_WAIT_SECS)

        # Try to kill the process if it is still alive.
        if (process.is_alive()):
            process.kill()

def _agent_handler(
        message_queue: multiprocessing.Queue,
        action_queue: multiprocessing.Queue,
        agent_info: pacai.core.agentinfo.AgentInfo) -> None:
    agent = pacai.core.agent.load(agent_info)

    while (True):
        (message_type, payload) = message_queue.get(True)
        if (message_type == MESSAGE_TYPE_START):
            (agent_index, suggested_seed, initial_state) = payload
            agent.game_start(agent_index, suggested_seed, initial_state)
        elif (message_type == MESSAGE_TYPE_ACTION):
            (state, user_inputs) = payload
            action = _get_action(agent, state, user_inputs)
            action_queue.put(action, False)
        elif (message_type == MESSAGE_TYPE_COMPLETE):
            final_state = payload
            agent.game_complete(final_state)
            break
        else:
            raise ValueError(f"Unknown message type: '{message_type}'.")

    # Close the action queue.
    action_queue.close()

    # Empty the message queue.
    while (not message_queue.empty()):
        message_queue.get(False)

def _get_action(
        agent: pacai.core.agent.Agent,
        state: pacai.core.gamestate.GameState,
        user_inputs: list[pacai.core.action.Action],
        ) -> pacai.core.action.ActionRecord:
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
