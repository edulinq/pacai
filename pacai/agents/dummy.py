import pacai.core.action
import pacai.core.agent
import pacai.core.gamestate

class DummyAgent(pacai.core.agent.Agent):
    """
    An agent that only takes the STOP action.
    At first this may seem useless, but dummy agents can serve several purposes.
    Like being a stand-in for a future agent, fallback for a failing agent, or a placeholder when running a replay.
    """

    def get_action(self, state: pacai.core.gamestate.GameState) -> pacai.core.action.Action:
        return pacai.core.action.STOP
