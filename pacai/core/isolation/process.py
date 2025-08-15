import logging
import multiprocessing
import random
import sys
import typing
import queue as pyqueue

import edq.util.time

import pacai.core.action
import pacai.core.agent
import pacai.core.agentaction
import pacai.core.agentinfo
import pacai.core.gamestate
import pacai.core.isolation.isolator

MESSAGE_TYPE_START: str = 'start'
MESSAGE_TYPE_ACTION: str = 'action'
MESSAGE_TYPE_COMPLETE: str = 'complete'

JOIN_WAIT_SECS: float = 0.25
REAP_WAIT_SECS: float = 0.10

class ProcessIsolator(pacai.core.isolation.isolator.AgentIsolator):
    """
    An isolator that runs agents in their own process.
    This is a fairly quick and simple way to ensure agents cannot access the same memory space as the game engine.
    Agents will still have access to the same disk and permissions as the game engine.

    If an agent times out on any of its actions,
    then no additional calls will be made to that agent and the isolator will close itself.
    This is because we can no longer guarantee the integrity of the communication queues.
    """

    def __init__(self) -> None:
        self._agent_processes: dict[int, multiprocessing.Process] = {}
        """
        A process for each agent.
        """

        # Cannot consistently type multiprocessing.Queue before 3.11.
        self._agent_message_queues: dict[int, multiprocessing.Queue] = {}
        """
        The queues used to send messages to each agent process.

        These queues will be loaded by the game thread and emptied by the agent threads.
        Messages of type `tuple[str, typing.Any]` will be sent through these queues.
        """

        # Cannot consistently type multiprocessing.Queue before 3.11.
        self._agent_action_queues: dict[int, multiprocessing.Queue] = {}
        """
        The queues used for each agent to send back actions.

        These queues will be loaded by the agent threads and emptied by the game thread.
        Messages of type `pacai.core.agentaction.AgentAction | None` will be sent through these queues.
        """

        self._closed: bool = False
        """ Whether this isolator has already been closed. """

        # Windows has differences with spawning processes.
        if (sys.platform.startswith("win")):
            raise ValueError("Process isolation is not available on Windows.")

    def init_agents(self, agent_infos: dict[int, pacai.core.agentinfo.AgentInfo]) -> None:
        if (self._closed):
            raise ValueError("This isolator has already been closed.")

        for (agent_index, agent_info) in agent_infos.items():
            message_queue: multiprocessing.Queue = multiprocessing.Queue()
            action_queue: multiprocessing.Queue = multiprocessing.Queue()

            args = (message_queue, action_queue, agent_info)
            process = multiprocessing.Process(target = _agent_handler, args = args)
            process.start()

            self._agent_message_queues[agent_index] = message_queue
            self._agent_action_queues[agent_index] = action_queue
            self._agent_processes[agent_index] = process

    def game_start(self,
            rng: random.Random,
            initial_state: pacai.core.gamestate.GameState,
            timeout: float,
            ) -> dict[int, pacai.core.agentaction.AgentActionRecord]:
        if (self._closed):
            raise ValueError("This isolator has already been closed.")

        results = {}
        for agent_index in self._agent_processes.keys():  # pylint: disable=consider-iterating-dictionary
            suggested_seed = rng.randint(0, 2**64)
            message = (MESSAGE_TYPE_START, (agent_index, suggested_seed, initial_state))
            results[agent_index] = self._send_agent_message(agent_index, message, timeout)

            if (results[agent_index].timeout):
                break

        return results

    def game_complete(self,
            final_state: pacai.core.gamestate.GameState,
            timeout: float,
            ) -> dict[int, pacai.core.agentaction.AgentActionRecord]:
        if (self._closed):
            return {}

        results = {}
        for agent_index in self._agent_processes.keys():  # pylint: disable=consider-iterating-dictionary
            message = (MESSAGE_TYPE_COMPLETE, final_state)
            results[agent_index] = self._send_agent_message(agent_index, message, timeout)

            if (results[agent_index].timeout):
                break

        return results

    def get_action(self,
            state: pacai.core.gamestate.GameState,
            user_inputs: list[pacai.core.action.Action],
            timeout: float,
            ) -> pacai.core.agentaction.AgentActionRecord:
        if (self._closed):
            raise ValueError("This isolator has already been closed.")

        message = (MESSAGE_TYPE_ACTION, (state, user_inputs))
        return self._send_agent_message(state.agent_index, message, timeout)

    def close(self) -> None:
        if (self._closed):
            return

        # Close all sending (message) queues.
        for queue in self._agent_message_queues.values():
            queue.close()

        # Empty all receiving (action) queues.
        for queue in self._agent_message_queues.values():
            _empty_queue(queue)

        # Join all processes.
        for process in self._agent_processes.values():
            _join_process(process)

        self._agent_message_queues.clear()
        self._agent_action_queues.clear()
        self._agent_processes.clear()

        self._closed = True

    def _send_agent_message(self,
            agent_index: int,
            message: tuple,
            raw_timeout_secs: float,
            ) -> pacai.core.agentaction.AgentActionRecord:
        """ Send an agent a message and wait for a response. """

        message_queue = self._agent_message_queues[agent_index]
        action_queue = self._agent_action_queues[agent_index]

        timeout_secs = None
        if (raw_timeout_secs > 0.0):
            timeout_secs = raw_timeout_secs

        # Send the message.
        message_queue.put(message, False)

        crashed = False
        timeout = False
        agent_action = None

        start_time = edq.util.time.Timestamp.now()

        # Receive the action.
        try:
            agent_action = action_queue.get(True, timeout_secs)
            crashed = (agent_action is None)
        except pyqueue.Empty:
            timeout = True

        end_time = edq.util.time.Timestamp.now()

        # The agent has timed out, close this isolator.
        if (timeout):
            self.close()

        return pacai.core.agentaction.AgentActionRecord(
                agent_index = agent_index,
                agent_action = agent_action,
                duration = end_time.sub(start_time),
                crashed = crashed,
                timeout = timeout)

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

        agent_method: typing.Callable[..., pacai.core.agentaction.AgentAction] | None = None
        agent_kwargs: dict[str, typing.Any] = {}

        if (message_type == MESSAGE_TYPE_START):
            (agent_index, suggested_seed, initial_state) = payload

            agent_method = agent.game_start_full
            agent_kwargs = {
                'agent_index': agent_index,
                'suggested_seed': suggested_seed,
                'initial_state': initial_state,
            }
        elif (message_type == MESSAGE_TYPE_ACTION):
            (state, user_inputs) = payload

            agent_method = agent.get_action_full
            agent_kwargs = {
                'state': state,
                'user_inputs': user_inputs,
            }
        elif (message_type == MESSAGE_TYPE_COMPLETE):
            final_state = payload

            agent_method = agent.game_complete_full
            agent_kwargs = {
                'final_state': final_state,
            }
        else:
            raise ValueError(f"Unknown message type: '{message_type}'.")

        agent_action = _call_agent_method(agent, agent_method, agent_kwargs)
        action_queue.put(agent_action, False)

        if (message_type == MESSAGE_TYPE_COMPLETE):
            break

    # Close the action queue.
    action_queue.close()

    # Empty the message queue.
    _empty_queue(message_queue)

def _empty_queue(queue: multiprocessing.Queue) -> None:
    """
    Attempt to empty out the given queue.
    Ignore anyhting that is pulled out of the queue and ignore any queue closed error.
    """

    try:
        while (not queue.empty()):
            try:
                queue.get(False)
            except ValueError:
                return
    except OSError as ex:
        # When checking if a queue is empty, we can get an error if the queue was already closed.
        if (str(ex) == 'handle is closed'):
            return

        # This was not the expected/allowed error.
        raise ex

def _get_agent_action(
        agent: pacai.core.agent.Agent,
        state: pacai.core.gamestate.GameState,
        user_inputs: list[pacai.core.action.Action],
        ) -> pacai.core.agentaction.AgentAction | None:
    """ Get action from the agent. """

    try:
        return agent.get_action_full(state, user_inputs)
    except Exception as ex:
        logging.warning("Agent '%s' (%d) crashed.", agent.name, state.agent_index, exc_info = ex)
        return None


def _call_agent_method(
        agent: pacai.core.agent.Agent,
        agent_method: typing.Callable[..., pacai.core.agentaction.AgentAction],
        agent_method_kwargs: dict[str, typing.Any],
        ) -> pacai.core.agentaction.AgentAction | None:
    """ Call a method on the agent. """

    try:
        return agent_method(**agent_method_kwargs)
    except Exception as ex:
        logging.warning("Agent '%s' crashed.", agent.name, exc_info = ex)
        return None
