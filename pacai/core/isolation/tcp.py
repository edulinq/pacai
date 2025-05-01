import pacai.core.isolation.none

# TEST
# class TCPIsolator(pacai.core.isolation.isolator.AgentIsolator):
class TCPIsolator(pacai.core.isolation.none.NoneIsolator):
    """
    An isolator that opens TCP sockets for agents to connect on.
    This requires agents to have outside orchestration for connecting to the game sever.
    This allows agents from other machines (possibly virtual) to play in this game.
    This allows for the possibility of agents being fully isolated from the game engine.
    """
