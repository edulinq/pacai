import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

class DummyAgent(pacai.core.agent.Agent):
    """
    An agent that only takes the STOP action.
    At first this may seem useless, but dummy agents can serve several purposes.
    Like being a stand-in for a future agent, fallback for a failing agent, or a placeholder when running a replay.
    """

    def get_action(self, state: pacai.core.gamestate.GameState, user_inputs: list[pacai.core.action.Action]) -> pacai.core.action.Action:
        return pacai.core.action.STOP

    def game_start(self, agent_index: int, suggested_seed: int, initial_state: pacai.core.gamestate.GameState) -> None:
        pass

    def game_complete(self, final_state: pacai.core.gamestate.GameState) -> None:
        pass
